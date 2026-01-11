from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ghost_url: str
    ghost_api_key: str
    openai_api_key: str
    rate_limit_delay: float = 1.0
    log_level: str = "INFO"
    content_deletion_warning_threshold: float = 0.2
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
