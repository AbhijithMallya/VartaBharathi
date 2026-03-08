from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.llm import OPENAI
from src.config.mail import GMAIL

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env", env_file_encoding='utf-8',env_nested_delimiter="__", extra='ignore')
    openai: OPENAI
    gmail: GMAIL

settings = Settings() # type: ignore