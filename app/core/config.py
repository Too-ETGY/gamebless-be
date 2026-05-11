from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Gamebless API"
    DEBUG: bool = False

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()