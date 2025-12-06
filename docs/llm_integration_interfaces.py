"""
LLM統合のPythonインターフェース定義

このファイルは、LLM統合設計書の実装サンプルとして提供されます。
実際の実装は src/llm/ ディレクトリ配下に配置してください。

ファイル構成:
    src/llm/
    ├── __init__.py
    ├── base.py            # BaseLLMProvider, LLMConfig, LLMMessage, LLMResponse
    ├── ollama.py          # OllamaProvider
    ├── openrouter.py      # OpenRouterProvider
    ├── factory.py         # LLMProviderFactory
    ├── prompt.py          # SYSTEM_PROMPT, FEW_SHOT_EXAMPLES, build_prompt
    ├── parser.py          # extract_sql, clean_sql
    ├── validator.py       # validate_sql, add_safety_limits
    └── error_handler.py   # QueryError, handle_query_error
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum


# =============================================================================
# Base Interfaces
# =============================================================================

class LLMProviderType(Enum):
    """LLM provider types."""
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    LLAMA_CPP = "llama_cpp"


@dataclass
class LLMMessage:
    """LLM message format.

    Attributes:
        role: Message role ("system", "user", "assistant")
        content: Message content
    """
    role: str
    content: str


@dataclass
class LLMResponse:
    """LLM response format.

    Attributes:
        content: Generated text content
        model: Model name used for generation
        tokens_used: Number of tokens used (optional)
        finish_reason: Reason for completion (optional)
        raw_response: Raw API response (optional)
    """
    content: str
    model: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class LLMConfig:
    """LLM configuration.

    Attributes:
        provider: Provider type (ollama, openrouter, etc.)
        model: Model name
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
        base_url: API base URL (optional)
        api_key: API key for authentication (optional)
        extra_params: Additional provider-specific parameters (optional)
    """
    provider: LLMProviderType
    model: str
    temperature: float = 0.1
    max_tokens: int = 1000
    timeout: int = 30
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    extra_params: Optional[Dict[str, Any]] = None


class LLMError(Exception):
    """LLM operation error."""
    pass


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.

    All LLM providers must implement this interface to ensure
    consistent behavior across different backends.

    Examples:
        >>> config = LLMConfig(
        ...     provider=LLMProviderType.OLLAMA,
        ...     model="codellama:13b-instruct"
        ... )
        >>> provider = OllamaProvider(config)
        >>> response = provider.generate([
        ...     LLMMessage(role="user", content="Generate SQL...")
        ... ])
    """

    def __init__(self, config: LLMConfig):
        """Initialize LLM provider.

        Args:
            config: LLM configuration
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider-specific configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        pass

    @abstractmethod
    def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Generate response from messages.

        Args:
            messages: List of conversation messages
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse object

        Raises:
            LLMError: If generation fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and ready.

        Returns:
            True if provider is available, False otherwise
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models.

        Returns:
            List of model names
        """
        pass

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__} model={self.config.model}>"


# =============================================================================
# Ollama Provider Interface
# =============================================================================

class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider.

    Supports running local models via Ollama API.
    Default endpoint: http://localhost:11434

    Recommended models for SQL generation:
    - codellama:13b-instruct
    - deepseek-coder:6.7b-instruct
    - sqlcoder:15b
    - mistral:7b-instruct-v0.2

    Examples:
        >>> config = LLMConfig(
        ...     provider=LLMProviderType.OLLAMA,
        ...     model="codellama:13b-instruct",
        ...     base_url="http://localhost:11434"
        ... )
        >>> provider = OllamaProvider(config)
        >>> response = provider.generate([
        ...     LLMMessage(role="user", content="Generate SQL...")
        ... ])
    """

    def __init__(self, config: LLMConfig):
        """Initialize Ollama provider."""
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
        self.api_url = f"{self.base_url}/api/chat"

    def _validate_config(self) -> None:
        """Validate Ollama configuration."""
        if not self.config.model:
            raise ValueError("Model name is required for Ollama")

    def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Generate response using Ollama API.

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters (stream, format, etc.)

        Returns:
            LLMResponse object

        Raises:
            LLMError: If generation fails
        """
        # Implementation in src/llm/ollama.py
        raise NotImplementedError

    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        # Implementation in src/llm/ollama.py
        raise NotImplementedError

    def list_models(self) -> List[str]:
        """List available Ollama models."""
        # Implementation in src/llm/ollama.py
        raise NotImplementedError


# =============================================================================
# OpenRouter Provider Interface
# =============================================================================

class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter API provider.

    Provides access to multiple commercial LLMs via unified API.
    Requires API key from https://openrouter.ai

    Recommended models for SQL generation (cost-effective):
    - google/gemini-pro-1.5 ($0.50/1M tokens)
    - anthropic/claude-3-haiku ($0.25/1M tokens)
    - meta-llama/llama-3-70b-instruct ($0.90/1M tokens)
    - deepseek/deepseek-coder-33b-instruct ($0.14/1M tokens)

    Examples:
        >>> config = LLMConfig(
        ...     provider=LLMProviderType.OPENROUTER,
        ...     model="google/gemini-pro-1.5",
        ...     api_key="sk-or-..."
        ... )
        >>> provider = OpenRouterProvider(config)
        >>> response = provider.generate([
        ...     LLMMessage(role="user", content="Generate SQL...")
        ... ])
    """

    def __init__(self, config: LLMConfig):
        """Initialize OpenRouter provider."""
        super().__init__(config)
        self.base_url = config.base_url or "https://openrouter.ai/api/v1"
        self.api_url = f"{self.base_url}/chat/completions"

    def _validate_config(self) -> None:
        """Validate OpenRouter configuration."""
        if not self.config.model:
            raise ValueError("Model name is required for OpenRouter")
        if not self.config.api_key:
            raise ValueError(
                "API key is required for OpenRouter. "
                "Get one at https://openrouter.ai/keys"
            )

    def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Generate response using OpenRouter API.

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters

        Returns:
            LLMResponse object

        Raises:
            LLMError: If generation fails
        """
        # Implementation in src/llm/openrouter.py
        raise NotImplementedError

    def is_available(self) -> bool:
        """Check if OpenRouter API is available."""
        # Implementation in src/llm/openrouter.py
        raise NotImplementedError

    def list_models(self) -> List[str]:
        """List available OpenRouter models."""
        # Implementation in src/llm/openrouter.py
        raise NotImplementedError


# =============================================================================
# Factory Interface
# =============================================================================

class LLMProviderFactory:
    """Factory for creating LLM providers.

    Examples:
        >>> config = LLMConfig(
        ...     provider=LLMProviderType.OLLAMA,
        ...     model="codellama:13b-instruct"
        ... )
        >>> provider = LLMProviderFactory.create(config)

        >>> # From config dict
        >>> provider = LLMProviderFactory.from_dict({
        ...     "provider": "ollama",
        ...     "model": "codellama:13b-instruct"
        ... })
    """

    _providers = {
        LLMProviderType.OLLAMA: OllamaProvider,
        LLMProviderType.OPENROUTER: OpenRouterProvider,
    }

    @classmethod
    def create(cls, config: LLMConfig) -> BaseLLMProvider:
        """Create LLM provider from config.

        Args:
            config: LLM configuration

        Returns:
            LLM provider instance

        Raises:
            LLMError: If provider type is not supported
        """
        # Implementation in src/llm/factory.py
        raise NotImplementedError

    @classmethod
    def from_dict(cls, config_dict: dict) -> BaseLLMProvider:
        """Create LLM provider from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            LLM provider instance

        Raises:
            LLMError: If configuration is invalid
        """
        # Implementation in src/llm/factory.py
        raise NotImplementedError

    @classmethod
    def register_provider(
        cls,
        provider_type: LLMProviderType,
        provider_class: type
    ) -> None:
        """Register custom LLM provider.

        Args:
            provider_type: Provider type enum
            provider_class: Provider class (must inherit from BaseLLMProvider)
        """
        # Implementation in src/llm/factory.py
        raise NotImplementedError


# =============================================================================
# Prompt Engineering
# =============================================================================

SYSTEM_PROMPT = """あなたは競馬データベース専門のSQLアシスタントです。
ユーザーの自然言語クエリを正確なSQLクエリに変換してください。

[スキーマ情報、ルール、出力形式は docs/llm_integration_design.md を参照]
"""


FEW_SHOT_EXAMPLES = [
    {
        "query": "2024年のGⅠレースを全て表示して",
        "sql": "SELECT * FROM NL_RA WHERE 開催年月日 >= 20240101 AND グレード = 'A'"
    },
    # More examples...
]


def build_prompt(user_query: str, include_examples: bool = True) -> str:
    """Build complete prompt for Text-to-SQL.

    Args:
        user_query: User's natural language query
        include_examples: Whether to include few-shot examples

    Returns:
        Complete prompt string
    """
    # Implementation in src/llm/prompt.py
    raise NotImplementedError


# =============================================================================
# SQL Parsing
# =============================================================================

def extract_sql(llm_response: str) -> Optional[str]:
    """Extract SQL query from LLM response.

    Handles various formats:
    - ```sql ... ```
    - ```SQL ... ```
    - SELECT ... (直接SQL)
    - 説明文 + SQL

    Args:
        llm_response: Raw LLM response text

    Returns:
        Extracted SQL query, or None if not found

    Examples:
        >>> extract_sql("```sql\\nSELECT * FROM NL_RA\\n```")
        'SELECT * FROM NL_RA'
    """
    # Implementation in src/llm/parser.py
    raise NotImplementedError


def clean_sql(sql: str) -> str:
    """Clean and normalize SQL query.

    Args:
        sql: Raw SQL query

    Returns:
        Cleaned SQL query
    """
    # Implementation in src/llm/parser.py
    raise NotImplementedError


# =============================================================================
# SQL Validation
# =============================================================================

class SQLValidationError(Exception):
    """SQL validation error."""
    pass


def validate_sql(sql: str, strict: bool = True) -> tuple[bool, Optional[str]]:
    """Validate SQL query for safety and correctness.

    Args:
        sql: SQL query to validate
        strict: If True, apply strict validation rules

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_sql("SELECT * FROM NL_RA")
        (True, None)

        >>> validate_sql("DROP TABLE NL_RA")
        (False, "Dangerous SQL operation detected: DROP")
    """
    # Implementation in src/llm/validator.py
    raise NotImplementedError


def add_safety_limits(sql: str, max_rows: int = 1000) -> str:
    """Add safety LIMIT clause if not present.

    Args:
        sql: SQL query
        max_rows: Maximum rows to return

    Returns:
        SQL query with LIMIT clause
    """
    # Implementation in src/llm/validator.py
    raise NotImplementedError


# =============================================================================
# Error Handling
# =============================================================================

class QueryError(Exception):
    """Query processing error.

    Attributes:
        message: Error message
        error_type: Type of error (llm_error, sql_error, validation_error, etc.)
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        error_type: str = "unknown",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize query error."""
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}


def handle_query_error(error: Exception, user_query: str) -> str:
    """Handle query error and generate user-friendly message.

    Args:
        error: The exception that occurred
        user_query: Original user query

    Returns:
        User-friendly error message
    """
    # Implementation in src/llm/error_handler.py
    raise NotImplementedError


# =============================================================================
# Usage Example
# =============================================================================

def example_usage():
    """Example usage of LLM integration."""

    # 1. Initialize LLM provider
    config = LLMConfig(
        provider=LLMProviderType.OLLAMA,
        model="codellama:13b-instruct",
        temperature=0.1
    )
    llm = LLMProviderFactory.create(config)

    # 2. Build prompt
    user_query = "2024年のGⅠレースを全て表示して"
    prompt = build_prompt(user_query)
    messages = [LLMMessage(role="user", content=prompt)]

    # 3. Generate SQL
    response = llm.generate(messages)

    # 4. Extract and clean SQL
    sql = extract_sql(response.content)
    sql = clean_sql(sql)

    # 5. Validate SQL
    is_valid, error = validate_sql(sql, strict=True)
    if not is_valid:
        raise SQLValidationError(error)

    # 6. Add safety limits
    sql = add_safety_limits(sql, max_rows=1000)

    # 7. Execute (using existing database handler)
    from src.database.sqlite_handler import SQLiteDatabase
    database = SQLiteDatabase({"path": "data/keiba.db"})

    with database:
        results = database.fetch_all(sql)

    return results


if __name__ == "__main__":
    print(__doc__)
    print("\nThis file contains interface definitions for LLM integration.")
    print("Actual implementation should be placed in src/llm/ directory.")
