from flask import Blueprint, jsonify

udemy_bp = Blueprint("udemy", __name__)

@udemy_bp.route("/status", methods=["GET"])
def udemy_status():
    return jsonify({"status": "Udemy tracker ready"}), 200
