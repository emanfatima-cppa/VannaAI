from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # DB
    db_connection_string: str
    azure_sql_connection_string: str
    rms_connection_string: str
    postgres_connection_string: str
    pop_connection_string: str = "oracle+oracledb://username:password@hostname:1521/?service_name=orcl"

    # Auth
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # OpenAI
    openai_api_key: str

    # Vanna / Chroma
    chroma_persist_dir: str = "./chroma_db"

    # CORS
    frontend_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://192.168.11.232:5173",
        "http://192.168.11.232:5174",
        "http://192.168.11.232:5175",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()