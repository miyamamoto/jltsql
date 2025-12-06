# LLM統合設計書 - 競馬データ分析アプリ

## 概要

本設計書は、JRVLTSQLアプリケーションへのLLM（Large Language Model）統合の詳細設計を定義します。Text-to-SQL機能により、自然言語クエリから競馬データベースへのSQLクエリを生成します。

### 設計目標

- ローカルLLM（Ollama、llama.cpp）とOpenRouter APIの両方をサポート
- プロバイダーを簡単に切り替え可能な抽象化層
- 競馬ドメインに特化したText-to-SQLプロンプト設計
- 高精度なSQL生成とバリデーション

---

## 1. アーキテクチャ概要

```
┌─────────────────────────────────────────────────────┐
│                   CLI Interface                      │
│              (jltsql query "...")                    │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│              Query Handler                           │
│  - 自然言語クエリの受付                              │
│  - レスポンス整形・表示                              │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│           LLM Provider Factory                       │
│  - プロバイダー選択・初期化                          │
│  - 設定管理                                          │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────────┐   ┌──────────────────┐
│  Ollama Provider │   │ OpenRouter       │
│  (ローカル)       │   │ Provider (API)   │
└────────┬─────────┘   └────────┬─────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
┌─────────────────────────────────────────────────────┐
│            Prompt Engineering                        │
│  - システムプロンプト                                │
│  - スキーマ情報の埋め込み                            │
│  - Few-shot examples                                 │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│           Response Processing                        │
│  - SQL抽出パーサー                                   │
│  - バリデーション                                    │
│  - エラーハンドリング                                │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│           Database Execution                         │
│  - SQLクエリ実行                                     │
│  - 結果の取得・整形                                  │
└─────────────────────────────────────────────────────┘
```

---

## 2. LLMプロバイダー抽象化設計

### 2.1 共通インターフェース定義

```python
"""LLM provider abstraction for JRVLTSQL."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum


class LLMProviderType(Enum):
    """LLM provider types."""
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    LLAMA_CPP = "llama_cpp"


@dataclass
class LLMMessage:
    """LLM message format."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """LLM response format."""
    content: str
    model: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: LLMProviderType
    model: str
    temperature: float = 0.1  # Low temperature for deterministic SQL
    max_tokens: int = 1000
    timeout: int = 30
    # Provider-specific settings
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    extra_params: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.

    All LLM providers must implement this interface to ensure
    consistent behavior across different backends.
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


class LLMError(Exception):
    """LLM operation error."""
    pass
```

### 2.2 Ollama実装

```python
"""Ollama provider implementation."""

import requests
from typing import List, Optional
from src.llm.base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMError,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


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
        logger.info(
            "Ollama provider initialized",
            model=config.model,
            base_url=self.base_url
        )

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
        try:
            # Convert messages to Ollama format
            ollama_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # Prepare request payload
            payload = {
                "model": self.config.model,
                "messages": ollama_messages,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                }
            }

            # Add extra parameters
            if self.config.extra_params:
                payload["options"].update(self.config.extra_params)

            # Make API request
            logger.debug("Sending request to Ollama", model=self.config.model)
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()

            # Parse response
            result = response.json()

            return LLMResponse(
                content=result["message"]["content"],
                model=self.config.model,
                tokens_used=result.get("eval_count"),
                finish_reason=result.get("done_reason"),
                raw_response=result
            )

        except requests.exceptions.Timeout:
            raise LLMError(f"Ollama request timed out after {self.config.timeout}s")
        except requests.exceptions.ConnectionError:
            raise LLMError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Is Ollama running? (ollama serve)"
            )
        except requests.exceptions.RequestException as e:
            raise LLMError(f"Ollama API error: {e}")
        except (KeyError, ValueError) as e:
            raise LLMError(f"Invalid Ollama response format: {e}")

    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            # Check if Ollama is running
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()

            # Check if model is pulled
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]

            return self.config.model in model_names

        except Exception as e:
            logger.warning(f"Ollama availability check failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()

            models = response.json().get("models", [])
            return [m["name"] for m in models]

        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []
```

### 2.3 OpenRouter実装

```python
"""OpenRouter provider implementation."""

import requests
from typing import List
from src.llm.base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMError,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


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
        logger.info(
            "OpenRouter provider initialized",
            model=config.model
        )

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
        try:
            # Convert messages to OpenAI format
            api_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # Prepare request payload
            payload = {
                "model": self.config.model,
                "messages": api_messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
            }

            # Add extra parameters
            if self.config.extra_params:
                payload.update(self.config.extra_params)

            # Prepare headers
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/miyamamoto/jrvltsql",
                "X-Title": "JRVLTSQL"
            }

            # Make API request
            logger.debug("Sending request to OpenRouter", model=self.config.model)
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.config.timeout
            )
            response.raise_for_status()

            # Parse response
            result = response.json()
            choice = result["choices"][0]

            return LLMResponse(
                content=choice["message"]["content"],
                model=result.get("model", self.config.model),
                tokens_used=result.get("usage", {}).get("total_tokens"),
                finish_reason=choice.get("finish_reason"),
                raw_response=result
            )

        except requests.exceptions.Timeout:
            raise LLMError(f"OpenRouter request timed out after {self.config.timeout}s")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise LLMError("Invalid OpenRouter API key")
            elif e.response.status_code == 429:
                raise LLMError("OpenRouter rate limit exceeded")
            else:
                raise LLMError(f"OpenRouter API error: {e}")
        except requests.exceptions.RequestException as e:
            raise LLMError(f"OpenRouter request failed: {e}")
        except (KeyError, ValueError) as e:
            raise LLMError(f"Invalid OpenRouter response format: {e}")

    def is_available(self) -> bool:
        """Check if OpenRouter API is available."""
        try:
            # Test with a simple request
            response = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                timeout=5
            )
            return response.status_code == 200

        except Exception as e:
            logger.warning(f"OpenRouter availability check failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """List available OpenRouter models."""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                timeout=10
            )
            response.raise_for_status()

            models = response.json().get("data", [])
            return [m["id"] for m in models]

        except Exception as e:
            logger.error(f"Failed to list OpenRouter models: {e}")
            return []
```

### 2.4 プロバイダーファクトリー

```python
"""LLM provider factory."""

from typing import Optional
from src.llm.base import BaseLLMProvider, LLMConfig, LLMProviderType, LLMError
from src.llm.ollama import OllamaProvider
from src.llm.openrouter import OpenRouterProvider
from src.utils.logger import get_logger

logger = get_logger(__name__)


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
        provider_class = cls._providers.get(config.provider)

        if not provider_class:
            supported = ", ".join([p.value for p in cls._providers.keys()])
            raise LLMError(
                f"Unsupported provider: {config.provider}. "
                f"Supported providers: {supported}"
            )

        logger.info(
            "Creating LLM provider",
            provider=config.provider.value,
            model=config.model
        )

        return provider_class(config)

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
        try:
            # Parse provider type
            provider_str = config_dict.get("provider", "ollama")
            provider_type = LLMProviderType(provider_str)

            # Create config
            config = LLMConfig(
                provider=provider_type,
                model=config_dict["model"],
                temperature=config_dict.get("temperature", 0.1),
                max_tokens=config_dict.get("max_tokens", 1000),
                timeout=config_dict.get("timeout", 30),
                base_url=config_dict.get("base_url"),
                api_key=config_dict.get("api_key"),
                extra_params=config_dict.get("extra_params")
            )

            return cls.create(config)

        except KeyError as e:
            raise LLMError(f"Missing required config key: {e}")
        except ValueError as e:
            raise LLMError(f"Invalid config value: {e}")

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
        if not issubclass(provider_class, BaseLLMProvider):
            raise ValueError(
                f"{provider_class} must inherit from BaseLLMProvider"
            )

        cls._providers[provider_type] = provider_class
        logger.info(
            "Registered custom LLM provider",
            provider_type=provider_type.value,
            provider_class=provider_class.__name__
        )
```

---

## 3. プロンプトエンジニアリング

### 3.1 システムプロンプト設計

```python
"""Prompt templates for Text-to-SQL."""


SYSTEM_PROMPT = """あなたは競馬データベース専門のSQLアシスタントです。
ユーザーの自然言語クエリを正確なSQLクエリに変換してください。

## データベーススキーマ

### 主要テーブル

**NL_RA (レース情報)**
- 開催年月日 (INTEGER, YYYYMMDD形式)
- 競馬場コード (TEXT, 01=札幌, 02=函館, 03=福島, 04=新潟, 05=東京, 06=中山, 07=中京, 08=京都, 09=阪神, 10=小倉)
- レース番号 (INTEGER, 1-12)
- レース名 (TEXT)
- グレード (TEXT, A=GⅠ, B=GⅡ, C=GⅢ, D=Listed, 空白=平場)
- 距離 (INTEGER, メートル単位)
- トラック種別 (TEXT, 1=芝, 2=ダート, 3=障害芝, 4=障害ダート)
- 馬場状態 (TEXT, 1=良, 2=稍重, 3=重, 4=不良)
- 天候 (TEXT, 1=晴, 2=曇, 3=雨, 4=小雨, 5=雪, 6=小雪)
- レース条件_記号 (TEXT, 500万下、1000万下、1600万下等)

**NL_SE (出馬表/成績)**
- 開催年月日 (INTEGER, YYYYMMDD形式)
- 競馬場コード (TEXT)
- レース番号 (INTEGER)
- 馬番 (INTEGER)
- 血統登録番号 (TEXT, 馬の一意識別子)
- 馬名 (TEXT)
- 性別コード (TEXT, 1=牡, 2=牝, 3=セン)
- 馬齢 (INTEGER)
- 騎手コード (TEXT)
- 斤量 (REAL, kg)
- 着順 (INTEGER)
- タイム (TEXT, M:SS.S形式)
- 単勝人気順 (INTEGER)
- 単勝オッズ (REAL)
- 通過順位 (TEXT, コーナーごとの順位)

**NL_HR (払戻情報)**
- 開催年月日 (INTEGER)
- 競馬場コード (TEXT)
- レース番号 (INTEGER)
- 単勝_馬番 (INTEGER)
- 単勝_払戻金 (INTEGER, 100円あたり)
- 複勝_馬番_1〜5 (INTEGER)
- 複勝_払戻金_1〜5 (INTEGER)
- 馬連_馬番 (TEXT, "01-02"形式)
- 馬連_払戠金 (INTEGER)
- ワイド_馬番_1〜7 (TEXT)
- ワイド_払戻金_1〜7 (INTEGER)
- 馬単_馬番 (TEXT, "01-02"形式)
- 馬単_払戻金 (INTEGER)
- 3連複_馬番 (TEXT, "01-02-03"形式)
- 3連複_払戻金 (INTEGER)
- 3連単_馬番 (TEXT, "01-02-03"形式)
- 3連単_払戻金 (INTEGER)

**NL_UM (馬マスタ)**
- 血統登録番号 (TEXT, PRIMARY KEY)
- 馬名 (TEXT)
- 性別コード (TEXT)
- 毛色コード (TEXT)
- 生年月日 (INTEGER, YYYYMMDD形式)
- 父馬_血統登録番号 (TEXT)
- 母馬_血統登録番号 (TEXT)
- 生産者コード (TEXT)
- 馬主コード (TEXT)

**NL_KS (騎手マスタ)**
- 騎手コード (TEXT, PRIMARY KEY)
- 騎手名 (TEXT)
- 騎手名カナ (TEXT)
- 所属場コード (TEXT, 1=美浦, 2=栗東)

**NL_CH (調教師マスタ)**
- 調教師コード (TEXT, PRIMARY KEY)
- 調教師名 (TEXT)
- 調教師名カナ (TEXT)
- 所属場コード (TEXT, 1=美浦, 2=栗東)

**NL_JG (重賞情報)**
- 開催年月日 (INTEGER)
- 競馬場コード (TEXT)
- レース番号 (INTEGER)
- 重賞回次 (INTEGER, 第○回)
- 重賞名_正式 (TEXT)
- グレード (TEXT)
- ハンデ区分 (TEXT)

### SQLルール

1. **日付形式**: YYYYMMDD形式の整数 (例: 20240101)
2. **競馬場コード**: 2桁のゼロパディング文字列 (例: '05'=東京)
3. **JOIN推奨**:
   - レース詳細が必要なら NL_RA と NL_SE を開催年月日, 競馬場コード, レース番号で結合
   - 馬情報が必要なら NL_SE と NL_UM を血統登録番号で結合
   - 払戻情報が必要なら NL_HR を結合
4. **着順フィルタ**: 着順 = 1 で1着馬のみ
5. **グレードフィルタ**: グレード = 'A' でGⅠレースのみ
6. **距離範囲**: 1000〜3600 (1000m〜3600m)
7. **NULL処理**: 未確定データは NULL

## 出力形式

SQLクエリのみを出力してください。説明は不要です。
```sql
SELECT ...
```

## 重要な注意事項

- SQLiteを使用しているため、SQLite標準の関数を使用してください
- 日付の比較は整数として行ってください (例: 開催年月日 >= 20240101)
- LIMIT句を適切に使用して、結果を制限してください
- コメントは含めないでください
"""


FEW_SHOT_EXAMPLES = [
    {
        "query": "2024年のGⅠレースを全て表示して",
        "sql": """SELECT
    NL_RA.開催年月日,
    NL_RA.競馬場コード,
    NL_RA.レース番号,
    NL_RA.レース名,
    NL_RA.グレード,
    NL_RA.距離
FROM NL_RA
WHERE NL_RA.開催年月日 >= 20240101
  AND NL_RA.開催年月日 < 20250101
  AND NL_RA.グレード = 'A'
ORDER BY NL_RA.開催年月日, NL_RA.レース番号;"""
    },
    {
        "query": "直近10レースの単勝1番人気の勝率を計算して",
        "sql": """SELECT
    COUNT(*) as 総レース数,
    SUM(CASE WHEN 着順 = 1 THEN 1 ELSE 0 END) as 勝利数,
    ROUND(100.0 * SUM(CASE WHEN 着順 = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as 勝率
FROM NL_SE
WHERE 単勝人気順 = 1
  AND 着順 IS NOT NULL
ORDER BY 開催年月日 DESC, レース番号 DESC
LIMIT 10;"""
    },
    {
        "query": "東京競馬場の芝2000mで行われたレースの平均タイムは?",
        "sql": """SELECT
    AVG(CAST(SUBSTR(NL_SE.タイム, 1, 1) AS INTEGER) * 60 +
        CAST(SUBSTR(NL_SE.タイム, 3, 2) AS REAL) +
        CAST(SUBSTR(NL_SE.タイム, 6, 1) AS REAL) / 10) as 平均タイム秒
FROM NL_SE
JOIN NL_RA ON
    NL_SE.開催年月日 = NL_RA.開催年月日 AND
    NL_SE.競馬場コード = NL_RA.競馬場コード AND
    NL_SE.レース番号 = NL_RA.レース番号
WHERE NL_RA.競馬場コード = '05'
  AND NL_RA.距離 = 2000
  AND NL_RA.トラック種別 = '1'
  AND NL_SE.着順 = 1
  AND NL_SE.タイム IS NOT NULL;"""
    },
    {
        "query": "武豊騎手の2023年の勝利数と勝率を教えて",
        "sql": """SELECT
    COUNT(*) as 騎乗数,
    SUM(CASE WHEN 着順 = 1 THEN 1 ELSE 0 END) as 勝利数,
    ROUND(100.0 * SUM(CASE WHEN 着順 = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as 勝率
FROM NL_SE
JOIN NL_KS ON NL_SE.騎手コード = NL_KS.騎手コード
WHERE NL_KS.騎手名 LIKE '%武豊%'
  AND NL_SE.開催年月日 >= 20230101
  AND NL_SE.開催年月日 < 20240101
  AND NL_SE.着順 IS NOT NULL;"""
    },
    {
        "query": "3連単の最高配当トップ10を表示して",
        "sql": """SELECT
    NL_HR.開催年月日,
    NL_HR.競馬場コード,
    NL_HR.レース番号,
    NL_RA.レース名,
    NL_HR.3連単_馬番,
    NL_HR.3連単_払戻金
FROM NL_HR
JOIN NL_RA ON
    NL_HR.開催年月日 = NL_RA.開催年月日 AND
    NL_HR.競馬場コード = NL_RA.競馬場コード AND
    NL_HR.レース番号 = NL_RA.レース番号
WHERE NL_HR.3連単_払戻金 IS NOT NULL
ORDER BY NL_HR.3連単_払戻金 DESC
LIMIT 10;"""
    },
    {
        "query": "ディープインパクト産駒のGⅠ勝利数は?",
        "sql": """SELECT
    COUNT(*) as GⅠ勝利数,
    COUNT(DISTINCT NL_SE.血統登録番号) as 勝利馬数
FROM NL_SE
JOIN NL_UM ON NL_SE.血統登録番号 = NL_UM.血統登録番号
JOIN NL_RA ON
    NL_SE.開催年月日 = NL_RA.開催年月日 AND
    NL_SE.競馬場コード = NL_RA.競馬場コード AND
    NL_SE.レース番号 = NL_RA.レース番号
JOIN NL_UM AS 父馬 ON NL_UM.父馬_血統登録番号 = 父馬.血統登録番号
WHERE 父馬.馬名 = 'ディープインパクト'
  AND NL_RA.グレード = 'A'
  AND NL_SE.着順 = 1;"""
    },
]


def build_prompt(user_query: str, include_examples: bool = True) -> str:
    """Build complete prompt for Text-to-SQL.

    Args:
        user_query: User's natural language query
        include_examples: Whether to include few-shot examples

    Returns:
        Complete prompt string
    """
    prompt_parts = [SYSTEM_PROMPT]

    if include_examples:
        prompt_parts.append("\n## 例題\n")
        for i, example in enumerate(FEW_SHOT_EXAMPLES, 1):
            prompt_parts.append(f"\n### 例{i}")
            prompt_parts.append(f"**クエリ**: {example['query']}")
            prompt_parts.append(f"**SQL**:\n```sql\n{example['sql']}\n```\n")

    prompt_parts.append(f"\n## あなたのタスク\n\n**クエリ**: {user_query}\n**SQL**:")

    return "\n".join(prompt_parts)
```

### 3.2 スキーマ情報の動的埋め込み

```python
"""Dynamic schema information for prompts."""

from typing import List, Dict
from src.database.base import BaseDatabase


def get_table_schema_info(database: BaseDatabase, table_name: str) -> str:
    """Get schema information for a specific table.

    Args:
        database: Database instance
        table_name: Name of the table

    Returns:
        Schema description string
    """
    # Get column information
    if hasattr(database, 'get_table_columns'):
        columns = database.get_table_columns(table_name)
    else:
        # Fallback: query PRAGMA or information_schema
        columns = _query_table_columns(database, table_name)

    schema_parts = [f"**{table_name}**"]
    for col in columns:
        schema_parts.append(f"- {col['name']} ({col['type']})")

    return "\n".join(schema_parts)


def _query_table_columns(database: BaseDatabase, table_name: str) -> List[Dict]:
    """Query table columns from database.

    Args:
        database: Database instance
        table_name: Name of the table

    Returns:
        List of column dictionaries
    """
    try:
        # Try SQLite PRAGMA
        result = database.fetch_all(f"PRAGMA table_info({table_name})")
        return [{"name": row["name"], "type": row["type"]} for row in result]
    except:
        # Try PostgreSQL information_schema
        sql = """
            SELECT column_name as name, data_type as type
            FROM information_schema.columns
            WHERE table_name = ?
            ORDER BY ordinal_position
        """
        result = database.fetch_all(sql, (table_name,))
        return result


def get_sample_data(database: BaseDatabase, table_name: str, limit: int = 3) -> str:
    """Get sample data from table for context.

    Args:
        database: Database instance
        table_name: Name of the table
        limit: Number of sample rows

    Returns:
        Formatted sample data string
    """
    try:
        rows = database.fetch_all(f"SELECT * FROM {table_name} LIMIT {limit}")

        if not rows:
            return "（データなし）"

        # Format as markdown table
        if rows:
            headers = list(rows[0].keys())
            lines = ["| " + " | ".join(headers) + " |"]
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

            for row in rows:
                values = [str(row.get(h, "")) for h in headers]
                lines.append("| " + " | ".join(values) + " |")

            return "\n".join(lines)
    except Exception as e:
        return f"（サンプルデータ取得エラー: {e}）"
```

---

## 4. レスポンス処理

### 4.1 SQL抽出パーサー

```python
"""SQL extraction and parsing."""

import re
from typing import Optional, Tuple


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

        >>> extract_sql("Here's the SQL:\\nSELECT * FROM NL_RA;")
        'SELECT * FROM NL_RA'
    """
    # Pattern 1: Code block with ```sql or ```SQL
    code_block_pattern = r"```(?:sql|SQL)\s*\n(.*?)\n```"
    match = re.search(code_block_pattern, llm_response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern 2: Generic code block ```...```
    generic_block_pattern = r"```\s*\n(.*?)\n```"
    match = re.search(generic_block_pattern, llm_response, re.DOTALL)
    if match:
        sql = match.group(1).strip()
        # Verify it looks like SQL
        if is_valid_sql_format(sql):
            return sql

    # Pattern 3: Direct SQL statement (starts with SELECT, INSERT, UPDATE, DELETE, WITH)
    sql_start_pattern = r"\b(SELECT|INSERT|UPDATE|DELETE|WITH)\b"
    match = re.search(sql_start_pattern, llm_response, re.IGNORECASE)
    if match:
        # Extract from match position to end (or semicolon)
        sql = llm_response[match.start():].strip()
        # Remove trailing explanation if any
        sql = re.split(r'\n\n', sql)[0]  # Take first paragraph
        return sql.rstrip(';').strip()

    return None


def is_valid_sql_format(text: str) -> bool:
    """Check if text looks like SQL.

    Args:
        text: Text to check

    Returns:
        True if looks like SQL, False otherwise
    """
    sql_keywords = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
        'ALTER', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY'
    ]

    text_upper = text.upper()
    return any(keyword in text_upper for keyword in sql_keywords)


def clean_sql(sql: str) -> str:
    """Clean and normalize SQL query.

    Args:
        sql: Raw SQL query

    Returns:
        Cleaned SQL query
    """
    # Remove comments
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

    # Normalize whitespace
    sql = re.sub(r'\s+', ' ', sql)
    sql = sql.strip()

    # Remove trailing semicolon
    sql = sql.rstrip(';')

    return sql
```

### 4.2 バリデーション

```python
"""SQL validation."""

import re
from typing import Tuple, Optional


class SQLValidationError(Exception):
    """SQL validation error."""
    pass


def validate_sql(sql: str, strict: bool = True) -> Tuple[bool, Optional[str]]:
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
    sql_upper = sql.upper()

    # Check 1: No dangerous operations
    dangerous_keywords = ['DROP', 'TRUNCATE', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
    for keyword in dangerous_keywords:
        if re.search(rf'\b{keyword}\b', sql_upper):
            return False, f"Dangerous SQL operation detected: {keyword}"

    # Check 2: Must be SELECT query
    if not sql_upper.strip().startswith('SELECT') and not sql_upper.strip().startswith('WITH'):
        return False, "Only SELECT queries are allowed"

    # Check 3: No suspicious patterns
    suspicious_patterns = [
        (r';\s*SELECT', "Multiple statements detected"),
        (r'--', "SQL comments not allowed"),
        (r'/\*', "SQL comments not allowed"),
        (r'EXEC\s*\(', "Dynamic SQL execution not allowed"),
    ]

    for pattern, message in suspicious_patterns:
        if re.search(pattern, sql, re.IGNORECASE):
            return False, message

    # Check 4: Table name whitelist (strict mode)
    if strict:
        allowed_tables = [
            'NL_RA', 'NL_SE', 'NL_HR', 'NL_UM', 'NL_KS', 'NL_CH', 'NL_JG',
            'NL_BN', 'NL_BR', 'NL_H1', 'NL_H6', 'NL_O1', 'NL_O2', 'NL_O3',
            'NL_O4', 'NL_O5', 'NL_O6', 'NL_YS', 'NL_TK',
            'RT_RA', 'RT_SE', 'RT_HR', 'RT_O1', 'RT_O2', 'RT_O3', 'RT_O4',
            'RT_O5', 'RT_O6'
        ]

        # Extract table names from SQL
        table_pattern = r'\bFROM\s+([A-Z_]+)\b|\bJOIN\s+([A-Z_]+)\b'
        found_tables = re.findall(table_pattern, sql_upper)
        found_tables = [t for group in found_tables for t in group if t]

        for table in found_tables:
            if table not in allowed_tables:
                return False, f"Table not allowed: {table}"

    return True, None


def add_safety_limits(sql: str, max_rows: int = 1000) -> str:
    """Add safety LIMIT clause if not present.

    Args:
        sql: SQL query
        max_rows: Maximum rows to return

    Returns:
        SQL query with LIMIT clause
    """
    sql_upper = sql.upper()

    # Check if LIMIT already exists
    if 'LIMIT' in sql_upper:
        # Extract existing limit
        match = re.search(r'LIMIT\s+(\d+)', sql_upper)
        if match:
            existing_limit = int(match.group(1))
            if existing_limit <= max_rows:
                return sql  # Already safe
            else:
                # Replace with max_rows
                return re.sub(
                    r'LIMIT\s+\d+',
                    f'LIMIT {max_rows}',
                    sql,
                    flags=re.IGNORECASE
                )

    # Add LIMIT clause
    sql = sql.rstrip(';').strip()
    return f"{sql} LIMIT {max_rows}"
```

### 4.3 エラーハンドリング

```python
"""Error handling for LLM queries."""

from typing import Optional, Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)


class QueryError(Exception):
    """Query processing error."""

    def __init__(
        self,
        message: str,
        error_type: str = "unknown",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize query error.

        Args:
            message: Error message
            error_type: Type of error (llm_error, sql_error, validation_error, etc.)
            details: Additional error details
        """
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
    logger.error(
        "Query processing failed",
        user_query=user_query,
        error=str(error),
        error_type=type(error).__name__
    )

    if isinstance(error, QueryError):
        if error.error_type == "llm_error":
            return (
                "LLMとの通信でエラーが発生しました。\n"
                f"詳細: {error}\n"
                "設定を確認してください。"
            )
        elif error.error_type == "sql_extraction_error":
            return (
                "LLMの応答からSQLを抽出できませんでした。\n"
                "クエリを変更して再試行してください。"
            )
        elif error.error_type == "validation_error":
            return (
                f"生成されたSQLが安全性チェックで失敗しました。\n"
                f"理由: {error}\n"
                "クエリを変更して再試行してください。"
            )
        elif error.error_type == "execution_error":
            return (
                f"SQLの実行でエラーが発生しました。\n"
                f"詳細: {error}\n"
                "クエリを確認してください。"
            )

    # Generic error
    return (
        f"クエリの処理中にエラーが発生しました。\n"
        f"詳細: {error}\n"
        "ログを確認してください。"
    )


def suggest_fix(error: Exception, sql: str) -> Optional[str]:
    """Suggest fix for common SQL errors.

    Args:
        error: SQL execution error
        sql: The SQL query that failed

    Returns:
        Suggestion string, or None
    """
    error_str = str(error).lower()

    # Common error patterns and suggestions
    suggestions = {
        "no such table": (
            "テーブルが存在しません。\n"
            "ヒント: 'jltsql create-tables' でテーブルを作成してください。"
        ),
        "no such column": (
            "カラムが存在しません。\n"
            "ヒント: スキーマ定義を確認してください。"
        ),
        "syntax error": (
            "SQL構文エラーです。\n"
            "ヒント: クエリの書き方を確認してください。"
        ),
        "ambiguous column": (
            "カラム名が曖昧です。\n"
            "ヒント: テーブル名を明示してください (例: NL_RA.開催年月日)"
        ),
    }

    for pattern, suggestion in suggestions.items():
        if pattern in error_str:
            return suggestion

    return None
```

---

## 5. CLIインターフェース

### 5.1 クエリコマンド実装

```python
"""CLI command for natural language queries."""

import click
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax

from src.cli.main import cli
from src.llm.factory import LLMProviderFactory
from src.llm.prompt import build_prompt
from src.llm.parser import extract_sql, clean_sql
from src.llm.validator import validate_sql, add_safety_limits
from src.llm.error_handler import handle_query_error, QueryError
from src.database.sqlite_handler import SQLiteDatabase
from src.database.postgresql_handler import PostgreSQLDatabase

console = Console(legacy_windows=True)


@cli.command()
@click.argument("query", required=True)
@click.option(
    "--provider",
    type=click.Choice(["ollama", "openrouter"]),
    help="LLM provider to use (default: from config)"
)
@click.option(
    "--model",
    help="Model to use (default: from config)"
)
@click.option(
    "--show-sql",
    is_flag=True,
    help="Show generated SQL query"
)
@click.option(
    "--explain",
    is_flag=True,
    help="Explain the generated SQL"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Only generate SQL, don't execute"
)
@click.option(
    "--db",
    type=click.Choice(["sqlite", "postgresql"]),
    default=None,
    help="Database type (default: from config)"
)
@click.pass_context
def query(ctx, query, provider, model, show_sql, explain, dry_run, db):
    """Execute natural language query.

    \b
    Examples:
      jltsql query "2024年のGⅠレースを全て表示して"
      jltsql query "武豊騎手の勝率を教えて" --show-sql
      jltsql query "3連単の最高配当は?" --provider ollama
      jltsql query "東京競馬場のレース数" --dry-run
    """
    config = ctx.obj.get("config")

    # Get LLM config
    llm_config = config.get("llm", {}) if config else {}

    # Override with CLI options
    if provider:
        llm_config["provider"] = provider
    if model:
        llm_config["model"] = model

    # Validate LLM config
    if not llm_config.get("model"):
        console.print(
            "[red]Error:[/red] No LLM model configured. "
            "Please set in config.yaml or use --model option."
        )
        return

    console.print(f"[bold cyan]Processing query:[/bold cyan] {query}\n")

    try:
        # Step 1: Initialize LLM provider
        console.print("[dim]Initializing LLM provider...[/dim]")
        llm = LLMProviderFactory.from_dict(llm_config)

        if not llm.is_available():
            console.print(
                f"[red]Error:[/red] LLM provider '{llm_config['provider']}' is not available.\n"
                f"Model: {llm_config['model']}"
            )
            return

        # Step 2: Build prompt
        console.print("[dim]Building prompt...[/dim]")
        from src.llm.base import LLMMessage
        prompt = build_prompt(query, include_examples=True)
        messages = [LLMMessage(role="user", content=prompt)]

        # Step 3: Generate SQL
        console.print(f"[dim]Generating SQL with {llm_config['model']}...[/dim]")
        response = llm.generate(messages)

        # Step 4: Extract SQL
        sql = extract_sql(response.content)
        if not sql:
            raise QueryError(
                "Could not extract SQL from LLM response",
                error_type="sql_extraction_error"
            )

        sql = clean_sql(sql)

        # Step 5: Validate SQL
        console.print("[dim]Validating SQL...[/dim]")
        is_valid, error_msg = validate_sql(sql, strict=True)
        if not is_valid:
            raise QueryError(
                error_msg,
                error_type="validation_error"
            )

        # Step 6: Add safety limits
        sql = add_safety_limits(sql, max_rows=1000)

        # Show generated SQL
        if show_sql or dry_run:
            console.print("\n[bold]Generated SQL:[/bold]")
            syntax = Syntax(sql, "sql", theme="monokai", line_numbers=False)
            console.print(syntax)
            console.print()

        if dry_run:
            console.print("[yellow]Dry run mode - SQL not executed[/yellow]")
            return

        # Step 7: Execute SQL
        # Determine database type
        if db:
            db_type = db
        else:
            db_type = config.get("database.type", "sqlite") if config else "sqlite"

        console.print(f"[dim]Executing query on {db_type}...[/dim]\n")

        # Initialize database
        if db_type == "sqlite":
            db_config = config.get("databases.sqlite") if config else {"path": "data/keiba.db"}
            database = SQLiteDatabase(db_config)
        elif db_type == "postgresql":
            if not config:
                console.print("[red]Error:[/red] PostgreSQL requires configuration file.")
                return
            database = PostgreSQLDatabase(config.get("databases.postgresql"))
        else:
            console.print(f"[red]Error:[/red] Unsupported database type: {db_type}")
            return

        # Execute query
        with database:
            try:
                results = database.fetch_all(sql)
            except Exception as e:
                raise QueryError(
                    str(e),
                    error_type="execution_error"
                )

        # Step 8: Display results
        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return

        # Create rich table
        table = Table(show_header=True, header_style="bold cyan")

        # Add columns
        headers = list(results[0].keys())
        for header in headers:
            table.add_column(header)

        # Add rows
        for row in results:
            table.add_row(*[str(row[h] if row[h] is not None else "") for h in headers])

        console.print(table)
        console.print(f"\n[dim]Rows returned: {len(results)}[/dim]")

        # Show token usage if available
        if response.tokens_used:
            console.print(f"[dim]Tokens used: {response.tokens_used}[/dim]")

    except QueryError as e:
        error_msg = handle_query_error(e, query)
        console.print(f"\n[red][ERROR][/red]\n{error_msg}")
    except Exception as e:
        error_msg = handle_query_error(e, query)
        console.print(f"\n[red][UNEXPECTED ERROR][/red]\n{error_msg}")
```

---

## 6. 設定ファイル拡張

### 6.1 config.yaml拡張

```yaml
# LLM Configuration
llm:
  # Provider: "ollama" or "openrouter"
  provider: "ollama"

  # Model name
  model: "codellama:13b-instruct"

  # Generation parameters
  temperature: 0.1  # Low temperature for deterministic SQL
  max_tokens: 1000
  timeout: 30

  # Ollama-specific settings
  ollama:
    base_url: "http://localhost:11434"

  # OpenRouter-specific settings (uncomment to use)
  # openrouter:
  #   api_key: "sk-or-v1-..."  # Get from https://openrouter.ai/keys
  #   base_url: "https://openrouter.ai/api/v1"

  # Prompt settings
  prompt:
    include_examples: true
    max_examples: 6

  # Safety settings
  validation:
    strict_mode: true
    max_result_rows: 1000
    allowed_tables:
      - NL_*
      - RT_*
```

---

## 7. 推奨モデル

### 7.1 ローカルLLM（Ollama）

#### 最推奨

**1. DeepSeek-Coder 6.7B Instruct**
```bash
ollama pull deepseek-coder:6.7b-instruct
```
- **理由**: コード生成に特化、SQLに強い
- **メモリ**: 8GB RAM
- **速度**: 高速（6.7Bパラメータ）
- **精度**: Text-to-SQLで高精度

**2. CodeLlama 13B Instruct**
```bash
ollama pull codellama:13b-instruct
```
- **理由**: Meta開発、コード特化
- **メモリ**: 16GB RAM
- **速度**: 中速
- **精度**: 非常に高い

#### 代替モデル

**3. SQLCoder 15B**
```bash
ollama pull sqlcoder:15b
```
- **理由**: Text-to-SQL専用モデル
- **メモリ**: 32GB RAM
- **速度**: 低速
- **精度**: SQL生成に最適化

**4. Mistral 7B Instruct v0.2**
```bash
ollama pull mistral:7b-instruct-v0.2
```
- **理由**: 汎用性が高い
- **メモリ**: 8GB RAM
- **速度**: 高速
- **精度**: 良好

### 7.2 OpenRouter（クラウドAPI）

#### コスト対効果推奨

**1. Google Gemini Pro 1.5**
- **モデルID**: `google/gemini-pro-1.5`
- **料金**: $0.50/1M tokens (入力・出力平均)
- **理由**: 高性能・低価格、長いコンテキスト
- **推奨用途**: 一般利用

**2. Anthropic Claude 3 Haiku**
- **モデルID**: `anthropic/claude-3-haiku`
- **料金**: $0.25/1M tokens (入力), $1.25/1M tokens (出力)
- **理由**: 超高速、低コスト
- **推奨用途**: 大量クエリ処理

**3. DeepSeek Coder 33B Instruct**
- **モデルID**: `deepseek/deepseek-coder-33b-instruct`
- **料金**: $0.14/1M tokens
- **理由**: 最安値、コード特化
- **推奨用途**: コスト重視

#### 高精度モデル

**4. Anthropic Claude 3 Sonnet**
- **モデルID**: `anthropic/claude-3-sonnet`
- **料金**: $3.00/1M tokens (入力), $15.00/1M tokens (出力)
- **理由**: 最高精度、複雑なクエリに対応
- **推奨用途**: 本番環境・重要クエリ

**5. OpenAI GPT-4 Turbo**
- **モデルID**: `openai/gpt-4-turbo`
- **料金**: $10.00/1M tokens (入力), $30.00/1M tokens (出力)
- **理由**: 非常に高精度
- **推奨用途**: 高精度が必要な場合

### 7.3 モデル選択ガイド

```python
"""Model selection guide."""

# メモリ別推奨（ローカル）
MEMORY_RECOMMENDATIONS = {
    "8GB": ["deepseek-coder:6.7b-instruct", "mistral:7b-instruct-v0.2"],
    "16GB": ["codellama:13b-instruct", "deepseek-coder:6.7b-instruct"],
    "32GB": ["sqlcoder:15b", "codellama:34b-instruct"],
}

# 用途別推奨（OpenRouter）
USE_CASE_RECOMMENDATIONS = {
    "cost_optimized": "deepseek/deepseek-coder-33b-instruct",
    "speed_optimized": "anthropic/claude-3-haiku",
    "quality_optimized": "anthropic/claude-3-sonnet",
    "balanced": "google/gemini-pro-1.5",
}

# コスト試算（1000クエリあたり、平均500 tokens/query）
COST_ESTIMATES = {
    "google/gemini-pro-1.5": 0.25,  # $0.25
    "anthropic/claude-3-haiku": 0.13,  # $0.13
    "deepseek/deepseek-coder-33b-instruct": 0.07,  # $0.07
    "anthropic/claude-3-sonnet": 1.50,  # $1.50
    "openai/gpt-4-turbo": 5.00,  # $5.00
}
```

---

## 8. 使用例

### 8.1 基本的な使用例

```bash
# Ollamaで簡単なクエリ
jltsql query "2024年のGⅠレースを全て表示して"

# SQL表示
jltsql query "武豊騎手の勝率を教えて" --show-sql

# Dry run（SQLのみ生成、実行しない）
jltsql query "3連単の最高配当は?" --dry-run

# プロバイダー指定
jltsql query "東京競馬場のレース数" --provider openrouter --model google/gemini-pro-1.5
```

### 8.2 Python APIでの使用

```python
from src.llm.factory import LLMProviderFactory, LLMConfig, LLMProviderType
from src.llm.base import LLMMessage
from src.llm.prompt import build_prompt
from src.llm.parser import extract_sql, clean_sql
from src.llm.validator import validate_sql, add_safety_limits
from src.database.sqlite_handler import SQLiteDatabase

# 1. LLM初期化
config = LLMConfig(
    provider=LLMProviderType.OLLAMA,
    model="codellama:13b-instruct",
    temperature=0.1
)
llm = LLMProviderFactory.create(config)

# 2. クエリ生成
user_query = "2024年のGⅠレースを全て表示して"
prompt = build_prompt(user_query)
messages = [LLMMessage(role="user", content=prompt)]

response = llm.generate(messages)

# 3. SQL抽出
sql = extract_sql(response.content)
sql = clean_sql(sql)

# 4. バリデーション
is_valid, error = validate_sql(sql)
if not is_valid:
    print(f"Validation error: {error}")
    exit(1)

sql = add_safety_limits(sql, max_rows=1000)

# 5. 実行
database = SQLiteDatabase({"path": "data/keiba.db"})
with database:
    results = database.fetch_all(sql)

for row in results:
    print(row)
```

---

## 9. テスト戦略

### 9.1 単体テスト

```python
"""Tests for LLM integration."""

import pytest
from src.llm.factory import LLMProviderFactory, LLMConfig, LLMProviderType
from src.llm.parser import extract_sql, clean_sql
from src.llm.validator import validate_sql


class TestSQLExtraction:
    """Test SQL extraction from LLM responses."""

    def test_extract_from_code_block(self):
        """Test extraction from ```sql code block."""
        response = """Here's the SQL:
```sql
SELECT * FROM NL_RA WHERE 開催年月日 >= 20240101
```
        """
        sql = extract_sql(response)
        assert sql == "SELECT * FROM NL_RA WHERE 開催年月日 >= 20240101"

    def test_extract_direct_sql(self):
        """Test extraction of direct SQL."""
        response = "SELECT * FROM NL_RA LIMIT 10"
        sql = extract_sql(response)
        assert sql == "SELECT * FROM NL_RA LIMIT 10"

    def test_clean_sql(self):
        """Test SQL cleaning."""
        sql = """
        SELECT * FROM NL_RA  -- Get all races
        WHERE 開催年月日 >= 20240101;
        """
        cleaned = clean_sql(sql)
        assert "--" not in cleaned
        assert ";" not in cleaned


class TestSQLValidation:
    """Test SQL validation."""

    def test_valid_select(self):
        """Test valid SELECT query."""
        sql = "SELECT * FROM NL_RA LIMIT 10"
        is_valid, error = validate_sql(sql)
        assert is_valid
        assert error is None

    def test_invalid_drop(self):
        """Test rejection of DROP statement."""
        sql = "DROP TABLE NL_RA"
        is_valid, error = validate_sql(sql)
        assert not is_valid
        assert "DROP" in error

    def test_invalid_table(self):
        """Test rejection of unknown table."""
        sql = "SELECT * FROM unknown_table"
        is_valid, error = validate_sql(sql, strict=True)
        assert not is_valid
        assert "not allowed" in error
```

### 9.2 統合テスト

```python
"""Integration tests for Text-to-SQL."""

import pytest
from src.llm.factory import LLMProviderFactory, LLMConfig, LLMProviderType
from src.llm.base import LLMMessage
from src.llm.prompt import build_prompt


@pytest.mark.integration
class TestTextToSQL:
    """Integration tests for full Text-to-SQL pipeline."""

    @pytest.fixture
    def ollama_provider(self):
        """Create Ollama provider."""
        config = LLMConfig(
            provider=LLMProviderType.OLLAMA,
            model="codellama:13b-instruct"
        )
        provider = LLMProviderFactory.create(config)

        if not provider.is_available():
            pytest.skip("Ollama not available")

        return provider

    def test_gi_races_query(self, ollama_provider):
        """Test GⅠ races query."""
        query = "2024年のGⅠレースを全て表示して"
        prompt = build_prompt(query)
        messages = [LLMMessage(role="user", content=prompt)]

        response = ollama_provider.generate(messages)

        from src.llm.parser import extract_sql
        sql = extract_sql(response.content)

        assert sql is not None
        assert "NL_RA" in sql
        assert "グレード" in sql or "GRADE" in sql.upper()
        assert "2024" in sql or "20240101" in sql
```

---

## 10. デプロイメントと運用

### 10.1 Ollamaセットアップ

```bash
# 1. Ollamaインストール（Windows）
# https://ollama.ai/download からインストーラーをダウンロード

# 2. Ollama起動
ollama serve

# 3. モデルダウンロード
ollama pull deepseek-coder:6.7b-instruct
ollama pull codellama:13b-instruct

# 4. モデル確認
ollama list

# 5. テスト
ollama run deepseek-coder:6.7b-instruct "SELECT * FROM users"
```

### 10.2 OpenRouterセットアップ

```bash
# 1. API キー取得
# https://openrouter.ai/keys にアクセス

# 2. 環境変数設定
set OPENROUTER_API_KEY=sk-or-v1-...

# 3. config.yaml に追加
# llm:
#   provider: openrouter
#   model: google/gemini-pro-1.5
#   openrouter:
#     api_key: ${OPENROUTER_API_KEY}
```

### 10.3 パフォーマンス最適化

```yaml
# config.yaml - パフォーマンス設定

llm:
  # キャッシュ設定
  cache:
    enabled: true
    ttl: 3600  # 1時間
    max_entries: 1000

  # バッチ処理
  batch:
    enabled: true
    max_batch_size: 10

  # タイムアウト
  timeout: 30

  # リトライ
  retry:
    max_attempts: 3
    backoff_factor: 2
```

---

## 11. まとめ

本設計書では、JRVLTSQLアプリケーションへのLLM統合の詳細設計を定義しました。

### 主要コンポーネント

1. **LLMプロバイダー抽象化層**: Ollama、OpenRouterを統一インターフェースで利用
2. **プロンプトエンジニアリング**: 競馬ドメイン特化のText-to-SQLプロンプト
3. **SQL抽出・バリデーション**: 安全性を確保したSQL生成
4. **CLIインターフェース**: `jltsql query` コマンドで自然言語クエリを実行

### 推奨構成

**ローカル開発環境**
- Ollama + DeepSeek-Coder 6.7B Instruct
- メモリ: 8GB RAM以上
- 無料、高速

**本番環境**
- OpenRouter + Google Gemini Pro 1.5
- コスト: $0.50/1M tokens
- 高精度、スケーラブル

### 次のステップ

1. `src/llm/` ディレクトリ作成
2. 各モジュール実装（base.py, ollama.py, openrouter.py, factory.py, prompt.py, parser.py, validator.py, error_handler.py）
3. CLIコマンド実装（`jltsql query`）
4. テスト実装
5. ドキュメント作成

これにより、ユーザーは自然言語で競馬データベースをクエリできるようになります。
