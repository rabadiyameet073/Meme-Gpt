from app.core.config import settings

class CDNService:
    def get_url(self, filename: str, format_type: str = "png") -> str:
        return f"{settings.CDN_BASE_URL}/memes/{filename}.{format_type}"

cdn_service = CDNService()
