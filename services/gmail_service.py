from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from utils.logger import get_logger
import base64
import os
from email.mime.text import MIMEText
from typing import Optional, List, Dict, Any

logger = get_logger(__name__)

class GmailService:
    def __init__(self, credentials_data: Optional[Dict[str, Any]] = None):
        self.service = None
        
        if credentials_data:
            try:
                token = credentials_data.get('token')
                creds = Credentials(token=token) if token else Credentials.from_authorized_user_info(credentials_data)
                self.service = build("gmail", "v1", credentials=creds)
                logger.info("Gmail: Using Frontend Auth")
            except Exception as e:
                logger.warning(f"Frontend Auth Failed: {e}")

        if not self.service and os.path.exists("token.json"):
             try:
                from google.oauth2.credentials import Credentials as UserCredentials
                creds = UserCredentials.from_authorized_user_file("token.json")
                self.service = build("gmail", "v1", credentials=creds)
                logger.info("Gmail: Using Backend Auth")
             except Exception as e:
                 logger.error(f"Backend Auth Failed: {e}")

    def send_email(self, to_email: str, subject: str, body_text: str) -> Optional[Dict[str, Any]]:
        if not self.service: return None
        try:
            msg = MIMEText(body_text)
            msg['to'], msg['subject'] = to_email, subject
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            return self.service.users().messages().send(userId='me', body={'raw': raw}).execute()
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return None

    def list_messages(self, query: str = "is:unread", max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.service: return []
        try:
            return self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute().get('messages', [])
        except Exception as e:
            logger.error(f"Error listing emails: {e}")
            return []

    def get_message_content(self, msg_id: str) -> str:
        if not self.service: return ""
        try:
            msg = self.service.users().messages().get(userId='me', id=msg_id).execute()
            snippet = msg.get('snippet', '')
            return snippet
        except Exception as e:
            logger.error(f"Error reading email {msg_id}: {e}")
            return ""
