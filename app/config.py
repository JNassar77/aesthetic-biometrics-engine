from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_key: str = ""
    n8n_webhook_url: str = ""
    allowed_origins: str = "http://localhost:3000"
    max_image_size_mb: int = 10
    min_face_confidence: float = 0.7

    model_config = {"env_file": ".env"}


settings = Settings()
