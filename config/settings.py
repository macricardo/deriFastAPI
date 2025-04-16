#Environment Variables
import os
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # SECRET_KEY
    # SECRET_KEY: str = os.getenv("SECRET_KEY")
    # APP_ENV: str = os.getenv("APP_ENV", "development")

    # PostgreSQL Settings
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "")

    @property
    def DATABASE_URL(self) -> str:
        """Dynamically generate DATABASE_URL"""
        encoded_user = urllib.parse.quote_plus(self.POSTGRES_USER)
        encoded_password = urllib.parse.quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql://{encoded_user}:{encoded_password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


# Instantiate settings
settings = Settings()