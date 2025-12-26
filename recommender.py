from ai.gemini_agent import GeminiAgent
from utils.logger import get_logger
import json
from typing import List, Dict, Any

logger = get_logger(__name__)

class RecommenderSystem:
    def __init__(self):
        self.agent = GeminiAgent()

    def get_recommendations(self, user_history: List[str], current_focus: str) -> List[Dict[str, Any]]:
        context = f"History: {', '.join(user_history)}. Current: {current_focus}."
        raw_plan = self.agent.generate_study_plan(current_focus, context)
        
        try:
            js = json.loads(raw_plan)
            steps = js.get("plan", [])
        except json.JSONDecodeError:
            logger.error("Recommender JSON Parse Error")
            steps = []
        
        if not steps:
            return [{"id": 1, "title": "Review core concepts (Fallback)", "type": "reading"}]

        return [
            {
                "id": i + 1,
                "title": f"{s.get('step')} ({s.get('duration')})",
                "type": s.get("type", "suggested_action")
            }
            for i, s in enumerate(steps)
        ]
