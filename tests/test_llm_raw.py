import asyncio
import json
from app.core.llm import safe_acompletion
from app.core.config import Config

async def test():
    prompt = """
    You are MacroManager's Clinical Copilot.
    EXACT BUDGET FOR THIS MEAL: {"protein": 20, "carbs": 50, "fat": 10, "calories": 350}
    User Query: "What should I eat for lunch?"
    Format: Clean Markdown.
    """
    print("Sending request to LLM...")
    try:
        resp = await safe_acompletion(
            model=Config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            api_base=Config.LITELLM_API_BASE,
            temperature=0.2
        )
        print("--- RAW RESPONSE ---")
        print(resp.choices[0].message.content)
        print("--- END RESPONSE ---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
