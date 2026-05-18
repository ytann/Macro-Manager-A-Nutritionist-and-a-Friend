import requests
import time
import json

API_URL = "http://localhost:8000"

def test():
    # 1. Log meal: 1 bowl of daal khichdi for breakfast
    print("Logging meal...")
    payload = {
        "text": "1 bowl of daal khichdi",
        "meal_type": "breakfast",
        "environment": "home",
        "is_voice": False
    }
    r = requests.post(f"{API_URL}/log/start", json=payload)
    r.raise_for_status()
    meal_id = r.json()["meal_id"]
    print(f"Meal ID: {meal_id}")

    # 2. Wait for resolution
    while True:
        res = requests.get(f"{API_URL}/log/status/{meal_id}").json()
        if res["status"] == "completed":
            break
        print("Waiting for resolution...")
        time.sleep(2)
    print("Meal resolved.")

    # 3. Get current state (summary)
    summary = requests.get(f"{API_URL}/summary").json()
    consumed = summary["daily"]["consumed"]
    goals = summary["daily"]["goals"]
    
    remaining = {
        "protein": max(0.0, goals["protein"] - consumed["protein"]),
        "carbs": max(0.0, goals["carbs"] - consumed["carbs"]),
        "fat": max(0.0, goals["fat"] - consumed["fat"]),
        "calories": max(0.0, goals["calories"] - consumed["calories"]),
    }

    # 4. Ask copilot for lunch
    print("Asking copilot...")
    planner_payload = {
        "user_query": "what can I get for lunch",
        "remaining_macros": remaining,
        "goals": goals,
        "consumed_macros": consumed,
        "meal_type": "lunch",
        "memory_context": ""
    }
    r = requests.post(f"{API_URL}/planner", json=planner_payload)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    test()
