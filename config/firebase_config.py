import firebase_admin
from firebase_admin import credentials, firestore
import os, json, base64
from dotenv import load_dotenv
load_dotenv()

class MockFirestoreClient:
    def collection(self, name):
        return self

    def document(self, name):
        return self

    def add(self, data):
        print(f"[MOCK] Added to Firestore: {data}")
        return None

    def update(self, data):
        print(f"[MOCK] Updated Firestore: {data}")
        return None


def init_firebase():
    if firebase_admin._apps:
        return firestore.client()

    # encoded_key = os.environ.get("FIREBASE_KEY")
    # if encoded_key:
    #     try:
    #         decoded_json = base64.b64decode(encoded_key).decode("utf-8")
    #         firebase_dict = json.loads(decoded_json)

    #         cred = credentials.Certificate(firebase_dict)
    #         firebase_admin.initialize_app(cred)
    #         print("Firebase initialized using ENV variable (base64 decoded)")
    #         return firestore.client()

    #     except Exception as e:
    #         print("Failed to load Firebase from ENV variable:", e)
    #         print("Trying local file fallback...")

    if os.path.exists("serviceAccountKey.json"):
        try:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
            print("Firebase initialized using local JSON file")
            return firestore.client()
        except Exception as e:
            print("Error loading local serviceAccountKey.json:", e)

    print("No Firebase credentials found. Running in MOCK mode.")
    return MockFirestoreClient()
