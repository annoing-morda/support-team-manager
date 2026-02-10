"""Application configuration using pydantic-settings."""

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram
    bot_token: str = Field(..., description="Telegram Bot API token")

    # Database
    database_url: PostgresDsn = Field(
        ..., description="PostgreSQL connection URL (async driver)"
    )

    # Admin configuration
    admin_ids: str = Field(
        ..., description="Comma-separated list of Telegram user IDs with admin rights"
    )

    # Scheduler configuration
    reminder_hour: int = Field(9, description="Hour for daily duty reminder (0-23)")
    reminder_minute: int = Field(0, description="Minute for daily duty reminder (0-59)")
    tz: str = Field("Europe/Moscow", description="Timezone for scheduler")

    # Logging
    log_level: str = Field("INFO", description="Logging level")

    @property
    def admin_ids_list(self) -> list[int]:
        """Parse admin IDs from comma-separated string."""
        return [int(id_.strip()) for id_ in self.admin_ids.split(",") if id_.strip()]

    @property
    def database_url_str(self) -> str:
        """Get database URL as string."""
        return str(self.database_url)


# Global settings instance
settings = Settings()
