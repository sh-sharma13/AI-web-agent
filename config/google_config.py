import os
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv() # Fallback to .env if yall wanna make your keys public

class GoogleConfig:
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    CALENDAR_CREDENTIALS = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
    GMAIL_CREDENTIALS = os.getenv("GOOGLE_GMAIL_CREDENTIALS")
    
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/youtube.readonly'
    ]
