import requests
import json

API_URL = "http://localhost:8000"

def test():
    print("Testing planner simple request...")
    planner_payload = {
        "user_query": "What should I eat for lunch?",
        "remaining_macros": {"protein": 50, "carbs": 100, "fat": 30, "calories": 600},
        "goals": {"protein": 140, "carbs": 200, "fat": 65, "calories": 1800},
        "consumed_macros": {"protein": 90, "carbs": 100, "fat": 35, "calories": 1200},
        "meal_type": "lunch",
        "memory_context": ""
    }
    try:
        r = requests.post(f"{API_URL}/planner", json=planner_payload, timeout=120)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
