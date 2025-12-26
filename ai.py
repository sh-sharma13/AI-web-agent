from flask import Blueprint, jsonify, request
from ai.recommender import RecommenderSystem
from ai.gemini_agent import GeminiAgent
from services.calendar_service import CalendarService
from services.gmail_service import GmailService
from services.notion_service import NotionService
from utils.logger import get_logger
import json, datetime

logger = get_logger(__name__)
ai_bp = Blueprint("ai", __name__)
recommender = RecommenderSystem()
agent = GeminiAgent()

@ai_bp.route("/recommend", methods=["POST"])
def get_recommendations():
    data = request.json or {}
    return jsonify({"recommendations": recommender.get_recommendations(
        data.get("history", []), data.get("focus", "General Learning")
    )})

@ai_bp.route("/summarize", methods=["POST"])
def summarize_content():
    text = (request.json or {}).get("text")
    if not text: return jsonify({"error": "Missing text"}), 400
    return jsonify({"summary": agent.summarize_content(text)})


@ai_bp.route("/analyze_history", methods=["POST"])
def analyze_history():
    data = request.json or {}
    history = data.get("history", [])
    creds = data.get("credentials", {})
    notion_token = data.get("notion_token")
    
    gmail_context = []
    if creds.get("token"):
        g_service = GmailService(creds)
        msgs = g_service.list_messages(query="subject:(course OR learn OR study)", max_results=5)
        for m in msgs:
            gmail_context.append(g_service.get_message_content(m['id']))

    notion_context = []
    if notion_token:
        pass

    if not history and not gmail_context: return jsonify({"error": "No history or context provided"}), 400
    
    analysis_raw = agent.analyze_learning_path(history, gmail_context, notion_context)
    analysis = json.loads(analysis_raw) if isinstance(analysis_raw, str) else analysis_raw
    
    if "suggested_events" in analysis:
        c_service = CalendarService(creds)
        for ev in analysis["suggested_events"]:
            try:
                c_service.create_event(ev["summary"], ev["start_time"], ev.get("duration", 60))
                ev["status"] = "scheduled"
            except Exception as e:
                ev["status"] = "failed"

    return jsonify(analysis)


@ai_bp.route("/agent_action", methods=["POST"])
def agent_action():
    data = request.json or {}
    command = data.get("command")
    if not command: return jsonify({"error": "Missing command"}), 400

    today = data.get("current_date", "2025-12-16")
    
    prompt = f"""
    You're a helpful Assistant. Figure out what the user wants from: "{command}".
    
    Tools you can use:
    - SCHEDULE_EVENT (summary, start_time iso)
    - SEND_EMAIL (to_email, subject, body)
    - SUMMARIZE (content)
    - CREATE_NOTION_NOTE (title, content)
    
    Context: {data.get("context", "")}. Date: {today}.
    
    Return JSON: {{ "tool": "NAME", "parameters": {{...}}, "explanation": "reason" }}
    """
    
    try:
        raw = agent.model.generate_content(prompt).text
        plan = json.loads(raw.split("```json")[-1].split("```")[0].strip() if "```" in raw else raw)
        
        tool, params, creds = plan.get("tool"), plan.get("parameters", {}), data.get("credentials")
        notion_token = data.get("notion_token") 
        
        result = None

        if tool == "SCHEDULE_EVENT" and creds:
             res = CalendarService(creds).create_event(params.get("summary"), params.get("start_time"))
             result = f"Error: {res['error']}" if res and "error" in res else (f"Event created: {res.get('htmlLink')}" if res else "Failed.")
             
        elif tool == "SEND_EMAIL" and creds:
             res = GmailService(creds).send_email(params.get("to_email"), params.get("subject", "BlueLays Agent"), params.get("body", ""))
             result = "Email sent!" if res else "Email failed."
             
        elif tool == "CALCULATOR":
            result = "Calculator isn't built yet, sorry!"

        elif tool == "SUMMARIZE":
            result = agent.summarize_content(params.get("content", command))
            
        elif tool == "CREATE_NOTION_NOTE":
             n_service = NotionService(notion_token) if notion_token else NotionService() 
             url = n_service.create_page(params.get("title", "Study Note"), params.get("content", ""))
             
             if url:
                 result = f"Saved to Notion! {url}"
             else:
                 result = "Couldn't save to Notion. Check your connection?"

        return jsonify({"status": "success", "action": plan, "execution_result": result})

    except Exception as e:
        logger.error(f"Agent Error: {e}")
        return jsonify({"error": "Processing failed", "details": str(e)}), 500
