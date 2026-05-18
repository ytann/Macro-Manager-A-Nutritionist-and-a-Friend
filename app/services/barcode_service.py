import httpx
from typing import Dict, Optional
import base64
import json
from app.core.logger import logger
from app.services.database import DatabaseManager
from app.core import queries
from app.utils.nutrition import normalize_to_100g
from barcode_decoder import decode_barcode_async
from app.services.foodbank import FoodbankService
from app.core.llm import safe_acompletion
from app.core.config import Config
from app.schemas.food_schemas import LabelExtraction
import asyncio

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("easyocr not installed. Label OCR text extraction will be skipped.")

class BarcodeService:
    def __init__(self, db: DatabaseManager, foodbank: FoodbankService):
        self.db = db
        self.foodbank = foodbank
        self._reader = None

    @property
    def reader(self):
        if self._reader is None and EASYOCR_AVAILABLE:
            self._reader = easyocr.Reader(['en'], gpu=False)
        return self._reader

    async def process_barcode(self, base64_image: str) -> Optional[Dict]:
        barcode_info = await decode_barcode_async(base64_image)
        if not barcode_info:
            return None
        barcode_data = barcode_info['data']

        # 1. Local DB
        row = self.db.run_foodbank(queries.FOODS_SEARCH_BY_BARCODE, (barcode_data,), fetchone=True)
        if row:
            logger.info(f"Barcode {barcode_data} found in local DB.")
            return dict(row)

        # 2. OpenFoodFacts
        logger.info(f"Barcode {barcode_data} not in DB. Querying OpenFoodFacts...")
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode_data}.json", timeout=5.0)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get('status') == 1:
                        product = data['product']
                        nutriments = product.get('nutriments', {})
                        name = product.get('product_name', f"Product {barcode_data}")
                        serving_size = float(product.get('serving_quantity') or 100)
                        
                        # Use 100g data if available, otherwise normalize
                        if 'energy-kcal_100g' in nutriments:
                            cal = float(nutriments.get('energy-kcal_100g') or 0)
                            p = float(nutriments.get('proteins_100g') or 0)
                            c = float(nutriments.get('carbohydrates_100g') or 0)
                            f = float(nutriments.get('fat_100g') or 0)
                        elif 'energy-kcal_serving' in nutriments and serving_size > 0:
                            cal = normalize_to_100g(nutriments.get('energy-kcal_serving') or 0, serving_size)
                            p = normalize_to_100g(nutriments.get('proteins_serving') or 0, serving_size)
                            c = normalize_to_100g(nutriments.get('carbohydrates_serving') or 0, serving_size)
                            f = normalize_to_100g(nutriments.get('fat_serving') or 0, serving_size)
                        else:
                            cal, p, c, f = 0.0, 0.0, 0.0, 0.0

                        logger.info(f"Found {name} on OpenFoodFacts.")
                        self.db.run_foodbank(queries.FOODS_UPSERT_BARCODE, (barcode_data, name, name.lower(), barcode_data, cal, p, c, f, 0, 0, 0, 0, 0, 1, 'openfoodfacts'), commit=True)
                        return {'name': name, 'calories': cal, 'protein': p, 'carbs': c, 'fat': f, 'verified': 1}
            except Exception as e:
                logger.error(f"OpenFoodFacts API failed: {e}")

        # 3. Tavily -> LLM (Sync Queue) via FoodbankService
        logger.info(f"Querying Tavily for barcode {barcode_data}")
        query = f"barcode {barcode_data} nutrition facts"
        product_info = await self.foodbank.get_nutrition_data(query)
        
        if product_info:
            name = product_info.get('name', f"Scanned Item {barcode_data}")
            self.db.run_foodbank(queries.FOODS_UPSERT_BARCODE, (barcode_data, name, name.lower(), barcode_data, product_info['calories'], product_info['protein'], product_info['carbs'], product_info['fat'], 0, 0, 0, 0, 0, 0, 'tavily_llm'), commit=True)
            product_info['verified'] = 0
            product_info['name'] = name
            return product_info
        
        return None

    async def process_label(self, base64_image: str) -> Optional[Dict]:
        image_bytes = base64.b64decode(base64_image)
        text_extracted = ""
        if EASYOCR_AVAILABLE and self.reader:
            try:
                # Run easyocr in a thread to avoid blocking the event loop
                results = await asyncio.to_thread(self.reader.readtext, image_bytes)
                text_extracted = " ".join([text for _, text, _ in results])
                logger.info(f"EasyOCR extracted text: {text_extracted[:100]}...")
            except Exception as e:
                logger.error(f"EasyOCR failed: {e}")

        prompt = f"""
        Extract nutritional information from this product label image.

        If OCR text is provided, use it as a secondary hint to resolve ambiguities, but prioritize the visual information from the image.

        Extracted OCR text: {text_extracted if text_extracted.strip() else "None provided."}

        Return the results in a JSON object following this schema:
        {{
          "name": "string",
          "serving_size": float,
          "calories": float,
          "protein": float,
          "carbs": float,
          "fat": float
        }}

        If a value is not found, set it to 0. If serving size is not found or ambiguous, assume 100.
        """
        try:
            resp = await safe_acompletion(
                model=Config.LLM_MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                response_format={"type": "json_object"},
                api_base=Config.LITELLM_API_BASE,
                temperature=0.0
            )
            
            # Use Pydantic for robust parsing
            data_dict = json.loads(resp.choices[0].message.content)
            data = LabelExtraction.model_validate(data_dict)
            
            serving_size = data.serving_size
            
            cal = normalize_to_100g(data.calories, serving_size)
            p = normalize_to_100g(data.protein, serving_size)
            c = normalize_to_100g(data.carbs, serving_size)
            f = normalize_to_100g(data.fat, serving_size)
            
            # Since OCR + LLM is used, verified = 1 as per constraints: "All data from DB, OpenFoodFacts, and OCR will be marked verified = 1."
            name = data.name if data.name.strip() else "Scanned Label Product"
            self.db.run_foodbank(queries.FOODS_UPSERT_BARCODE, (None, name, name.lower(), None, cal, p, c, f, 0, 0, 0, 0, 0, 1, 'ocr'), commit=True)
            
            return {'name': name, 'calories': cal, 'protein': p, 'carbs': c, 'fat': f, 'verified': 1}
        except Exception as e:
            logger.error(f"Vision parsing failed: {e}")
            return None
