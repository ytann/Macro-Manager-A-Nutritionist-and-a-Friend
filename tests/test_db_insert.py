import asyncio
from app.services.database import DatabaseManager
from app.services.foodbank import FoodbankService
from app.services.barcode_service import BarcodeService

async def main():
    db = DatabaseManager()
    fb = FoodbankService(db)
    barcode_service = BarcodeService(db, fb)
    
    name = "Test Label Item"
    cal, p, c, f = 100, 10, 5, 2
    
    try:
        from app.core import queries
        db.run_foodbank(queries.FOODS_UPSERT_BARCODE, (None, name, name.lower(), None, cal, p, c, f, 0, 0, 0, 0, 0, 1, 'ocr'), commit=True)
        print("SUCCESS! Inserted perfectly.")
    except Exception as e:
        print(f"FAILED: {e}")

asyncio.run(main())
