from googleapiclient.discovery import build
from config.google_config import GoogleConfig
from utils.logger import get_logger

logger = get_logger(__name__)

class YouTubeService:
    def __init__(self):
        self.api_key = GoogleConfig.YOUTUBE_API_KEY
        if self.api_key:
            self.youtube = build("youtube", "v3", developerKey=self.api_key)
        else:
            self.youtube = None
            logger.warning("YouTube API Key not found. Running in MOCK mode.")

    def get_video_details(self, video_id):
        if not self.youtube: return {"title": f"Mock Video {video_id}", "description": "Mock Description"}
        try:
            res = self.youtube.videos().list(part="snippet", id=video_id).execute()
            if not res["items"]: return None
            s = res["items"][0]["snippet"]
            return {"title": s["title"], "channelTitle": s["channelTitle"], "description": s["description"], "tags": s.get("tags", []), "publishedAt": s["publishedAt"]}
        except Exception as e:
            logger.error(f"YouTube Details Error: {e}")
            return None

    def search_videos(self, query, max_results=5):
        if not self.youtube: 
            return [{"title": f"Mock Result: {query}", "videoId": "mock_id"}]
        try:
            res = self.youtube.search().list(part="snippet", q=query, type="video", maxResults=max_results).execute()
            return [{"title": i["snippet"]["title"], "videoId": i["id"]["videoId"], "description": i["snippet"]["description"]} for i in res.get("items", [])]
        except Exception as e:
            logger.error(f"YouTube Search Error: {e}")
            return []
