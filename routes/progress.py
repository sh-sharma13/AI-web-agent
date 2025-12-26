from flask import Blueprint, request, jsonify
from config.firebase_config import init_firebase
from firebase_admin import firestore
from utils.logger import get_logger

progress_bp = Blueprint("progress", __name__)
db = init_firebase()
logger = get_logger(__name__) 

@progress_bp.route("/", methods=["POST"])
def update_progress():
    try:
        data = request.json
        user_id = data["user_id"]
        course = data["course"]
        platform = data.get("platform", "custom")
        progress = data["progress"]

        logger.info(f"Updating progress for user={user_id}, course={course}, progress={progress}")

        db.collection("users").document(user_id).collection("progress").add({
            "course": course,
            "platform": platform,
            "progress": progress
        })

        # db.collection("users").document(user_id).update({
        #     "progress": progress,
        #     "last_updated": firestore.SERVER_TIMESTAMP,
        #     "updated_by": "BlueLays"
        # })

        logger.info("Progress updated successfully")
        return jsonify({"message": "Progress updated"}), 200

    except Exception as e:
        logger.error(f"Error updating progress: {str(e)}")
        return jsonify({"error": str(e)}), 500
