from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./ma_advisory.db"
    storage_dir: str = "./storage"
    cors_origins: str = "*"
    share_token_ttl_days: int = 14
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60
    webhook_secret: str = "change-me"
    bootstrap_token: str = "change-me"


settings = Settings()
