import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    app_name: str = "Intentra"
    api_prefix: str = "/api"
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    mongo_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongo_db_name: str = os.getenv("MONGODB_DB_NAME", "intentra")
    mongo_server_selection_timeout_ms: int = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000"))
    allowed_origins: list[str] = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    force_https: bool = os.getenv("FORCE_HTTPS", "false").lower() == "true"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    def validate_runtime_configuration(self) -> None:
        if len(self.jwt_secret_key) < 32 or self.jwt_secret_key.startswith("replace_with_"):
            raise ValueError("JWT_SECRET_KEY must contain at least 32 characters")


@lru_cache
def get_settings() -> Settings:
    return Settings()
