from flask import Blueprint, jsonify, request
from services.notion_service import NotionService
from utils.logger import get_logger

logger = get_logger(__name__)
notion_bp = Blueprint("notion", __name__)

@notion_bp.route("/create_page", methods=["POST"])
def create_page():
    try:
        data = request.json or {}
        token = data.get("token") 
        database_id = data.get("database_id")
        title = data.get("title")
        properties = data.get("properties")

        if not database_id or not title:
             return jsonify({"error": "Missing database_id or title"}), 400

        service = NotionService(token) 
        result = service.create_page(database_id, title, properties)
        
        if result:
            return jsonify({"status": "created", "page": result}), 200
        else:
             return jsonify({"error": "Failed to create Notion page"}), 500

    except Exception as e:
        logger.error(f"Notion Create Error: {e}")
        return jsonify({"error": str(e)}), 500
