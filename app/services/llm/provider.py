from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import get_settings
from app.models.schemas import LLMProvider


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def get_model(self, temperature: float = 0.7, **kwargs) -> BaseChatModel:
        """Get the LLM model instance."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured."""
        pass


def _is_real_key(key: Optional[str]) -> bool:
    """Check if an API key looks like a real key, not a placeholder."""
    if not key:
        return False
    placeholder_prefixes = ("your_", "sk-placeholder", "change-", "xxx", "TODO")
    if any(key.lower().startswith(p.lower()) for p in placeholder_prefixes):
        return False
    if key in ("", "none", "null", "undefined"):
        return False
    # Real keys are typically 20+ characters
    return len(key) >= 20


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(self):
        self.settings = get_settings()

    def get_model(
        self,
        temperature: float = 0.7,
        model_name: Optional[str] = None,
        **kwargs
    ) -> BaseChatModel:
        """Get Claude model instance."""
        if not self.is_available():
            raise ValueError(
                "Anthropic API key is not configured. "
                "Set a valid ANTHROPIC_API_KEY in your .env file."
            )
        return ChatAnthropic(
            anthropic_api_key=self.settings.ANTHROPIC_API_KEY,
            model=model_name or self.settings.ANTHROPIC_MODEL,
            temperature=temperature,
            **kwargs
        )

    def is_available(self) -> bool:
        """Check if Anthropic API key is configured with a real key."""
        return _is_real_key(self.settings.ANTHROPIC_API_KEY)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider."""

    def __init__(self):
        self.settings = get_settings()

    def get_model(
        self,
        temperature: float = 0.7,
        model_name: Optional[str] = None,
        **kwargs
    ) -> BaseChatModel:
        """Get Gemini model instance."""
        if not self.is_available():
            raise ValueError(
                "Google API key is not configured. "
                "Set a valid GOOGLE_API_KEY in your .env file."
            )
        return ChatGoogleGenerativeAI(
            google_api_key=self.settings.GOOGLE_API_KEY,
            model=model_name or self.settings.GEMINI_MODEL,
            temperature=temperature,
            **kwargs
        )

    def is_available(self) -> bool:
        """Check if Google API key is configured with a real key."""
        return _is_real_key(self.settings.GOOGLE_API_KEY)


class LLMFactory:
    """Factory for creating LLM instances."""

    _providers: Dict[LLMProvider, BaseLLMProvider] = {
        LLMProvider.CLAUDE: ClaudeProvider(),
        LLMProvider.GEMINI: GeminiProvider(),
    }

    @classmethod
    def get_provider(cls, provider: Optional[LLMProvider] = None) -> BaseLLMProvider:
        """
        Get LLM provider instance.

        Args:
            provider: Specific provider to use. If None, uses default from settings.

        Returns:
            BaseLLMProvider instance.

        Raises:
            ValueError: If provider is not supported or not configured.
        """
        settings = get_settings()

        if provider is None:
            provider = LLMProvider(settings.DEFAULT_LLM_PROVIDER)

        if provider not in cls._providers:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        llm_provider = cls._providers[provider]

        if not llm_provider.is_available():
            raise ValueError(
                f"LLM provider {provider} is not configured. "
                f"Please set the required API key in environment variables."
            )

        return llm_provider

    @classmethod
    def get_model(
        cls,
        provider: Optional[LLMProvider] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> BaseChatModel:
        """
        Get LLM model instance.

        Args:
            provider: Specific provider to use.
            temperature: Model temperature (0-1).
            **kwargs: Additional model parameters.

        Returns:
            BaseChatModel instance ready to use.
        """
        llm_provider = cls.get_provider(provider)
        return llm_provider.get_model(temperature=temperature, **kwargs)

    @classmethod
    def list_available_providers(cls) -> List[LLMProvider]:
        """Get list of currently available (configured) providers."""
        return [
            provider
            for provider, instance in cls._providers.items()
            if instance.is_available()
        ]
