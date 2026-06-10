"""Configuration settings for Axiom using Pydantic Settings."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenRouter API
    openrouter_api_key: str = Field(..., description="OpenRouter API key")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL"
    )
    default_model: str = Field(
        default="openrouter/openai/gpt-oss-120b:free",
        description="Default LLM model to use"
    )

    # Tool timeouts
    nmap_timeout: int = Field(default=120, description="Nmap scan timeout in seconds")
    general_tool_timeout: int = Field(default=60, description="General tool timeout in seconds")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()