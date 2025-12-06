# LLM統合設計 - 概要

## ドキュメント構成

1. **llm_integration_design.md** (1,985行) - 完全な設計書
2. **llm_integration_interfaces.py** - Pythonインターフェース定義
3. **LLM_INTEGRATION_SUMMARY.md** (このファイル) - クイックリファレンス

---

## クイックスタート

### 1. ローカルLLM（Ollama）でのセットアップ

```bash
# Ollamaインストール
# https://ollama.ai/download

# 推奨モデルのダウンロード
ollama pull deepseek-coder:6.7b-instruct

# Ollama起動
ollama serve
```

### 2. 設定ファイル（config/config.yaml）

```yaml
llm:
  provider: "ollama"
  model: "deepseek-coder:6.7b-instruct"
  temperature: 0.1
  max_tokens: 1000
  timeout: 30

  ollama:
    base_url: "http://localhost:11434"
```

### 3. 使用例

```bash
# 基本的なクエリ
jltsql query "2024年のGⅠレースを全て表示して"

# SQL表示
jltsql query "武豊騎手の勝率を教えて" --show-sql

# Dry run（SQLのみ生成）
jltsql query "3連単の最高配当は?" --dry-run
```

---

## アーキテクチャ概要

```
┌─────────────────────┐
│   CLI Interface     │  jltsql query "..."
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Query Handler     │  自然言語クエリ受付・結果表示
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Provider Factory   │  プロバイダー選択・初期化
└────┬────────────┬───┘
     │            │
     ▼            ▼
┌─────────┐  ┌─────────────┐
│ Ollama  │  │ OpenRouter  │  LLM API呼び出し
└────┬────┘  └──────┬──────┘
     │              │
     └──────┬───────┘
            ▼
┌─────────────────────┐
│ Prompt Engineering  │  システムプロンプト + Few-shot
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Response Processing │  SQL抽出・バリデーション
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Database Execution  │  SQLクエリ実行
└─────────────────────┘
```

---

## 主要コンポーネント

### 1. LLMプロバイダー抽象化

**ファイル**: `src/llm/base.py`

```python
from src.llm.factory import LLMProviderFactory, LLMConfig, LLMProviderType

config = LLMConfig(
    provider=LLMProviderType.OLLAMA,
    model="codellama:13b-instruct"
)
provider = LLMProviderFactory.create(config)
```

**サポート対象**:
- Ollama (ローカルLLM)
- OpenRouter (クラウドAPI)

### 2. プロンプトエンジニアリング

**ファイル**: `src/llm/prompt.py`

- システムプロンプト: 競馬DBスキーマ + SQLルール
- Few-shot examples: 6つの代表的クエリ例
- 動的スキーマ埋め込み

### 3. SQL抽出・バリデーション

**ファイル**: `src/llm/parser.py`, `src/llm/validator.py`

```python
from src.llm.parser import extract_sql, clean_sql
from src.llm.validator import validate_sql, add_safety_limits

# LLM応答からSQL抽出
sql = extract_sql(response.content)
sql = clean_sql(sql)

# 安全性チェック
is_valid, error = validate_sql(sql, strict=True)

# LIMIT句追加
sql = add_safety_limits(sql, max_rows=1000)
```

**バリデーション**:
- SELECT以外のクエリを拒否
- テーブル名ホワイトリスト
- SQLインジェクション対策
- 結果行数制限

### 4. エラーハンドリング

**ファイル**: `src/llm/error_handler.py`

```python
from src.llm.error_handler import QueryError, handle_query_error

try:
    # クエリ処理
    pass
except QueryError as e:
    error_msg = handle_query_error(e, user_query)
    print(error_msg)
```

---

## 推奨モデル

### ローカルLLM（Ollama）

| モデル | メモリ | 速度 | 精度 | 推奨用途 |
|--------|--------|------|------|----------|
| **deepseek-coder:6.7b-instruct** | 8GB | 高速 | 高 | 最推奨 |
| **codellama:13b-instruct** | 16GB | 中速 | 非常に高 | 高精度 |
| **sqlcoder:15b** | 32GB | 低速 | 最高 | SQL特化 |
| **mistral:7b-instruct-v0.2** | 8GB | 高速 | 良 | 汎用 |

### OpenRouter（クラウドAPI）

| モデル | 料金/1M tokens | 推奨用途 |
|--------|----------------|----------|
| **google/gemini-pro-1.5** | $0.50 | バランス型（推奨） |
| **anthropic/claude-3-haiku** | $0.25 | 高速・低コスト |
| **deepseek/deepseek-coder-33b-instruct** | $0.14 | 最安値 |
| **anthropic/claude-3-sonnet** | $3.00 | 高精度 |

---

## ディレクトリ構成

```
src/llm/
├── __init__.py
├── base.py            # BaseLLMProvider, LLMConfig, LLMMessage
├── ollama.py          # OllamaProvider実装
├── openrouter.py      # OpenRouterProvider実装
├── factory.py         # LLMProviderFactory
├── prompt.py          # SYSTEM_PROMPT, build_prompt
├── parser.py          # extract_sql, clean_sql
├── validator.py       # validate_sql, add_safety_limits
└── error_handler.py   # QueryError, handle_query_error
```

---

## 実装チェックリスト

### Phase 1: 基盤実装

- [ ] `src/llm/base.py` - 抽象インターフェース
- [ ] `src/llm/factory.py` - ファクトリーパターン
- [ ] `src/llm/prompt.py` - プロンプトテンプレート
- [ ] `src/llm/parser.py` - SQL抽出ロジック
- [ ] `src/llm/validator.py` - バリデーション

### Phase 2: プロバイダー実装

- [ ] `src/llm/ollama.py` - Ollama統合
- [ ] `src/llm/openrouter.py` - OpenRouter統合
- [ ] `src/llm/error_handler.py` - エラーハンドリング

### Phase 3: CLI統合

- [ ] `src/cli/main.py` - `jltsql query` コマンド追加
- [ ] Rich表示（テーブル、シンタックスハイライト）
- [ ] `--show-sql`, `--dry-run`, `--explain` オプション

### Phase 4: テスト

- [ ] 単体テスト（`tests/test_llm_*.py`）
- [ ] 統合テスト（End-to-End）
- [ ] パフォーマンステスト

### Phase 5: ドキュメント

- [ ] ユーザーガイド
- [ ] API リファレンス
- [ ] トラブルシューティング

---

## 設定例

### Ollama設定

```yaml
llm:
  provider: "ollama"
  model: "deepseek-coder:6.7b-instruct"
  temperature: 0.1
  max_tokens: 1000
  timeout: 30

  ollama:
    base_url: "http://localhost:11434"

  prompt:
    include_examples: true
    max_examples: 6

  validation:
    strict_mode: true
    max_result_rows: 1000
```

### OpenRouter設定

```yaml
llm:
  provider: "openrouter"
  model: "google/gemini-pro-1.5"
  temperature: 0.1
  max_tokens: 1000
  timeout: 30

  openrouter:
    api_key: "${OPENROUTER_API_KEY}"  # 環境変数から読み込み
    base_url: "https://openrouter.ai/api/v1"

  prompt:
    include_examples: true
    max_examples: 6

  validation:
    strict_mode: true
    max_result_rows: 1000
```

---

## クエリ例

### 基本クエリ

```bash
jltsql query "2024年のGⅠレースを全て表示して"
jltsql query "武豊騎手の2023年の勝利数と勝率を教えて"
jltsql query "東京競馬場の芝2000mで行われたレースの平均タイムは?"
```

### オプション付きクエリ

```bash
# SQL表示
jltsql query "直近10レースの単勝1番人気の勝率" --show-sql

# Dry run（SQLのみ生成、実行しない）
jltsql query "3連単の最高配当トップ10" --dry-run

# プロバイダー指定
jltsql query "ディープインパクト産駒のGⅠ勝利数" --provider openrouter
```

---

## パフォーマンス最適化

### キャッシュ設定

```yaml
llm:
  cache:
    enabled: true
    ttl: 3600  # 1時間
    max_entries: 1000
```

### バッチ処理

```yaml
llm:
  batch:
    enabled: true
    max_batch_size: 10
```

### リトライ設定

```yaml
llm:
  retry:
    max_attempts: 3
    backoff_factor: 2
```

---

## トラブルシューティング

### Ollamaが起動しない

```bash
# Ollamaプロセス確認
ollama list

# Ollama起動
ollama serve

# モデル確認
ollama list
```

### OpenRouter API エラー

```bash
# API キー確認
echo $OPENROUTER_API_KEY

# API キー設定
export OPENROUTER_API_KEY="sk-or-v1-..."
```

### SQLバリデーションエラー

```bash
# 詳細ログ確認
jltsql query "..." --verbose

# Dry runでSQLのみ確認
jltsql query "..." --dry-run --show-sql
```

---

## コスト試算

### OpenRouter使用時（月間1,000クエリ）

| モデル | 平均tokens/query | 月間コスト | 用途 |
|--------|------------------|------------|------|
| google/gemini-pro-1.5 | 500 | $0.25 | 推奨 |
| anthropic/claude-3-haiku | 500 | $0.13 | 低コスト |
| deepseek/deepseek-coder-33b-instruct | 500 | $0.07 | 最安値 |
| anthropic/claude-3-sonnet | 500 | $1.50 | 高精度 |

---

## 次のステップ

1. **ローカル開発環境セットアップ**
   - Ollamaインストール
   - DeepSeek-Coder 6.7B モデルダウンロード
   - テストクエリ実行

2. **基盤実装**
   - `src/llm/base.py` から実装開始
   - 単体テスト作成
   - CLIコマンド統合

3. **本番環境セットアップ**
   - OpenRouter API キー取得
   - 設定ファイル更新
   - パフォーマンステスト

---

## 参考リンク

- **設計書詳細**: [llm_integration_design.md](./llm_integration_design.md)
- **インターフェース定義**: [llm_integration_interfaces.py](./llm_integration_interfaces.py)
- **Ollama**: https://ollama.ai
- **OpenRouter**: https://openrouter.ai
- **DeepSeek-Coder**: https://github.com/deepseek-ai/DeepSeek-Coder
- **CodeLlama**: https://github.com/facebookresearch/codellama

---

## ライセンス

Apache License 2.0 - JRVLTSQLプロジェクトと同一
