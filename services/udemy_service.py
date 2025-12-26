from utils.logger import get_logger

logger = get_logger(__name__)

class UdemyService:
    def __init__(self): pass

    def get_course_details(self, course_id):
        return {"title": "Mock Udemy Course", "url": f"https://www.udemy.com/course/{course_id}/"}

    def process_progress(self, user_id, course_data, progress_percent):
        logger.info(f"Udemy progress {user_id}: {progress_percent}%")
        return True
