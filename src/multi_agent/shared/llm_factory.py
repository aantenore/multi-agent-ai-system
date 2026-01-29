"""
Factory for creating LLM clients.

Supports transparent switching between local (Ollama) and remote (OpenAI, Anthropic, Gemini) models.
This is the fundamental pattern for abstracting providers.
"""

from enum import Enum
from typing import Any

from langchain_core.language_models import BaseChatModel
from loguru import logger

from multi_agent.shared.config import settings, LLMProvider


class LLMType(str, Enum):
    """LLM type for specific use cases."""

    GENERAL = "general"  # General tasks
    CODING = "coding"  # Code generation
    REASONING = "reasoning"  # Complex reasoning


# Recommended models per type
# Flash = faster, cheaper, good for general tasks
# Pro = more capable, better for coding and complex reasoning
RECOMMENDED_MODELS = {
    LLMProvider.GEMINI: {
        LLMType.GENERAL: "gemini-2.5-flash-lite",
        LLMType.CODING: "gemini-3-pro-preview",
        LLMType.REASONING: "gemini-3-pro-preview",
    },
    LLMProvider.OLLAMA: {
        LLMType.GENERAL: "mistral",
        LLMType.CODING: "qwen2.5-coder",
        LLMType.REASONING: "lfm2.5-thinking:1.2b",
    },
    LLMProvider.OPENAI: {
        LLMType.GENERAL: "gpt-4o-mini",
        LLMType.CODING: "gpt-4o",
        LLMType.REASONING: "gpt-4o",
    },
}


def create_llm(
    provider: LLMProvider | None = None,
    model: str | None = None,
    llm_type: LLMType = LLMType.GENERAL,
    **kwargs: Any,
) -> BaseChatModel:
    """
    Create an LLM instance based on configuration.

    Args:
        provider: Provider to use (default: from settings)
        model: Specific model (default: from settings or recommended)
        llm_type: Task type for automatic model selection
        **kwargs: Additional parameters for the provider

    Returns:
        BaseChatModel instance ready to use

    Example:
        >>> llm = create_llm()  # Uses settings
        >>> llm = create_llm(provider=LLMProvider.GEMINI, model="gemini-3-pro-preview")
        >>> llm = create_llm(llm_type=LLMType.CODING)  # Chooses model for coding
    """
    # Determine provider and model
    provider = provider or settings.llm_provider

    if model is None:
        # Use model from settings or recommended for the type
        model = settings.llm_model or RECOMMENDED_MODELS.get(provider, {}).get(llm_type)

    logger.info(f"Creating LLM: provider={provider.value}, model={model}")

    # Common parameters
    common_params = {
        "temperature": kwargs.pop("temperature", settings.agent_temperature),
        "max_tokens": kwargs.pop("max_tokens", settings.agent_max_tokens),
    }

    if provider == LLMProvider.GEMINI:
        return _create_gemini_llm(model, common_params, **kwargs)
    elif provider == LLMProvider.OLLAMA:
        return _create_ollama_llm(model, common_params, **kwargs)
    elif provider == LLMProvider.OPENAI:
        return _create_openai_llm(model, common_params, **kwargs)
    elif provider == LLMProvider.ANTHROPIC:
        return _create_anthropic_llm(model, common_params, **kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _create_gemini_llm(model: str, params: dict, **kwargs) -> BaseChatModel:
    """Create Google Gemini LLM."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY not configured in .env")

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=settings.google_api_key,
        temperature=params["temperature"],
        max_output_tokens=params["max_tokens"],
        **kwargs,
    )


def _create_ollama_llm(model: str, params: dict, **kwargs) -> BaseChatModel:
    """Create Ollama LLM (local)."""
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=model,
        base_url=settings.ollama_host,
        temperature=params["temperature"],
        num_predict=params["max_tokens"],
        **kwargs,
    )


def _create_openai_llm(model: str, params: dict, **kwargs) -> BaseChatModel:
    """Create OpenAI LLM (remote)."""
    from langchain_openai import ChatOpenAI

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY not configured in .env")

    return ChatOpenAI(
        model=model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=params["temperature"],
        max_tokens=params["max_tokens"],
        **kwargs,
    )


def _create_anthropic_llm(model: str, params: dict, **kwargs) -> BaseChatModel:
    """Create Anthropic LLM (remote)."""
    from langchain_anthropic import ChatAnthropic

    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY not configured in .env")

    return ChatAnthropic(
        model=model,
        api_key=settings.anthropic_api_key,
        temperature=params["temperature"],
        max_tokens=params["max_tokens"],
        **kwargs,
    )


def list_available_models(provider: LLMProvider | None = None) -> list[str]:
    """
    List available models for a provider.

    For Ollama, queries the local server.
    For others, returns a static list.
    """
    provider = provider or settings.llm_provider

    if provider == LLMProvider.GEMINI:
        return [
            "gemini-3-pro-preview",
            "gemini-3-flash-preview",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-thinking-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]

    elif provider == LLMProvider.OLLAMA:
        try:
            import httpx

            response = httpx.get(f"{settings.ollama_host}/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m["name"] for m in models]
        except Exception as e:
            logger.warning(f"Unable to list Ollama models: {e}")
        return []

    elif provider == LLMProvider.OPENAI:
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]

    elif provider == LLMProvider.ANTHROPIC:
        return ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]

    return []
