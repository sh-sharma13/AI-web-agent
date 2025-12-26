from flask import Blueprint, jsonify, request
from services.youtube_service import YouTubeService
from utils.logger import get_logger

logger = get_logger(__name__)
youtube_bp = Blueprint("youtube", __name__)
youtube_service = YouTubeService()

@youtube_bp.route("/details", methods=["GET"])
def get_video_details():
    video_id = request.args.get("videoId")
    if not video_id:
        return jsonify({"error": "Missing videoId parameter"}), 400
    
    details = youtube_service.get_video_details(video_id)
    if details:
        return jsonify(details), 200
    else:
        return jsonify({"error": "Video not found or API error"}), 404

@youtube_bp.route("/search", methods=["GET"])
def search_videos():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Missing q (query) parameter"}), 400

    results = youtube_service.search_videos(query)
    return jsonify({"items": results}), 200
