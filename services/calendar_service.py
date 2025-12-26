from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from utils.logger import get_logger
import datetime
import os

logger = get_logger(__name__)

class CalendarService:
    def __init__(self, credentials_data=None):
        self.service = None
        
        if credentials_data:
            try:
                token = credentials_data.get('token')
                creds = Credentials(token=token) if token else Credentials.from_authorized_user_info(credentials_data)
                self.service = build("calendar", "v3", credentials=creds)
                logger.info("Calendar: Using Frontend Auth")
            except Exception as e:
                logger.warning(f"Frontend Auth Failed: {e}")

        if not self.service and os.path.exists("token.json"):
            try:
                from google.oauth2.credentials import Credentials as UserCredentials
                creds = UserCredentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/calendar"])
                self.service = build("calendar", "v3", credentials=creds)
                logger.info("Calendar: Using Backend Auth")
            except Exception as e:
                logger.error(f"Backend Auth Failed: {e}")

    def create_event(self, summary, start_time_iso, duration_minutes=30, description=None):
        if not self.service: return {"error": "Auth missing"}

        try:
            start_dt = datetime.datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
            end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)

            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'UTC',
                },
            }

            created_event = self.service.events().insert(calendarId='primary', body=event).execute()
            return created_event
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            return {"error": str(e)}

    def list_upcoming_events(self, max_results=10):
        if not self.service:
             return []
        
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId='primary', timeMin=now,
                maxResults=max_results, singleEvents=True,
                orderBy='startTime').execute()
            return events_result.get('items', [])
        except Exception as e:
            logger.error(f"Error listing events: {e}")
            return []
