from flask import Blueprint, jsonify, request
from services.gmail_service import GmailService
from utils.logger import get_logger

logger = get_logger(__name__)
gmail_bp = Blueprint("gmail", __name__)

@gmail_bp.route("/send", methods=["POST"])
def send_email():
    try:
        data = request.json or {}
        creds_data = data.get("credentials")
        to_email = data.get("to")
        subject = data.get("subject", "BlueLays Study Reminder")
        body = data.get("body", "Time to study!")

        if not to_email:
            return jsonify({"error": "Missing 'to' email address"}), 400

        service = GmailService(creds_data) 
        result = service.send_email(to_email, subject, body)
        
        if result:
            return jsonify({"status": "sent", "result": result}), 200
        else:
            return jsonify({"error": "Failed to send email"}), 500
            
    except Exception as e:
        logger.error(f"Gmail Send Error: {e}")
        return jsonify({"error": str(e)}), 500

@gmail_bp.route("/list", methods=["POST"])
def list_emails():
    try:
        data = request.json or {}
        creds_data = data.get("credentials")
        query = data.get("query", "is:unread")
        max_results = data.get("max_results", 5)
        
        service = GmailService(creds_data)
        messages = service.list_messages(query, max_results)
        return jsonify({"messages": messages}), 200
        
    except Exception as e:
        logger.error(f"Gmail List Error: {e}")
        return jsonify({"error": str(e)}), 500
