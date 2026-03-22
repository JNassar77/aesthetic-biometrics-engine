from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_key: str = ""
    n8n_webhook_url: str = ""
    allowed_origins: str = "http://localhost:3000"
    max_image_size_mb: int = 10
    min_face_confidence: float = 0.7
    api_keys: str = ""  # Comma-separated API keys; empty = dev mode (no auth)
    rate_limit_rpm: int = 60  # Requests per minute per IP; 0 = disabled

    model_config = {"env_file": ".env"}


settings = Settings()
