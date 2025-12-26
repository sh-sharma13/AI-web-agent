import google.generativeai as genai
from config.google_config import GoogleConfig
from utils.logger import get_logger
import datetime
import json
import time
from typing import Optional, Dict, Any, List

logger = get_logger(__name__)

class GeminiAgent:
    def __init__(self):
        self.api_key = GoogleConfig.GEMINI_API_KEY
        self.model = None
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.3})
        else:
            logger.warning("Gemini API Key missing - Agent will vary")

    def _clean_json(self, text: str) -> str:
        if "```" in text:
            text = text.split("```")[-2]
            if text.startswith("json"):
                text = text[4:]
        return text.strip()

    def _generate_with_retry(self, prompt: str, retries: int = 2) -> Dict[str, Any]:
        if not self.model: return {}

        for i in range(retries + 1):
            try:
                response = self.model.generate_content(prompt)
                clean_text = self._clean_json(response.text)
                return json.loads(clean_text)
            except json.JSONDecodeError:
                if i == retries:
                     logger.error("Giving up on JSON parsing.")
            except Exception as e:
                logger.error(f"Gemini API Error: {e}")
                if i == retries: break
                time.sleep(1) 
        
        return {} 

    def generate_study_plan(self, topic: str, user_context: str = "") -> str:
        prompt = f"""
        Act as a super friendly Tutor. Topic: '{topic}'. Context: {user_context}.
        Create a 3-5 step plan. Keep it actionable.
        Return JSON: {{ "plan": [ {{ "step": "desc", "duration": "time", "type": "video|reading|practice" }} ] }} 
        """
        res = self._generate_with_retry(prompt)
        return json.dumps(res) if res else '{"plan": []}'

    def summarize_content(self, text: str) -> str:
        if not self.model: return "Simulated Summary."
        try:
            return self.model.generate_content(f"Give me 3 punchy bullet points to summarize this:\n{text[:3000]}").text
        except Exception as e:
            logger.error(f"Summary failed: {e}")
            return "Couldn't summarize right now."

    def analyze_learning_path(self, history_data: List[Dict], gmail_context: List[str] = [], notion_context: List[str] = []) -> Dict[str, Any]:
        if not self.model: return {}
        
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        
        prompt = f"""
        Role: Your friendly Study Buddy & Scheduler.
        Goal: Look at what I've been doing and help me plan my day for TOMORROW ({tomorrow}).
        
        My Data:
        - Recent History: {str(history_data[:60])}
        - Email Updates: {str(gmail_context[:3])}
        - Notes: {str(notion_context[:2])}
        
        Tasks:
        1. Group my history into "Topics" (e.g. Python, History).
        2. Guess my progress % based on video titles.
        3. Suggest 1-2 study sessions for tomorrow (Use my history timestamps to guess when I like to study).
        
        Output JSON:
        {{
            "dashboard_stats": [ 
                {{ 
                    "topic": "Name", 
                    "progress": 0-100, 
                    "recent_resource": "Video Title",
                    "url": "Link",
                    "next_step": "What should I do next?"
                }} 
            ],
            "suggested_events": [ 
                {{ 
                    "summary": "Study [Topic]: [Action]", 
                    "start_time": "{tomorrow}T18:00:00", 
                    "duration": 60 
                }} 
            ]
        }}
        """
        
        return self._generate_with_retry(prompt)
