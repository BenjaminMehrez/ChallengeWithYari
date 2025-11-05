from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
  # App
  APP_NAME: str = "FastAPI  Clean Architecture"
  APP_VERSION: str = "1.0.0"
  DEBUG: bool = False

  # Database
  DATABASE_URL: str
  DATABASE_TEST_URL: str
  
  # Security
  SECRET_KEY: str
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

  API_POKEMON: str

  model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings():
  return Settings()