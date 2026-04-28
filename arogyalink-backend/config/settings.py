from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Gemma
    gemma_api_key: str
    gemma_model: str = "gemma-2-27b-it"
    gemma_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"

    # Google
    google_maps_api_key: str = "placeholder"
    google_application_credentials: str = ""

    # Firebase
    firebase_database_url: str
    firebase_project_id: str

    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str

    # App
    port: int = 8080
    env: str = "development"
    app_base_url: str = "https://YOUR_CLOUD_RUN_URL"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
