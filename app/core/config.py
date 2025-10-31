from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
  # App
  APP_NAME: str = "FastAPI  Clean Architecture"
  APP_VERSION: str = "1.0.0"
  DEBUG: bool = False

  # Database
  DATABASE_URL: str = 'sqlite:///./test.db' 

  # Security
  SECRET_KEY: str
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

  API_POKEMON: str


  class Config:
    env_file = ".env"
    case_sensitive = False


@lru_cache()
def get_settings():
  return Settings()