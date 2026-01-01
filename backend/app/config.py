"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: str = ""
    
    # Logging
    log_level: str = "INFO"
    
    # Debug mode
    debug: bool = True
    
    # CORS
    cors_origins: str = "*"
    
    # Database
    database_url: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="",  # No prefix, use exact env var names
    )
    
    def __init__(self, **kwargs):
        """Initialize settings and create database directory."""
        super().__init__(**kwargs)
        
        # Set database URL if not provided
        # Use ./db/db_query.db relative to backend directory
        if not self.database_url:
            # Get the backend directory (parent of app directory)
            backend_dir = Path(__file__).parent.parent
            db_dir = backend_dir / "db"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "db_query.db"
            self.database_url = f"sqlite+aiosqlite:///{db_path.absolute()}"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()

