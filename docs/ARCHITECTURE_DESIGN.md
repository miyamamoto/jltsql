# 競馬データ分析アプリケーション アーキテクチャ設計書

## 1. 概要

本文書は、JRA-VAN DataLabの競馬データベースを使用した自然言語からSQLを生成する競馬データ分析アプリケーションのアーキテクチャを定義します。

### 1.1 要件サマリー

- **データソース**: JRA-VAN DataLab（SQLite/PostgreSQL）
- **コア機能**: 自然言語 → SQL生成 → クエリ実行 → 結果フォーマット
- **LLMプロバイダー**:
  1. ローカルLLM（Ollama等）
  2. OpenRouter API
- **既存システム**: JRVLTSQLプロジェクト（データ取得・インポート機能）

---

## 2. アーキテクチャ全体図

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │     CLI      │  │   Web API    │  │  Interactive │          │
│  │   Interface  │  │  (FastAPI)   │  │   REPL       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                     Application Layer                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Query Orchestrator                          │   │
│  │  (自然言語入力 → SQL生成 → 実行 → 整形)                 │   │
│  └───────┬──────────────────────────────────────────────────┘   │
│          │                                                       │
│  ┌───────┴──────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ SQL Generator│  │Query Executor│  │   Result     │         │
│  │   Service    │  │   Service    │  │  Formatter   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                       Domain Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Schema     │  │    Query     │  │   Analysis   │          │
│  │   Context    │  │   Validator  │  │    Result    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                   Infrastructure Layer                           │
│  ┌──────────────────┐  ┌───────────────┐  ┌──────────────┐     │
│  │ LLM Provider     │  │   Database    │  │  Monitoring  │     │
│  │  Abstraction     │  │   Handlers    │  │  & Logging   │     │
│  │                  │  │               │  │              │     │
│  │ ┌──────┐ ┌────┐ │  │ ┌────┐ ┌────┐│  │              │     │
│  │ │Ollama│ │OR  │ │  │ │SQLi│ │Post││  │              │     │
│  │ │      │ │API │ │  │ │te  │ │gre ││  │              │     │
│  │ └──────┘ └────┘ │  │ └────┘ └────┘│  │              │     │
│  └──────────────────┘  └───────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. レイヤー構成

### 3.1 Presentation Layer（プレゼンテーション層）

**責務**: ユーザーインターフェース、入出力の制御

#### 3.1.1 CLI Interface
```python
# src/cli/query_command.py
@click.command()
@click.argument("query", type=str)
@click.option("--format", type=click.Choice(["table", "json", "csv"]))
@click.option("--llm", type=click.Choice(["ollama", "openrouter"]))
def query(query: str, format: str, llm: str):
    """自然言語クエリを実行"""
    pass
```

**特徴**:
- `click`ベースのコマンドライン
- Rich UI（テーブル表示、プログレスバー）
- パイプライン対応（標準入出力）

#### 3.1.2 Web API（Optional）
```python
# src/api/main.py (FastAPI)
@app.post("/api/v1/query")
async def execute_query(request: QueryRequest) -> QueryResponse:
    """REST API経由でクエリ実行"""
    pass
```

#### 3.1.3 Interactive REPL
```python
# src/repl/interactive.py
while True:
    query = prompt("keiba> ")
    # SQL生成 → 実行 → 表示
```

---

### 3.2 Application Layer（アプリケーション層）

**責務**: ビジネスロジックの調整、ユースケースの実装

#### 3.2.1 Query Orchestrator
```python
# src/application/query_orchestrator.py

class QueryOrchestrator:
    """クエリ実行の全体フローを制御"""

    def __init__(
        self,
        sql_generator: SQLGeneratorService,
        query_executor: QueryExecutorService,
        result_formatter: ResultFormatterService
    ):
        self.sql_generator = sql_generator
        self.query_executor = query_executor
        self.result_formatter = result_formatter

    async def execute_natural_query(
        self,
        natural_query: str,
        output_format: OutputFormat = OutputFormat.TABLE
    ) -> AnalysisResult:
        """
        自然言語クエリを実行して結果を返す

        フロー:
        1. 自然言語 → SQL生成
        2. SQL検証
        3. クエリ実行
        4. 結果整形
        5. 統計情報付与
        """
        # 1. SQL生成
        sql_result = await self.sql_generator.generate_sql(natural_query)

        if not sql_result.is_valid:
            return AnalysisResult.error(sql_result.error_message)

        # 2. クエリ実行
        query_result = self.query_executor.execute(sql_result.sql)

        # 3. 結果整形
        formatted_result = self.result_formatter.format(
            query_result,
            output_format
        )

        return AnalysisResult(
            sql=sql_result.sql,
            data=formatted_result,
            metadata=self._create_metadata(query_result)
        )
```

#### 3.2.2 SQL Generator Service
```python
# src/application/services/sql_generator_service.py

class SQLGeneratorService:
    """自然言語からSQL生成"""

    def __init__(
        self,
        llm_provider: LLMProvider,
        schema_context: SchemaContext
    ):
        self.llm_provider = llm_provider
        self.schema_context = schema_context

    async def generate_sql(
        self,
        natural_query: str,
        max_retries: int = 3
    ) -> SQLGenerationResult:
        """
        自然言語からSQLを生成

        戦略:
        1. スキーマコンテキスト取得
        2. プロンプト構築
        3. LLM呼び出し
        4. SQL抽出・検証
        5. 失敗時はリトライ（最大max_retries回）
        """
        # スキーマ情報取得
        schema_info = self.schema_context.get_relevant_schema(natural_query)

        # プロンプト構築
        prompt = self._build_prompt(natural_query, schema_info)

        # LLM呼び出し（リトライロジック含む）
        for attempt in range(max_retries):
            try:
                response = await self.llm_provider.generate(prompt)
                sql = self._extract_sql(response)

                # SQL検証
                validation = self._validate_sql(sql)
                if validation.is_valid:
                    return SQLGenerationResult.success(sql, response)

            except LLMProviderError as e:
                if attempt == max_retries - 1:
                    return SQLGenerationResult.error(str(e))

        return SQLGenerationResult.error("Failed to generate valid SQL")

    def _build_prompt(
        self,
        natural_query: str,
        schema_info: SchemaInfo
    ) -> str:
        """プロンプト構築"""
        return f"""
あなたはJRA-VAN競馬データベースの専門家です。
以下の自然言語クエリをSQLに変換してください。

## データベーススキーマ
{schema_info.format_for_prompt()}

## テーブル説明
- NL_RA: レース情報（開催年月日、競馬場コード、レース番号等）
- NL_SE: 競走馬情報（血統番号、馬名等）
- NL_UM: 馬毎レース情報（着順、タイム等）
- NL_HR: 払戻情報（単勝、馬連、三連単等）

## 自然言語クエリ
{natural_query}

## 要件
1. PostgreSQL/SQLite互換のSQLを生成
2. 日本語列名を正確に使用
3. SELECTクエリのみ許可
4. JOINが必要な場合は適切に結合

生成したSQLのみを出力してください（説明不要）。
```sql
<ここにSQLを記述>
```
"""
```

#### 3.2.3 Query Executor Service
```python
# src/application/services/query_executor_service.py

class QueryExecutorService:
    """SQLクエリ実行"""

    def __init__(
        self,
        database: BaseDatabase,
        query_validator: QueryValidator,
        config: QueryConfig
    ):
        self.database = database
        self.query_validator = query_validator
        self.config = config

    def execute(
        self,
        sql: str,
        params: Optional[tuple] = None
    ) -> QueryResult:
        """
        SQLクエリを実行

        セーフティチェック:
        1. READ ONLYチェック（SELECT以外拒否）
        2. タイムアウト設定
        3. 結果行数制限
        """
        # バリデーション
        validation = self.query_validator.validate(sql)
        if not validation.is_valid:
            raise QueryValidationError(validation.error_message)

        # タイムアウト設定
        with query_timeout(self.config.timeout_seconds):
            try:
                rows = self.database.fetch_all(sql, params)

                # 結果行数制限
                if len(rows) > self.config.max_rows:
                    logger.warning(
                        f"Query returned {len(rows)} rows, "
                        f"truncating to {self.config.max_rows}"
                    )
                    rows = rows[:self.config.max_rows]

                return QueryResult.success(rows)

            except DatabaseError as e:
                return QueryResult.error(str(e))
```

#### 3.2.4 Result Formatter Service
```python
# src/application/services/result_formatter_service.py

class ResultFormatterService:
    """クエリ結果の整形"""

    def format(
        self,
        query_result: QueryResult,
        output_format: OutputFormat
    ) -> FormattedResult:
        """結果を指定フォーマットに整形"""

        formatters = {
            OutputFormat.TABLE: self._format_table,
            OutputFormat.JSON: self._format_json,
            OutputFormat.CSV: self._format_csv,
            OutputFormat.MARKDOWN: self._format_markdown
        }

        formatter = formatters.get(output_format)
        if not formatter:
            raise ValueError(f"Unsupported format: {output_format}")

        return formatter(query_result)

    def _format_table(self, result: QueryResult) -> str:
        """Rich Tableフォーマット"""
        from rich.table import Table

        table = Table(title="Query Result")

        # ヘッダー
        for col in result.columns:
            table.add_column(col, style="cyan")

        # データ行
        for row in result.rows:
            table.add_row(*[str(v) for v in row.values()])

        return table
```

---

### 3.3 Domain Layer（ドメイン層）

**責務**: ビジネスロジック、ドメイン知識のカプセル化

#### 3.3.1 Schema Context
```python
# src/domain/schema_context.py

class SchemaContext:
    """データベーススキーマのコンテキスト管理"""

    def __init__(self, database: BaseDatabase):
        self.database = database
        self._schema_cache = {}

    def get_relevant_schema(
        self,
        natural_query: str
    ) -> SchemaInfo:
        """
        自然言語クエリに関連するスキーマ情報を抽出

        戦略:
        1. キーワードマッチング（レース、馬、払戻等）
        2. 関連テーブル特定
        3. 列情報取得
        """
        # キーワード抽出
        keywords = self._extract_keywords(natural_query)

        # 関連テーブル特定
        relevant_tables = self._identify_tables(keywords)

        # スキーマ情報構築
        schema_info = SchemaInfo()
        for table_name in relevant_tables:
            table_schema = self._get_table_schema(table_name)
            schema_info.add_table(table_schema)

        return schema_info

    def _identify_tables(self, keywords: List[str]) -> List[str]:
        """キーワードから関連テーブルを特定"""
        table_mapping = {
            "レース": ["NL_RA"],
            "馬": ["NL_SE", "NL_UM"],
            "競走馬": ["NL_SE", "NL_UM"],
            "払戻": ["NL_HR"],
            "オッズ": ["RT_O1", "RT_O2"],
            "着順": ["NL_UM"],
            "騎手": ["NL_KS"],
            "調教師": ["NL_KS"]
        }

        tables = set()
        for keyword in keywords:
            if keyword in table_mapping:
                tables.update(table_mapping[keyword])

        # デフォルトで主要テーブルを含める
        if not tables:
            tables = {"NL_RA", "NL_SE", "NL_UM"}

        return list(tables)
```

#### 3.3.2 Query Validator
```python
# src/domain/query_validator.py

class QueryValidator:
    """SQLクエリの検証"""

    def validate(self, sql: str) -> ValidationResult:
        """
        SQLの安全性・正当性を検証

        チェック項目:
        1. SELECT文のみ許可
        2. 危険な操作の検出（DROP, DELETE等）
        3. 構文チェック
        """
        # 小文字化して検証
        sql_lower = sql.lower().strip()

        # SELECT以外拒否
        if not sql_lower.startswith("select"):
            return ValidationResult.error(
                "Only SELECT queries are allowed"
            )

        # 危険なキーワード検出
        dangerous_keywords = [
            "drop", "delete", "insert", "update",
            "truncate", "alter", "create"
        ]

        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                return ValidationResult.error(
                    f"Dangerous keyword detected: {keyword}"
                )

        # 構文チェック（簡易版）
        try:
            sqlparse.parse(sql)
        except Exception as e:
            return ValidationResult.error(f"Syntax error: {e}")

        return ValidationResult.success()
```

#### 3.3.3 Analysis Result
```python
# src/domain/analysis_result.py

@dataclass
class AnalysisResult:
    """分析結果を表すドメインモデル"""

    sql: str
    data: Any  # FormattedResult
    metadata: ResultMetadata
    status: ResultStatus
    error_message: Optional[str] = None

    @classmethod
    def success(
        cls,
        sql: str,
        data: Any,
        metadata: ResultMetadata
    ) -> "AnalysisResult":
        return cls(
            sql=sql,
            data=data,
            metadata=metadata,
            status=ResultStatus.SUCCESS
        )

    @classmethod
    def error(cls, error_message: str) -> "AnalysisResult":
        return cls(
            sql="",
            data=None,
            metadata=None,
            status=ResultStatus.ERROR,
            error_message=error_message
        )

@dataclass
class ResultMetadata:
    """結果メタデータ"""
    row_count: int
    execution_time_ms: float
    columns: List[str]
    query_plan: Optional[str] = None  # EXPLAIN結果
```

---

### 3.4 Infrastructure Layer（インフラストラクチャ層）

**責務**: 外部システム連携、技術的実装

#### 3.4.1 LLM Provider Abstraction

```python
# src/infrastructure/llm/base.py

class LLMProvider(ABC):
    """LLMプロバイダーの抽象基底クラス"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """テキスト生成"""
        pass

    @abstractmethod
    def get_model_info(self) -> ModelInfo:
        """モデル情報取得"""
        pass

# src/infrastructure/llm/ollama_provider.py

class OllamaProvider(LLMProvider):
    """OllamaローカルLLMプロバイダー"""

    def __init__(self, config: OllamaConfig):
        self.base_url = config.base_url or "http://localhost:11434"
        self.model = config.model or "llama3.2"
        self.client = httpx.AsyncClient(timeout=config.timeout)

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> LLMResponse:
        """Ollama APIでテキスト生成"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json=payload
        )

        if response.status_code != 200:
            raise LLMProviderError(
                f"Ollama API error: {response.status_code}"
            )

        data = response.json()
        return LLMResponse(
            text=data["response"],
            model=self.model,
            provider="ollama"
        )

# src/infrastructure/llm/openrouter_provider.py

class OpenRouterProvider(LLMProvider):
    """OpenRouter APIプロバイダー"""

    def __init__(self, config: OpenRouterConfig):
        self.api_key = config.api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = config.model or "anthropic/claude-3.5-sonnet"
        self.client = httpx.AsyncClient(timeout=config.timeout)

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> LLMResponse:
        """OpenRouter APIでテキスト生成"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            raise LLMProviderError(
                f"OpenRouter API error: {response.status_code}"
            )

        data = response.json()
        return LLMResponse(
            text=data["choices"][0]["message"]["content"],
            model=self.model,
            provider="openrouter",
            usage=data.get("usage")
        )

# src/infrastructure/llm/factory.py

class LLMProviderFactory:
    """LLMプロバイダーのファクトリー"""

    @staticmethod
    def create(config: Config) -> LLMProvider:
        """設定からプロバイダーを生成"""

        llm_type = config.get("llm.provider")

        if llm_type == "ollama":
            return OllamaProvider(
                OllamaConfig(
                    base_url=config.get("llm.ollama.base_url"),
                    model=config.get("llm.ollama.model"),
                    timeout=config.get("llm.ollama.timeout", 60)
                )
            )

        elif llm_type == "openrouter":
            return OpenRouterProvider(
                OpenRouterConfig(
                    api_key=config.get("llm.openrouter.api_key"),
                    model=config.get("llm.openrouter.model"),
                    timeout=config.get("llm.openrouter.timeout", 60)
                )
            )

        else:
            raise ValueError(f"Unknown LLM provider: {llm_type}")
```

#### 3.4.2 Database Handlers（既存実装を活用）

```python
# 既存のBaseDatabase, SQLiteDatabase, PostgreSQLDatabaseを使用
from src.database.base import BaseDatabase
from src.database.sqlite_handler import SQLiteDatabase
from src.database.postgresql_handler import PostgreSQLDatabase
```

#### 3.4.3 Monitoring & Logging

```python
# src/infrastructure/monitoring/query_monitor.py

class QueryMonitor:
    """クエリ実行のモニタリング"""

    def __init__(self, logger: Logger):
        self.logger = logger
        self.metrics = QueryMetrics()

    @contextmanager
    def track_query(self, query: str):
        """クエリ実行時間を計測"""
        start_time = time.time()
        try:
            yield
            execution_time = time.time() - start_time
            self.metrics.record_success(query, execution_time)
            self.logger.info(
                "Query executed successfully",
                execution_time_ms=execution_time * 1000
            )
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.record_failure(query, execution_time)
            self.logger.error(
                "Query execution failed",
                error=str(e),
                execution_time_ms=execution_time * 1000
            )
            raise

class QueryMetrics:
    """クエリメトリクス収集"""

    def __init__(self):
        self.total_queries = 0
        self.successful_queries = 0
        self.failed_queries = 0
        self.total_execution_time = 0.0

    def record_success(self, query: str, execution_time: float):
        self.total_queries += 1
        self.successful_queries += 1
        self.total_execution_time += execution_time

    def record_failure(self, query: str, execution_time: float):
        self.total_queries += 1
        self.failed_queries += 1
        self.total_execution_time += execution_time

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_queries": self.total_queries,
            "successful_queries": self.successful_queries,
            "failed_queries": self.failed_queries,
            "average_execution_time": (
                self.total_execution_time / self.total_queries
                if self.total_queries > 0 else 0
            ),
            "success_rate": (
                self.successful_queries / self.total_queries * 100
                if self.total_queries > 0 else 0
            )
        }
```

---

## 4. 主要コンポーネント詳細

### 4.1 LLMプロバイダー抽象化層

#### 設計原則
- **Strategy Pattern**: プロバイダー切り替えが容易
- **Dependency Injection**: テスト可能性確保
- **Async/Await**: 非同期処理対応

#### インターフェース統一
```python
class LLMProvider(ABC):
    async def generate(prompt: str) -> LLMResponse
    def get_model_info() -> ModelInfo
```

#### 実装プロバイダー
1. **OllamaProvider**: ローカルLLM（Ollama API）
2. **OpenRouterProvider**: クラウドLLM（OpenRouter API）

#### 拡張可能性
新しいLLMプロバイダーの追加は`LLMProvider`を継承するだけ:
```python
class CustomProvider(LLMProvider):
    async def generate(self, prompt: str) -> LLMResponse:
        # 実装
```

---

### 4.2 SQL生成エンジン

#### コアロジック
1. **コンテキスト取得**: 自然言語からキーワード抽出 → 関連スキーマ特定
2. **プロンプト構築**: スキーマ情報 + サンプルクエリ + 自然言語
3. **LLM呼び出し**: プロバイダー経由でSQL生成
4. **SQL抽出**: マークダウンコードブロックから抽出
5. **検証**: 構文チェック + セーフティチェック

#### プロンプトエンジニアリング
```python
def _build_prompt(natural_query: str, schema_info: SchemaInfo) -> str:
    """
    プロンプト構築戦略:
    1. 役割定義（競馬DB専門家）
    2. スキーマ情報提供
    3. サンプルクエリ（Few-shot learning）
    4. 制約条件明示
    """
    return f"""
# 役割
あなたはJRA-VAN競馬データベースの専門家です。

# スキーマ
{schema_info.format_for_prompt()}

# サンプルクエリ
Q: 2024年の東京競馬場のレース一覧を取得
A:
```sql
SELECT * FROM NL_RA
WHERE 開催年月日 BETWEEN 20240101 AND 20241231
  AND 競馬場コード = '05';
```

# クエリ
{natural_query}

# 制約
- PostgreSQL/SQLite互換SQL
- SELECT文のみ
- 日本語列名を使用
"""
```

#### リトライ戦略
```python
max_retries = 3
for attempt in range(max_retries):
    sql = llm.generate(prompt)
    if validate(sql):
        return sql
    # プロンプト改善して再試行
```

---

### 4.3 クエリ実行エンジン

#### セーフティメカニズム

```python
class QueryExecutorService:
    """セーフティチェック付きクエリ実行"""

    def execute(self, sql: str) -> QueryResult:
        # 1. READ ONLY検証
        if not is_read_only(sql):
            raise SecurityError("Write operations not allowed")

        # 2. タイムアウト設定
        with timeout(30):  # 30秒
            # 3. 実行
            rows = database.fetch_all(sql)

        # 4. 結果行数制限
        if len(rows) > 10000:
            rows = rows[:10000]
            logger.warning("Result truncated to 10000 rows")

        return QueryResult(rows)
```

#### パフォーマンス最適化
- **コネクションプーリング**: 既存のBaseDatabase実装を活用
- **クエリキャッシュ**: 同一クエリの結果をキャッシュ
- **EXPLAIN分析**: 遅いクエリを検出してログ記録

---

### 4.4 結果フォーマッター

#### サポートフォーマット
1. **TABLE**: Rich Console Table（CLI用）
2. **JSON**: 構造化データ
3. **CSV**: エクスポート用
4. **MARKDOWN**: ドキュメント埋め込み用

#### 実装例
```python
class ResultFormatterService:
    def format(self, result: QueryResult, format: OutputFormat):
        if format == OutputFormat.TABLE:
            return self._format_table(result)
        elif format == OutputFormat.JSON:
            return json.dumps(result.rows, ensure_ascii=False, indent=2)
        elif format == OutputFormat.CSV:
            return self._format_csv(result)
        elif format == OutputFormat.MARKDOWN:
            return self._format_markdown(result)
```

---

## 5. 設定管理方式

### 5.1 設定ファイル構造

```yaml
# config/config.yaml

# 既存設定（JV-Link, Database）
jvlink:
  service_key: "${JVLINK_SERVICE_KEY}"
  sid: "JLTSQL"

databases:
  sqlite:
    enabled: true
    path: "./data/keiba.db"
  postgresql:
    enabled: false
    host: "${POSTGRES_HOST:localhost}"
    port: 5432
    database: "keiba"
    user: "${POSTGRES_USER:postgres}"
    password: "${POSTGRES_PASSWORD}"

# 新規設定（LLM, Query）
llm:
  # LLMプロバイダー選択
  provider: "ollama"  # ollama | openrouter

  # Ollama設定
  ollama:
    base_url: "http://localhost:11434"
    model: "llama3.2"
    timeout: 60
    options:
      temperature: 0.7
      num_predict: 2000

  # OpenRouter設定
  openrouter:
    api_key: "${OPENROUTER_API_KEY}"
    model: "anthropic/claude-3.5-sonnet"
    timeout: 60
    options:
      temperature: 0.7
      max_tokens: 2000

query:
  # クエリ実行設定
  executor:
    timeout_seconds: 30
    max_rows: 10000
    enable_query_cache: true
    cache_ttl_seconds: 300

  # 結果フォーマット設定
  formatter:
    default_format: "table"  # table | json | csv | markdown
    table_max_width: 120
    json_indent: 2

# ロギング設定（既存）
logging:
  level: "INFO"
  file:
    enabled: true
    path: "./logs/jltsql.log"
  console:
    enabled: true
```

### 5.2 設定クラス拡張

```python
# src/utils/config.py（既存を拡張）

class Config:
    """既存Configクラスに追加メソッド"""

    def get_llm_config(self) -> LLMConfig:
        """LLM設定取得"""
        provider = self.get("llm.provider")

        if provider == "ollama":
            return OllamaConfig(
                base_url=self.get("llm.ollama.base_url"),
                model=self.get("llm.ollama.model"),
                timeout=self.get("llm.ollama.timeout", 60)
            )
        elif provider == "openrouter":
            return OpenRouterConfig(
                api_key=self.get("llm.openrouter.api_key"),
                model=self.get("llm.openrouter.model"),
                timeout=self.get("llm.openrouter.timeout", 60)
            )
        else:
            raise ConfigError(f"Unknown LLM provider: {provider}")

    def get_query_config(self) -> QueryConfig:
        """クエリ設定取得"""
        return QueryConfig(
            timeout_seconds=self.get("query.executor.timeout_seconds", 30),
            max_rows=self.get("query.executor.max_rows", 10000),
            enable_cache=self.get("query.executor.enable_query_cache", True),
            cache_ttl=self.get("query.executor.cache_ttl_seconds", 300),
            default_format=self.get("query.formatter.default_format", "table")
        )
```

### 5.3 環境変数対応

既存の`_expand_env_vars`関数を活用:
```python
# ${VAR}または${VAR:default}の形式をサポート
llm:
  openrouter:
    api_key: "${OPENROUTER_API_KEY}"  # 環境変数から取得
databases:
  postgresql:
    host: "${POSTGRES_HOST:localhost}"  # デフォルト値付き
```

---

## 6. エラーハンドリング戦略

### 6.1 エラー階層

```python
# src/domain/exceptions.py

class JRVLTSQLError(Exception):
    """ベース例外クラス"""
    pass

# Application Layer Errors
class QueryExecutionError(JRVLTSQLError):
    """クエリ実行エラー"""
    pass

class SQLGenerationError(JRVLTSQLError):
    """SQL生成エラー"""
    pass

class QueryValidationError(JRVLTSQLError):
    """クエリ検証エラー"""
    pass

# Infrastructure Layer Errors
class LLMProviderError(JRVLTSQLError):
    """LLMプロバイダーエラー"""
    pass

class DatabaseConnectionError(JRVLTSQLError):
    """DB接続エラー"""
    pass

# Domain Layer Errors
class SchemaNotFoundError(JRVLTSQLError):
    """スキーマ未発見エラー"""
    pass
```

### 6.2 エラーハンドリングパターン

#### Application Layer
```python
class QueryOrchestrator:
    async def execute_natural_query(
        self,
        natural_query: str
    ) -> AnalysisResult:
        try:
            # SQL生成
            sql_result = await self.sql_generator.generate_sql(natural_query)

            if not sql_result.is_valid:
                # ユーザーフレンドリーなエラーメッセージ
                return AnalysisResult.error(
                    f"SQLの生成に失敗しました: {sql_result.error_message}"
                )

            # クエリ実行
            query_result = self.query_executor.execute(sql_result.sql)

            return AnalysisResult.success(...)

        except LLMProviderError as e:
            logger.error("LLM provider error", error=str(e), exc_info=True)
            return AnalysisResult.error(
                f"LLMサービスとの通信に失敗しました。\n"
                f"プロバイダー設定を確認してください。\n"
                f"詳細: {e}"
            )

        except DatabaseError as e:
            logger.error("Database error", error=str(e), exc_info=True)
            return AnalysisResult.error(
                f"データベースエラーが発生しました。\n"
                f"詳細: {e}"
            )

        except Exception as e:
            logger.error("Unexpected error", error=str(e), exc_info=True)
            return AnalysisResult.error(
                f"予期しないエラーが発生しました。\n"
                f"ログファイルを確認してください。"
            )
```

#### Infrastructure Layer（LLM Provider）
```python
class OllamaProvider(LLMProvider):
    async def generate(self, prompt: str) -> LLMResponse:
        try:
            response = await self.client.post(...)

            if response.status_code != 200:
                raise LLMProviderError(
                    f"Ollama API returned status {response.status_code}"
                )

            return LLMResponse(...)

        except httpx.TimeoutException:
            raise LLMProviderError(
                "Ollamaへの接続がタイムアウトしました。\n"
                "Ollamaサーバーが起動しているか確認してください。"
            )

        except httpx.ConnectError:
            raise LLMProviderError(
                "Ollamaサーバーに接続できません。\n"
                "接続先URL: {self.base_url}"
            )
```

### 6.3 リトライロジック

```python
# src/infrastructure/retry.py

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

class SQLGeneratorService:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(LLMProviderError)
    )
    async def generate_sql(self, natural_query: str) -> SQLGenerationResult:
        """
        最大3回リトライ（指数バックオフ: 2秒, 4秒, 8秒）
        LLMProviderErrorの場合のみリトライ
        """
        response = await self.llm_provider.generate(prompt)
        # ...
```

### 6.4 ユーザーフィードバック

```python
# CLI層でのエラー表示
@click.command()
def query(query_text: str):
    result = orchestrator.execute_natural_query(query_text)

    if result.status == ResultStatus.ERROR:
        console.print(
            Panel(
                f"[red]エラー[/red]\n\n{result.error_message}",
                title="クエリ実行失敗",
                border_style="red"
            )
        )
        sys.exit(1)

    # 成功時の処理
    console.print(result.data)
```

---

## 7. ディレクトリ構成

```
jrvltsql/
├── src/
│   ├── cli/
│   │   ├── main.py                    # 既存CLI（拡張）
│   │   └── commands/
│   │       └── query_command.py       # 新規: クエリコマンド
│   │
│   ├── api/                            # 新規: Web API（Optional）
│   │   ├── main.py
│   │   └── routes/
│   │       └── query.py
│   │
│   ├── application/                    # 新規: Application Layer
│   │   ├── query_orchestrator.py
│   │   └── services/
│   │       ├── sql_generator_service.py
│   │       ├── query_executor_service.py
│   │       └── result_formatter_service.py
│   │
│   ├── domain/                         # 新規: Domain Layer
│   │   ├── schema_context.py
│   │   ├── query_validator.py
│   │   ├── analysis_result.py
│   │   └── exceptions.py
│   │
│   ├── infrastructure/                 # 新規: Infrastructure Layer
│   │   ├── llm/
│   │   │   ├── base.py
│   │   │   ├── ollama_provider.py
│   │   │   ├── openrouter_provider.py
│   │   │   └── factory.py
│   │   └── monitoring/
│   │       ├── query_monitor.py
│   │       └── metrics.py
│   │
│   ├── database/                       # 既存（そのまま利用）
│   │   ├── base.py
│   │   ├── sqlite_handler.py
│   │   └── postgresql_handler.py
│   │
│   └── utils/                          # 既存（拡張）
│       ├── config.py                   # LLM設定追加
│       └── logger.py
│
├── config/
│   └── config.yaml                     # LLM設定追加
│
├── tests/
│   ├── unit/
│   │   ├── test_sql_generator.py
│   │   ├── test_query_executor.py
│   │   └── test_llm_providers.py
│   └── integration/
│       └── test_query_orchestrator.py
│
└── docs/
    └── ARCHITECTURE_DESIGN.md          # 本ドキュメント
```

---

## 8. 実装フェーズ

### Phase 1: 基盤構築（Week 1-2）
- [ ] LLMプロバイダー抽象化層実装
  - [ ] `LLMProvider`基底クラス
  - [ ] `OllamaProvider`実装
  - [ ] `OpenRouterProvider`実装
  - [ ] `LLMProviderFactory`実装
- [ ] 設定管理拡張
  - [ ] `config.yaml`にLLM設定追加
  - [ ] `Config`クラスに`get_llm_config()`追加
- [ ] 単体テスト作成

### Phase 2: ドメイン層実装（Week 3）
- [ ] `SchemaContext`実装
  - [ ] キーワード抽出
  - [ ] テーブルマッピング
  - [ ] スキーマ情報取得
- [ ] `QueryValidator`実装
  - [ ] SELECT文チェック
  - [ ] 危険キーワード検出
  - [ ] 構文検証
- [ ] ドメインモデル定義
  - [ ] `AnalysisResult`
  - [ ] `ResultMetadata`
  - [ ] 例外クラス

### Phase 3: アプリケーション層実装（Week 4-5）
- [ ] `SQLGeneratorService`実装
  - [ ] プロンプト構築
  - [ ] LLM呼び出し
  - [ ] SQL抽出・検証
  - [ ] リトライロジック
- [ ] `QueryExecutorService`実装
  - [ ] セーフティチェック
  - [ ] タイムアウト制御
  - [ ] 結果行数制限
- [ ] `ResultFormatterService`実装
  - [ ] TABLE/JSON/CSV/Markdownフォーマット
- [ ] `QueryOrchestrator`実装
  - [ ] 全体フロー制御
  - [ ] エラーハンドリング

### Phase 4: プレゼンテーション層実装（Week 6）
- [ ] CLI拡張
  - [ ] `query`コマンド追加
  - [ ] Rich UI統合
- [ ] Interactive REPL（Optional）
- [ ] Web API（Optional）

### Phase 5: テスト・最適化（Week 7-8）
- [ ] 統合テスト
- [ ] E2Eテスト
- [ ] パフォーマンス最適化
- [ ] ドキュメント整備

---

## 9. 使用例

### 9.1 CLI使用例

```bash
# 基本的なクエリ実行
$ jrvltsql query "2024年の東京競馬場で開催されたレース一覧を取得"

# フォーマット指定
$ jrvltsql query "ディープインパクト産駒の勝率" --format json

# LLMプロバイダー指定
$ jrvltsql query "先週の重賞レース結果" --llm openrouter

# パイプライン処理
$ echo "2024年のG1レース一覧" | jrvltsql query --format csv > g1_races.csv
```

### 9.2 Python API使用例

```python
from src.application.query_orchestrator import QueryOrchestrator
from src.infrastructure.llm.factory import LLMProviderFactory
from src.database.sqlite_handler import SQLiteDatabase
from src.utils.config import load_config

# 初期化
config = load_config()
database = SQLiteDatabase(config.get("databases.sqlite"))
llm_provider = LLMProviderFactory.create(config)

orchestrator = QueryOrchestrator(
    sql_generator=SQLGeneratorService(llm_provider, schema_context),
    query_executor=QueryExecutorService(database),
    result_formatter=ResultFormatterService()
)

# クエリ実行
result = await orchestrator.execute_natural_query(
    "2024年の東京競馬場で開催されたレース一覧"
)

if result.status == ResultStatus.SUCCESS:
    print(f"SQL: {result.sql}")
    print(f"結果: {result.data}")
    print(f"実行時間: {result.metadata.execution_time_ms}ms")
else:
    print(f"エラー: {result.error_message}")
```

---

## 10. パフォーマンス考慮事項

### 10.1 LLM呼び出し最適化
- **キャッシング**: 同一クエリの結果をキャッシュ
- **ストリーミング**: 長時間応答時の進捗表示
- **タイムアウト**: 適切なタイムアウト設定（60秒）

### 10.2 データベースクエリ最適化
- **コネクションプーリング**: 既存実装を活用
- **クエリキャッシュ**: Redis等でクエリ結果キャッシュ
- **EXPLAIN分析**: 遅いクエリの検出・ログ記録

### 10.3 メモリ管理
- **結果行数制限**: デフォルト10,000行
- **ストリーミング処理**: 大量データ時はイテレーター使用

---

## 11. セキュリティ考慮事項

### 11.1 SQLインジェクション対策
- **READ ONLY強制**: SELECT文のみ許可
- **危険キーワード検出**: DROP, DELETE等を拒否
- **パラメータ化クエリ**: バインド変数使用

### 11.2 API認証（Web API使用時）
- **API Key認証**: エンドポイント保護
- **Rate Limiting**: 過剰リクエスト防止

### 11.3 機密情報保護
- **環境変数**: API Keyは環境変数管理
- **ログマスキング**: 機密情報をログに出力しない

---

## 12. まとめ

本アーキテクチャ設計は以下の特徴を持ちます:

### 12.1 設計原則
- **レイヤー分離**: 明確な責務分離
- **依存性注入**: テスト可能性・拡張性確保
- **抽象化**: LLMプロバイダー等を抽象化

### 12.2 拡張性
- 新しいLLMプロバイダーの追加が容易
- 新しい出力フォーマットの追加が容易
- Web APIへの拡張が容易

### 12.3 保守性
- 既存コード（Database層）を活用
- 明確なエラーハンドリング
- 包括的なロギング

### 12.4 パフォーマンス
- 非同期処理対応
- キャッシング戦略
- 適切なタイムアウト・制限

---

## 付録A: 参考実装例

### A.1 完全な実行フロー例

```python
# src/cli/commands/query_command.py

import click
from rich.console import Console
from rich.panel import Panel

from src.application.query_orchestrator import QueryOrchestrator
from src.application.services.sql_generator_service import SQLGeneratorService
from src.application.services.query_executor_service import QueryExecutorService
from src.application.services.result_formatter_service import ResultFormatterService
from src.domain.schema_context import SchemaContext
from src.domain.query_validator import QueryValidator
from src.infrastructure.llm.factory import LLMProviderFactory
from src.database.sqlite_handler import SQLiteDatabase
from src.database.postgresql_handler import PostgreSQLDatabase
from src.utils.config import load_config

console = Console()

@click.command()
@click.argument("query_text", type=str)
@click.option(
    "--format",
    type=click.Choice(["table", "json", "csv", "markdown"]),
    default="table",
    help="出力フォーマット"
)
@click.option(
    "--llm",
    type=click.Choice(["ollama", "openrouter"]),
    default=None,
    help="LLMプロバイダー（設定ファイルをオーバーライド）"
)
@click.option(
    "--db",
    type=click.Choice(["sqlite", "postgresql"]),
    default=None,
    help="データベースタイプ"
)
@click.option(
    "--explain",
    is_flag=True,
    help="生成されたSQLを表示"
)
@click.pass_context
def query(ctx, query_text: str, format: str, llm: str, db: str, explain: bool):
    """自然言語でデータベースにクエリを実行

    例:
        jrvltsql query "2024年の東京競馬場のレース一覧"
        jrvltsql query "ディープインパクト産駒の勝率" --format json
    """

    # 設定読み込み
    config = ctx.obj.get("config")
    if not config:
        console.print("[red]設定ファイルが見つかりません[/red]")
        return

    # LLMプロバイダーオーバーライド
    if llm:
        config._config["llm"]["provider"] = llm

    # データベースタイプ決定
    db_type = db or config.get("database.type", "sqlite")

    console.print(
        Panel(
            f"[cyan]クエリ:[/cyan] {query_text}\n"
            f"[dim]LLM:[/dim] {config.get('llm.provider')}\n"
            f"[dim]DB:[/dim] {db_type}",
            title="競馬データ分析",
            border_style="cyan"
        )
    )

    try:
        # データベース初期化
        if db_type == "sqlite":
            database = SQLiteDatabase(config.get("databases.sqlite"))
        else:
            database = PostgreSQLDatabase(config.get("databases.postgresql"))

        with database:
            # コンポーネント構築
            llm_provider = LLMProviderFactory.create(config)
            schema_context = SchemaContext(database)
            query_validator = QueryValidator()

            sql_generator = SQLGeneratorService(llm_provider, schema_context)
            query_executor = QueryExecutorService(
                database,
                query_validator,
                config.get_query_config()
            )
            result_formatter = ResultFormatterService()

            orchestrator = QueryOrchestrator(
                sql_generator,
                query_executor,
                result_formatter
            )

            # クエリ実行
            console.print("[cyan]SQL生成中...[/cyan]")

            import asyncio
            result = asyncio.run(
                orchestrator.execute_natural_query(query_text, format)
            )

            # 結果表示
            if result.status == ResultStatus.SUCCESS:
                if explain:
                    console.print(
                        Panel(
                            f"```sql\n{result.sql}\n```",
                            title="生成されたSQL",
                            border_style="green"
                        )
                    )

                console.print(result.data)
                console.print(
                    f"\n[dim]{result.metadata.row_count}行取得 "
                    f"({result.metadata.execution_time_ms:.2f}ms)[/dim]"
                )
            else:
                console.print(
                    Panel(
                        f"[red]{result.error_message}[/red]",
                        title="エラー",
                        border_style="red"
                    )
                )
                sys.exit(1)

    except Exception as e:
        console.print(
            Panel(
                f"[red]予期しないエラー:[/red]\n{e}",
                title="エラー",
                border_style="red"
            )
        )
        sys.exit(1)
```

---

## 付録B: 設定ファイル完全版

```yaml
# config/config.yaml

# JV-Link設定（既存）
jvlink:
  service_key: "${JVLINK_SERVICE_KEY}"
  sid: "JLTSQL"

# データベース設定（既存）
databases:
  sqlite:
    enabled: true
    path: "./data/keiba.db"
    timeout: 30
    pragma:
      journal_mode: "WAL"
      synchronous: "NORMAL"

  postgresql:
    enabled: false
    host: "${POSTGRES_HOST:localhost}"
    port: 5432
    database: "keiba"
    user: "${POSTGRES_USER:postgres}"
    password: "${POSTGRES_PASSWORD}"
    sslmode: "prefer"
    connect_timeout: 10

# データベースタイプ選択
database:
  type: "sqlite"  # sqlite | postgresql

# LLM設定（新規）
llm:
  # プロバイダー選択
  provider: "ollama"  # ollama | openrouter

  # Ollama設定
  ollama:
    base_url: "http://localhost:11434"
    model: "llama3.2"  # llama3.2, codellama, mistral等
    timeout: 60
    options:
      temperature: 0.7
      num_predict: 2000
      top_p: 0.9

  # OpenRouter設定
  openrouter:
    api_key: "${OPENROUTER_API_KEY}"
    model: "anthropic/claude-3.5-sonnet"
    # その他選択可能モデル:
    # - "anthropic/claude-3-opus"
    # - "openai/gpt-4"
    # - "google/gemini-pro"
    timeout: 60
    options:
      temperature: 0.7
      max_tokens: 2000

# クエリ設定（新規）
query:
  # SQL生成設定
  generator:
    max_retries: 3
    enable_few_shot: true  # Few-shot learning有効化
    sample_queries_path: "./config/sample_queries.yaml"

  # クエリ実行設定
  executor:
    timeout_seconds: 30
    max_rows: 10000
    enable_query_cache: true
    cache_ttl_seconds: 300
    enable_explain: false  # EXPLAIN実行（デバッグ用）

  # 結果フォーマット設定
  formatter:
    default_format: "table"
    table_max_width: 120
    table_max_rows: 100
    json_indent: 2
    csv_delimiter: ","

# ロギング設定（既存）
logging:
  level: "INFO"
  file:
    enabled: true
    path: "./logs/jltsql.log"
    max_bytes: 10485760  # 10MB
    backup_count: 5
  console:
    enabled: true

# パフォーマンス設定（既存）
performance:
  batch_size: 1000
  commit_interval: 10000
  max_workers: 4
```

---

以上が競馬データ分析アプリケーションの包括的なアーキテクチャ設計書です。
