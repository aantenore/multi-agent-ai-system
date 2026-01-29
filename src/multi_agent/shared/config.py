"""
Centralized configuration for the multi-agent system.

Uses pydantic-settings to load from .env and environment variables.
"""

from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    GEMINI = "gemini"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM Configuration
    llm_provider: LLMProvider = Field(
        default=LLMProvider.GEMINI,
        description="LLM provider to use (gemini, ollama, openai, anthropic)",
    )
    llm_model: str = Field(
        default="gemini-2.5-flash-lite", description="Model name to use"
    )

    # Google Gemini settings
    google_api_key: str = Field(default="", description="Google API key for Gemini")

    # Ollama settings
    ollama_host: str = Field(
        default="http://localhost:11434", description="Ollama server URL"
    )

    # OpenAI settings
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API base URL (for Azure or others)",
    )

    # Anthropic settings
    anthropic_api_key: str = Field(default="", description="Anthropic API key")

    # Agent settings
    agent_temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Temperature for generation"
    )
    agent_max_tokens: int = Field(default=4096, description="Max tokens per response")

    # Memory settings
    memory_max_messages: int = Field(
        default=20, description="Max messages in conversational memory"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    @property
    def project_root(self) -> Path:
        """Project root directory."""
        return Path(__file__).parent.parent.parent.parent


@lru_cache
def get_settings() -> Settings:
    """Singleton for settings."""
    return Settings()


# Global instance
settings = get_settings()
