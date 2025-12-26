from flask import Flask, jsonify
from flask_cors import CORS
from config.firebase_config import init_firebase
from routes import register_blueprints
from utils.logger import get_logger
import os

logger = get_logger(__name__)

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")
    app.config['JSON_SORT_KEYS'] = False
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    init_firebase()
    
    register_blueprints(app)
    
    @app.route("/health")
    @app.route("/")
    def health_check():
        return jsonify({
            "status": "success",
            "service": "BlueLays API",
            "version": "1.0.0"
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal Server Error: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled Exception: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

    logger.info("BlueLays Backend Initialized 🚀")
    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
