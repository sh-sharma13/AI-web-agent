import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_youtube():
    print("\n--- Testing YouTube Search ---")
    try:
        response = requests.get(f"{BASE_URL}/youtube/search", params={"q": "Python for experts"})
        if response.status_code == 200:
            items = response.json().get("items", [])
            print(f"✅ Success! Found {len(items)} videos.")
            for item in items[:2]:
                print(f"   - {item['title']} ({item['videoId']})")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_ai_recommend():
    print("\n--- Testing AI Recommendations ---")
    payload = {
        "history": ["Python Basics", "Flask Intro"],
        "focus": "Advanced API Design"
    }
    try:
        response = requests.post(f"{BASE_URL}/ai/recommend", json=payload)
        if response.status_code == 200:
            recs = response.json().get("recommendations", [])
            print(f"✅ Success! AI suggested:")
            for rec in recs:
                print(f"   - {rec['title']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Waiting for server to be ready (ensure 'python app.py' is running)...")
    time.sleep(1) 
    test_youtube()
    test_ai_recommend()
