from flask import Blueprint, jsonify, request
from services.calendar_service import CalendarService
from utils.logger import get_logger

logger = get_logger(__name__)
calendar_bp = Blueprint("calendar", __name__)

@calendar_bp.route("/create", methods=["POST"])
def create_event():
    try:
        creds_data = request.json.get("credentials")
        event_data = request.json.get("event", {})
        
        service = CalendarService(creds_data) 
        
        summary = event_data.get("summary", "Study Session")
        start_time = event_data.get("start", {}).get("dateTime") 
        
        if not start_time:
             return jsonify({"error": "Missing start time"}), 400

        result = service.create_event(summary, start_time)
        
        if result:
            return jsonify({"eventId": result.get("id"), "status": "created"}), 200
        else:
            return jsonify({"error": "Failed to create event"}), 500

    except Exception as e:
        logger.error(f"Route error: {e}")
        return jsonify({"error": str(e)}), 500
