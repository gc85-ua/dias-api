from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

env_path = BASE_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path if env_path.exists() else None, env_file_encoding="utf-8", extra="ignore")
    cache_db_host: str = 'localhost' # redis/valkey host
    cache_db_port: int = 6379 # redis/valkey port
    cache_db: int = 0 # redis/valkey database number

settings = Settings()