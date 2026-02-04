from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "POS Backend"
    JWT_SECRET_KEY: str = "CHANGEME-USE-ENV"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "pos"

    model_config = ConfigDict(env_file=".env")


settings = Settings()
