"""
Configuration settings for EPİAŞ Energy Analysis application
"""
import os
from datetime import timedelta
from typing import Optional
from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Configuration
    EPIAS_API_BASE_URL: str = Field(
        default="https://seffaflik.epias.com.tr/electricity-service/v1",
        env="EPIAS_API_BASE_URL"
    )
    EPIAS_AUTH_URL: str = Field(
        default="https://giris.epias.com.tr",
        env="EPIAS_AUTH_URL"
    )
    EPIAS_AUTH_TEST_URL: str = Field(
        default="https://giris-prp.epias.com.tr",
        env="EPIAS_AUTH_TEST_URL"
    )

    # Credentials
    EPIAS_USERNAME: str = Field("pure.transparency.test@gmail.com", env="EPIAS_USERNAME")
    EPIAS_PASSWORD: str = Field("Power.2025@", env="EPIAS_PASSWORD")

    # Environment
    ENVIRONMENT: str = Field(default="production", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # API Settings
    API_TIMEOUT: int = Field(default=30, env="API_TIMEOUT")
    API_MAX_RETRIES: int = Field(default=3, env="API_MAX_RETRIES")
    API_RETRY_DELAY: int = Field(default=1, env="API_RETRY_DELAY")

    # TGT Settings
    TGT_VALIDITY_HOURS: int = Field(default=2, env="TGT_VALIDITY_HOURS")
    TGT_REFRESH_MARGIN_MINUTES: int = Field(
        default=10,
        env="TGT_REFRESH_MARGIN_MINUTES"
    )

    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=100, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(default=1000, env="MAX_PAGE_SIZE")

    # Date formats
    DATE_FORMAT: str = "%Y-%m-%d"
    DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S%z"

    # Streamlit
    STREAMLIT_WIDE_MODE: bool = Field(default=True, env="STREAMLIT_WIDE_MODE")
    STREAMLIT_THEME: str = Field(default="light", env="STREAMLIT_THEME")

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        allowed = ["production", "test", "development"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    @property
    def auth_url(self) -> str:
        """Get the appropriate auth URL based on environment"""
        if self.ENVIRONMENT == "test":
            return self.EPIAS_AUTH_TEST_URL
        return self.EPIAS_AUTH_URL

    @property
    def tgt_validity_timedelta(self) -> timedelta:
        """Get TGT validity as timedelta"""
        return timedelta(hours=self.TGT_VALIDITY_HOURS)

    @property
    def tgt_refresh_margin(self) -> timedelta:
        """Get TGT refresh margin as timedelta"""
        return timedelta(minutes=self.TGT_REFRESH_MARGIN_MINUTES)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()