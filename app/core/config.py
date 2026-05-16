from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "GameBless Be"
    DEBUG: bool = False

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"

    # Gemini
    GEMINI_API_KEY: str

    # ChromaDB — path on disk where vectors are stored
    CHROMA_DB_PATH: str = "./chroma_db"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()