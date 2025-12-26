from flask import Blueprint
from .progress import progress_bp
from .ai import ai_bp
from .calendar_sync import calendar_bp
from .gmail_sync import gmail_bp
from .notion_sync import notion_bp
from .udemy_tracker import udemy_bp
from .youtube_tracker import youtube_bp

def register_blueprints(app):
    app.register_blueprint(progress_bp, url_prefix="/progress")
    app.register_blueprint(ai_bp, url_prefix="/ai")
    app.register_blueprint(calendar_bp, url_prefix="/calendar")
    app.register_blueprint(gmail_bp, url_prefix="/gmail")
    app.register_blueprint(notion_bp, url_prefix="/notion")
    app.register_blueprint(udemy_bp, url_prefix="/udemy")
    app.register_blueprint(youtube_bp, url_prefix="/youtube")
