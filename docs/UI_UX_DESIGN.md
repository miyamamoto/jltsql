# JRVLTSQL UI/UX設計書

## 1. プロジェクト概要

### 1.1 アプリケーション概要
- **名称**: JRVLTSQL - JRA-VAN Link To SQL
- **目的**: 競馬データを自然言語で分析できるCLIツール（将来的にGUI対応）
- **ターゲットユーザー**:
  - データアナリスト（SQL知識：中〜高）
  - 競馬データサイエンティスト
  - 馬券分析を行う個人ユーザー

### 1.2 コア機能
1. 自然言語からSQL生成（LLM活用）
2. 複数データベース対応（SQLite/PostgreSQL）
3. インタラクティブ/バッチ実行モード
4. 結果の可視化（テーブル/JSON/グラフ）

---

## 2. CLIインターフェース設計

### 2.1 コマンド体系

#### メインコマンド構造
```
jrvltsql
├── init              # プロジェクト初期化
├── config            # 設定管理
│   ├── --show
│   ├── --get <key>
│   └── --set <key>=<value>
├── query             # 【NEW】自然言語クエリ（メイン機能）
│   ├── --interactive (-i)
│   ├── --question (-q) <text>
│   ├── --llm <provider>
│   ├── --output (-o) <format>
│   ├── --save <filename>
│   └── --history
├── data              # データ管理グループ
│   ├── fetch
│   ├── export
│   ├── import
│   └── stats
├── db                # データベース管理グループ
│   ├── create-tables
│   ├── create-indexes
│   ├── migrate
│   └── backup
├── realtime          # リアルタイム監視
│   ├── start
│   ├── stop
│   ├── status
│   └── specs
└── llm               # 【NEW】LLM設定グループ
    ├── setup
    ├── list
    ├── test
    └── config
```

---

### 2.2 新規コマンド詳細設計

#### 2.2.1 `jrvltsql query` - 自然言語クエリ

**基本構文:**
```bash
jrvltsql query [OPTIONS] [QUESTION]
```

**オプション:**

| オプション | 短縮形 | 説明 | デフォルト |
|-----------|-------|------|-----------|
| `--interactive` | `-i` | インタラクティブモード起動 | False |
| `--question` | `-q` | 質問文を直接指定 | - |
| `--llm` | - | LLMプロバイダー選択 (openai/anthropic/local) | config.yaml |
| `--output` | `-o` | 出力形式 (table/json/csv) | table |
| `--save` | `-s` | 結果を保存 | - |
| `--explain` | `-e` | 生成されたSQLを表示 | False |
| `--dry-run` | - | SQL実行せずに表示のみ | False |
| `--limit` | `-l` | 結果の行数制限 | 100 |
| `--history` | - | クエリ履歴を表示 | False |

**使用例:**

```bash
# インタラクティブモード
jrvltsql query -i

# 直接質問（ワンショット）
jrvltsql query -q "2024年の東京競馬場での勝率トップ10の騎手は？"

# 出力形式指定
jrvltsql query -q "先週のG1レース結果" -o json

# SQL表示 + 実行
jrvltsql query -q "武豊騎手の2024年成績" --explain

# DRYランモード（SQL生成のみ）
jrvltsql query -q "先月の払戻金ランキング" --dry-run

# 結果をファイル保存
jrvltsql query -q "全騎手の年間勝率" -o csv --save results.csv

# 履歴表示
jrvltsql query --history
```

---

#### 2.2.2 `jrvltsql llm` - LLM設定管理

**サブコマンド:**

##### `jrvltsql llm setup`
LLMプロバイダーの初期設定ウィザード

```bash
jrvltsql llm setup

# 対話形式での設定
[?] LLMプロバイダーを選択してください:
  > OpenAI (ChatGPT)
    Anthropic (Claude)
    Local (Ollama/LM Studio)

[?] APIキーを入力してください: *********************

[?] 使用するモデルを選択してください:
  > gpt-4-turbo
    gpt-3.5-turbo
    claude-3-opus
    claude-3-sonnet

[OK] LLM設定が完了しました
     Provider: OpenAI
     Model: gpt-4-turbo
     設定ファイル: config/config.yaml
```

##### `jrvltsql llm list`
利用可能なLLMプロバイダー一覧

```bash
jrvltsql llm list

Available LLM Providers:
  OpenAI
    - gpt-4-turbo (推奨)
    - gpt-4
    - gpt-3.5-turbo

  Anthropic
    - claude-3-opus-20240229
    - claude-3-sonnet-20240229

  Local
    - ollama (llama3, mistral, etc.)
    - lm-studio
```

##### `jrvltsql llm test`
LLM接続テスト

```bash
jrvltsql llm test

Testing LLM Connection...
  Provider: OpenAI
  Model: gpt-4-turbo

[OK] Connection successful!
Response time: 1.2s
Test query: "SELECT COUNT(*) FROM NL_RA" -> Generated correctly
```

##### `jrvltsql llm config`
現在のLLM設定表示

```bash
jrvltsql llm config

Current LLM Configuration:
  Provider:    OpenAI
  Model:       gpt-4-turbo
  API Key:     sk-proj-****...****  (masked)
  Max Tokens:  4096
  Temperature: 0.1
  Timeout:     30s
```

---

## 3. ユーザーフロー

### 3.1 初回セットアップフロー

```
┌─────────────────────────────────────────┐
│ 1. プロジェクト初期化                      │
│    $ jrvltsql init                       │
│    → ディレクトリ作成、設定ファイル生成      │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 2. JV-Link設定                           │
│    config/config.yaml を編集              │
│    service_key: "XXXX-XXXX-..."         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 3. LLM設定                               │
│    $ jrvltsql llm setup                  │
│    → OpenAI/Anthropic/Localを選択       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 4. データベースセットアップ                │
│    $ jrvltsql db create-tables           │
│    $ jrvltsql db create-indexes          │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 5. データ取得                             │
│    $ python scripts/quickstart.py        │
│    → 過去データ一括取得（自動）            │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 6. 準備完了                               │
│    $ jrvltsql query -i                   │
│    → 自然言語で質問開始                   │
└─────────────────────────────────────────┘
```

---

### 3.2 質問→回答フロー（インタラクティブモード）

```
┌─────────────────────────────────────────┐
│ $ jrvltsql query -i                      │
│                                          │
│ JRVLTSQL Interactive Query Shell         │
│ Version: 0.2.0                           │
│ Database: SQLite (data/keiba.db)         │
│ LLM: OpenAI gpt-4-turbo                  │
│                                          │
│ Type your question or '/help' for help   │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ 🔍 > 2024年の中山競馬場での勝率トップ5の  │
│      騎手は？                             │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 🤖 Generating SQL...                     │
│ [■■■■■■■■■■] 100% (1.2s)              │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 📝 Generated SQL:                        │
│ ─────────────────────────────────────── │
│ SELECT                                   │
│   騎手名,                                 │
│   COUNT(CASE WHEN 着順 = 1 THEN 1 END) * │
│     100.0 / COUNT(*) AS 勝率,            │
│   COUNT(*) AS 騎乗数,                     │
│   COUNT(CASE WHEN 着順 = 1 THEN 1 END)   │
│     AS 勝利数                             │
│ FROM NL_SE se                            │
│ JOIN NL_RA ra ON se.開催年月日 =         │
│   ra.開催年月日 AND se.競馬場コード =      │
│   ra.競馬場コード                         │
│ WHERE ra.開催年月日 >= 20240101          │
│   AND ra.開催年月日 <= 20241231          │
│   AND ra.競馬場コード = '06'             │
│ GROUP BY 騎手名                          │
│ HAVING COUNT(*) >= 10                    │
│ ORDER BY 勝率 DESC                       │
│ LIMIT 5;                                 │
│ ─────────────────────────────────────── │
│                                          │
│ Execute this query? [Y/n/e/m]            │
│   Y: Yes, execute                        │
│   n: No, cancel                          │
│   e: Edit SQL manually                   │
│   m: Modify question                     │
└─────────────────┬───────────────────────┘
                  │ (User: Y)
                  ▼
┌─────────────────────────────────────────┐
│ ⚙️  Executing query...                   │
│ [■■■■■■■■■■] 100%                      │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ ✅ Query Results (5 rows, 0.05s)         │
│ ─────────────────────────────────────── │
│ ┌─────────┬────────┬──────┬────────┐    │
│ │ 騎手名   │ 勝率   │ 騎乗数│ 勝利数 │    │
│ ├─────────┼────────┼──────┼────────┤    │
│ │ 武豊     │ 25.4   │  118 │   30   │    │
│ │ ルメール │ 22.8   │  114 │   26   │    │
│ │ 横山武史 │ 19.3   │  135 │   26   │    │
│ │ 川田将雅 │ 18.9   │   95 │   18   │    │
│ │ 福永祐一 │ 17.2   │  116 │   20   │    │
│ └─────────┴────────┴──────┴────────┘    │
│                                          │
│ 💡 Insight: 武豊騎手が2024年の中山競馬場で  │
│   最高勝率25.4%を記録しています             │
│                                          │
│ Options:                                 │
│   [s] Save results                       │
│   [g] Generate chart                     │
│   [f] Follow-up question                 │
│   [h] Show query history                 │
│   [q] Back to prompt                     │
└─────────────────────────────────────────┘
```

---

### 3.3 エラー時のフロー

#### Case 1: SQL生成エラー

```
🔍 > 昨日のレース結果を教えて

🤖 Generating SQL...
❌ Error: Insufficient context

LLMが適切なSQLを生成できませんでした。

Suggestions:
  1. より具体的に質問してください
     例: "2024年12月15日の東京競馬場のレース結果"

  2. データベースに必要なデータが存在するか確認してください
     $ jrvltsql data stats

  3. 質問例を参照してください
     /examples
```

#### Case 2: SQL実行エラー

```
⚙️  Executing query...

❌ SQL Execution Error
   Error: no such column: 勝率

   Original SQL:
   SELECT 騎手名, 勝率 FROM NL_SE ...

   Possible causes:
   - Column name mismatch
   - Table schema changed

   Actions:
   [r] Retry SQL generation
   [e] Edit SQL manually
   [s] Show table schema
   [q] Cancel
```

#### Case 3: データ不足エラー

```
✅ Query executed successfully
⚠️  Warning: No data found

The query returned 0 rows.

Possible reasons:
  1. データ期間が設定されていません
     → jrvltsql data fetch --help

  2. 指定した条件に合致するデータがありません
     → Try: jrvltsql data stats --table NL_RA

  3. リアルタイムデータが必要な場合
     → jrvltsql realtime start
```

---

## 4. 出力フォーマット設計

### 4.1 テーブル形式（デフォルト）

```
✅ Query Results (5 rows, 0.05s)
─────────────────────────────────────────────────────────────
┌────┬────────────┬────────┬──────┬────────┬─────────┐
│ No │ 騎手名      │ 勝率   │ 騎乗数│ 勝利数 │ 連対率  │
├────┼────────────┼────────┼──────┼────────┼─────────┤
│  1 │ 武豊        │  25.4% │  118 │   30   │  42.3%  │
│  2 │ ルメール    │  22.8% │  114 │   26   │  39.5%  │
│  3 │ 横山武史    │  19.3% │  135 │   26   │  35.6%  │
│  4 │ 川田将雅    │  18.9% │   95 │   18   │  36.8%  │
│  5 │ 福永祐一    │  17.2% │  116 │   20   │  33.6%  │
└────┴────────────┴────────┴──────┴────────┴─────────┘

💡 Summary: Top 5 jockeys by win rate in 2024
   Highest win rate: 武豊 (25.4%)
   Total races analyzed: 578
```

**特徴:**
- 行番号付き
- カラムの自動幅調整
- パーセンテージは自動フォーマット
- 日本語対応（全角文字の幅調整）
- 要約コメント付き

---

### 4.2 JSON形式

```bash
jrvltsql query -q "騎手別勝率TOP5" -o json

# 出力
{
  "query": "騎手別勝率TOP5",
  "sql": "SELECT 騎手名, COUNT(*) AS 勝利数 ...",
  "execution_time": 0.052,
  "row_count": 5,
  "timestamp": "2024-12-15T10:30:45+09:00",
  "results": [
    {
      "騎手名": "武豊",
      "勝率": 25.4,
      "騎乗数": 118,
      "勝利数": 30,
      "連対率": 42.3
    },
    {
      "騎手名": "ルメール",
      "勝率": 22.8,
      "騎乗数": 114,
      "勝利数": 26,
      "連対率": 39.5
    }
    ...
  ],
  "metadata": {
    "database": "SQLite",
    "llm_provider": "OpenAI",
    "model": "gpt-4-turbo"
  }
}
```

**用途:**
- 他システムとの連携
- データパイプライン
- APIレスポンス

---

### 4.3 CSV形式

```bash
jrvltsql query -q "騎手別勝率TOP5" -o csv --save results.csv

# results.csv
騎手名,勝率,騎乗数,勝利数,連対率
武豊,25.4,118,30,42.3
ルメール,22.8,114,26,39.5
横山武史,19.3,135,26,35.6
川田将雅,18.9,95,18,36.8
福永祐一,17.2,116,20,33.6

✅ Results saved to: results.csv (5 rows)
```

**用途:**
- Excel分析
- データ共有
- バックアップ

---

### 4.4 グラフ/チャート形式

#### ASCII Art（CLI標準）

```bash
jrvltsql query -q "騎手別勝率TOP5" -o chart

騎手別勝率 TOP 5 (2024年中山競馬場)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

武豊      ████████████████████████▌ 25.4%
ルメール  ██████████████████████▊ 22.8%
横山武史  ███████████████████▎ 19.3%
川田将雅  ██████████████████▉ 18.9%
福永祐一  █████████████████▏ 17.2%

         0%    5%    10%   15%   20%   25%   30%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Races: 578 | Avg Win Rate: 20.7%
```

#### 画像出力（将来実装）

```bash
jrvltsql query -q "月別騎乗数推移" -o png --save chart.png

📊 Generating chart... Done!
✅ Chart saved to: chart.png

Options:
  [v] View chart
  [e] Edit chart settings
```

---

## 5. UX考慮事項

### 5.1 プログレス表示

#### LLM応答待ち

```
🤖 Analyzing your question...
   [████████░░░░░░░░░░░░] 40% | Understanding context...

🤖 Analyzing your question...
   [████████████████░░░░] 80% | Generating SQL...

🤖 Analyzing your question...
   [████████████████████] 100% | Complete! (2.3s)
```

#### データベースクエリ実行

```
⚙️  Executing query...
   [████████████████████] 100%

   Rows scanned: 15,234
   Rows returned: 50
   Execution time: 0.15s
```

#### 大量データ取得

```
📥 Fetching historical data...

   ┌─────────────────────────────────────┐
   │ Data Spec: RACE                     │
   │ Period: 2020-01-01 to 2024-12-31   │
   │ Progress: [██████░░░░] 60%         │
   │                                     │
   │ Downloaded: 45,231 / 75,000 records│
   │ Speed: 125 records/sec             │
   │ ETA: 4m 15s                        │
   └─────────────────────────────────────┘
```

---

### 5.2 ヘルプ・例文表示

#### インラインヘルプ

```
$ jrvltsql query -i

🔍 > /help

Available Commands:
  /help          - Show this help message
  /examples      - Show example questions
  /history       - Show query history
  /clear         - Clear screen
  /schema [table]- Show table schema
  /exit          - Exit interactive mode

Question Tips:
  - Be specific about dates and venues
  - Use jockey/horse names in Japanese
  - Mention specific race conditions

Examples:
  > 2024年のG1レース一覧
  > 武豊騎手の中山競馬場での勝率
  > 先週の3連単の最高配当
```

#### 例文集

```
$ jrvltsql query -i

🔍 > /examples

Example Questions by Category:

【基本的な集計】
  ✓ 2024年の東京競馬場のレース数は？
  ✓ 全騎手の総騎乗数ランキング
  ✓ 競馬場別のレース開催日数

【騎手分析】
  ✓ 武豊騎手の2024年成績
  ✓ 勝率トップ10の騎手（最低50騎乗）
  ✓ 騎手別の連対率と複勝率

【馬分析】
  ✓ ディープインパクト産駒の成績
  ✓ 3歳馬の勝率ランキング
  ✓ 芝とダートでの成績比較

【配当分析】
  ✓ 2024年の3連単最高配当TOP10
  ✓ 平均配当額の高い競馬場
  ✓ 万馬券の出現率

【時系列分析】
  ✓ 月別のレース開催数推移
  ✓ 年度別の平均配当額
  ✓ 騎手の勝率の年次変化

Try typing any of these questions!
```

---

### 5.3 履歴機能

#### クエリ履歴の表示

```
$ jrvltsql query --history

Query History (Last 10 queries)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 [1] 2024-12-15 10:30:45
     Q: 2024年の騎手別勝率TOP10
     Status: ✅ Success (0.05s, 10 rows)

 [2] 2024-12-15 10:25:12
     Q: 武豊騎手の中山競馬場での成績
     Status: ✅ Success (0.03s, 5 rows)

 [3] 2024-12-15 10:18:33
     Q: 先週のG1レース結果
     Status: ⚠️  No data (0.02s, 0 rows)

 [4] 2024-12-15 10:12:01
     Q: 昨日のレース結果
     Status: ❌ Error (SQL generation failed)

Commands:
  [number]  - Re-run query (e.g., '1')
  [s]       - Show SQL for query
  [c]       - Copy query to clipboard
  [d]       - Delete query from history
  [q]       - Back to prompt
```

#### 履歴から再実行

```
🔍 > /history

Select query to re-run:
 [1] 2024年の騎手別勝率TOP10
 [2] 武豊騎手の中山競馬場での成績
 [3] 先週のG1レース結果

🔍 > 1

Re-running query: "2024年の騎手別勝率TOP10"
🤖 Using cached SQL...
⚙️  Executing query...

✅ Query Results (10 rows, 0.04s)
...
```

---

### 5.4 エラーメッセージの設計原則

#### 原則1: 明確な原因提示
```
❌ Error: Database connection failed

× Bad:  "エラーが発生しました"
✓ Good: "データベース接続に失敗しました (data/keiba.db)"
```

#### 原則2: 具体的なアクション提示
```
❌ Error: Table 'NL_RA' does not exist

Suggested actions:
  1. Create database tables:
     $ jrvltsql db create-tables

  2. Check database configuration:
     $ jrvltsql config --show
```

#### 原則3: ドキュメントへの誘導
```
❌ LLM API Error: Invalid API key

Your OpenAI API key is invalid or expired.

How to fix:
  1. Get new API key from: https://platform.openai.com/api-keys
  2. Update configuration:
     $ jrvltsql llm setup

  3. Or edit config file directly:
     config/config.yaml

📖 Documentation: https://github.com/miyamamoto/jrvltsql#llm-setup
```

---

## 6. インタラクティブモードの詳細仕様

### 6.1 起動画面

```bash
$ jrvltsql query -i

╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   JRVLTSQL Interactive Query Shell                    ║
║   Version 0.2.0-alpha                                 ║
║                                                       ║
║   Ask questions in natural language (Japanese)        ║
║   Type /help for commands, /examples for samples      ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

Configuration:
  Database:     SQLite (data/keiba.db)
  Tables:       57 (NL_38, RT_19)
  Data Range:   2020-01-01 to 2024-12-15
  LLM Provider: OpenAI (gpt-4-turbo)
  Output:       Table format

Ready to answer your questions!

🔍 >
```

### 6.2 プロンプトデザイン

```
# 通常状態
🔍 >

# 実行中
⚙️  >

# エラー状態
❌ >

# 編集モード
✏️  >

# 確認待ち
❓ >
```

### 6.3 キーボードショートカット

| ショートカット | 機能 |
|--------------|------|
| `Ctrl+C` | キャンセル/中断 |
| `Ctrl+D` | 終了 |
| `Ctrl+L` | 画面クリア |
| `↑/↓` | 履歴ナビゲーション |
| `Tab` | オートコンプリート（将来実装） |
| `Ctrl+R` | 履歴検索（将来実装） |

### 6.4 自動補完（将来実装）

```
🔍 > 武豊[Tab]

Suggestions:
  武豊騎手の成績
  武豊騎手の勝率
  武豊騎手の2024年成績
  武豊騎手の中山競馬場での勝率

[↑/↓] to select, [Enter] to choose
```

---

## 7. 将来のGUI化を見据えた設計

### 7.1 アーキテクチャ分離

```
┌────────────────────────────────────────┐
│        Presentation Layer              │
│  ┌──────────┐  ┌──────────────────┐   │
│  │   CLI    │  │   GUI (Future)   │   │
│  │  (Click) │  │   (PyQt/Tkinter) │   │
│  └─────┬────┘  └────────┬─────────┘   │
└────────┼────────────────┼─────────────┘
         │                │
         └────────┬───────┘
                  │
┌─────────────────▼────────────────────┐
│        Business Logic Layer          │
│  ┌────────────────────────────────┐  │
│  │  QueryService                  │  │
│  │  - natural_language_to_sql()   │  │
│  │  - execute_query()             │  │
│  │  - format_results()            │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  LLMService                    │  │
│  │  - generate_sql()              │  │
│  │  - validate_sql()              │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
                  │
┌─────────────────▼────────────────────┐
│        Data Access Layer             │
│  ┌────────────────────────────────┐  │
│  │  DatabaseManager               │  │
│  │  - SQLiteDatabase              │  │
│  │  - PostgreSQLDatabase          │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

### 7.2 GUI画面イメージ（将来構想）

#### メイン画面（ワイヤーフレーム）

```
┌─────────────────────────────────────────────────────────────┐
│ JRVLTSQL - Horse Racing Data Analysis                       │
├─────────────────────────────────────────────────────────────┤
│ File  Edit  View  Query  Database  Settings  Help           │
├──────────┬──────────────────────────────────────────────────┤
│          │  🔍 質問を入力してください...                      │
│  History │  ┌────────────────────────────────────────────┐  │
│          │  │ 2024年の騎手別勝率TOP10                     │  │
│  ├ 今日  │  └────────────────────────────────────────────┘  │
│  ├ 昨日  │                                                   │
│  ├ 今週  │  [検索] [SQL表示] [履歴] [例文]                  │
│  └ 全体  │                                                   │
│          ├───────────────────────────────────────────────┤
│  Saved   │  📊 Results (10 rows)                            │
│  Queries │  ┌────┬─────────┬────────┬────────┬─────────┐  │
│          │  │ No │ 騎手名   │ 勝率   │ 騎乗数 │ 勝利数  │  │
│  ├ 騎手  │  ├────┼─────────┼────────┼────────┼─────────┤  │
│  ├ 馬    │  │  1 │ 武豊     │ 25.4%  │  118   │   30    │  │
│  ├ 配当  │  │  2 │ ルメール │ 22.8%  │  114   │   26    │  │
│  └ 統計  │  │ .. │ ...      │ ...    │  ...   │  ...    │  │
│          │  └────┴─────────┴────────┴────────┴─────────┘  │
│          │                                                   │
│          │  [Export] [Chart] [Save Query]                   │
│          │                                                   │
├──────────┴───────────────────────────────────────────────────┤
│ 🟢 Connected: SQLite | 📊 Tables: 57 | 📅 Data: 2020-2024    │
└─────────────────────────────────────────────────────────────┘
```

#### チャート表示画面

```
┌─────────────────────────────────────────────────────────────┐
│ Chart Viewer - 騎手別勝率TOP10                               │
├─────────────────────────────────────────────────────────────┤
│  Chart Type: [Bar Chart ▼]  [2D ▼]  [Color ▼]              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   30% ┤                                                      │
│       │  ███                                                 │
│   25% ┤  ███                                                 │
│       │  ███ ███                                             │
│   20% ┤  ███ ███ ███ ███                                     │
│       │  ███ ███ ███ ███ ███                                 │
│   15% ┤  ███ ███ ███ ███ ███ ███ ███ ███ ███ ███           │
│       │  ███ ███ ███ ███ ███ ███ ███ ███ ███ ███           │
│   10% ┤  ███ ███ ███ ███ ███ ███ ███ ███ ███ ███           │
│       └──┴───┴───┴───┴───┴───┴───┴───┴───┴───┴─            │
│         武豊 ル 横山 川田 福永 戸崎 松山 菱田 岩田 三浦       │
│                                                              │
│  Legend: ■ Win Rate (%)                                      │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  [Save as PNG] [Save as SVG] [Copy to Clipboard] [Close]    │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 GUI対応のためのCLI設計原則

1. **ビジネスロジックの完全分離**
   - CLIコマンドはプレゼンテーション層のみ
   - 全機能を`services/`モジュールに実装
   - GUIから同じサービスを呼び出せる設計

2. **設定管理の統一**
   - CLI/GUI共通の設定ファイル（YAML）
   - 環境変数のサポート
   - 設定変更APIの提供

3. **出力フォーマットの抽象化**
   - 結果は常に構造化データ（dict/list）で返す
   - フォーマッター（CLI/JSON/GUI）を分離
   - プログレス情報はコールバックで提供

4. **エラーハンドリングの標準化**
   - カスタム例外クラスの定義
   - エラーコードの体系化
   - エラーメッセージの多言語対応準備

---

## 8. 実装ロードマップ

### Phase 1: CLI基本機能（v0.2.0）
- [x] 既存コマンド（init, fetch, create-tables等）
- [ ] `jrvltsql query` コマンド追加
- [ ] `jrvltsql llm` コマンドグループ追加
- [ ] LLM統合（OpenAI API）
- [ ] テーブル形式出力
- [ ] JSON形式出力
- [ ] 基本的なエラーハンドリング

### Phase 2: UX改善（v0.3.0）
- [ ] インタラクティブモード
- [ ] プログレス表示の実装
- [ ] 履歴機能
- [ ] 例文集
- [ ] ASCII Artチャート
- [ ] SQLエディター機能

### Phase 3: 高度な機能（v0.4.0）
- [ ] 複数LLMプロバイダー対応（Anthropic, Local）
- [ ] SQL最適化機能
- [ ] クエリキャッシュ
- [ ] バッチクエリ実行
- [ ] スケジュール実行

### Phase 4: GUI準備（v0.5.0）
- [ ] ビジネスロジック完全分離
- [ ] REST API化（オプション）
- [ ] 設定管理UI化準備
- [ ] 画像チャート出力（matplotlib）

### Phase 5: GUI実装（v1.0.0）
- [ ] PyQt/Tkinterベースのデスクトップアプリ
- [ ] ドラッグ&ドロップインターフェース
- [ ] インタラクティブチャート
- [ ] ダッシュボード機能

---

## 9. 実装例（コードスニペット）

### 9.1 QueryServiceの基本構造

```python
# src/services/query_service.py

from typing import Dict, List, Optional
from src.services.llm_service import LLMService
from src.database.base import Database

class QueryService:
    """Natural language query service."""

    def __init__(self, database: Database, llm_service: LLMService):
        self.database = database
        self.llm_service = llm_service
        self.history = []

    def ask(
        self,
        question: str,
        dry_run: bool = False,
        explain: bool = False,
    ) -> Dict:
        """Process natural language question.

        Args:
            question: Natural language question
            dry_run: Only generate SQL, don't execute
            explain: Include SQL in response

        Returns:
            {
                "question": str,
                "sql": str,
                "results": List[Dict],
                "row_count": int,
                "execution_time": float,
                "error": Optional[str]
            }
        """
        # Generate SQL from question
        sql_result = self.llm_service.generate_sql(
            question=question,
            schema=self.database.get_schema()
        )

        if sql_result["error"]:
            return {
                "question": question,
                "sql": None,
                "results": [],
                "row_count": 0,
                "execution_time": 0,
                "error": sql_result["error"]
            }

        sql = sql_result["sql"]

        # Dry run mode: return SQL only
        if dry_run:
            return {
                "question": question,
                "sql": sql,
                "results": [],
                "row_count": 0,
                "execution_time": 0,
                "error": None
            }

        # Execute SQL
        try:
            import time
            start = time.time()
            results = self.database.fetch_all(sql)
            execution_time = time.time() - start

            response = {
                "question": question,
                "sql": sql if explain else None,
                "results": results,
                "row_count": len(results),
                "execution_time": execution_time,
                "error": None
            }

            # Add to history
            self.history.append(response)

            return response

        except Exception as e:
            return {
                "question": question,
                "sql": sql,
                "results": [],
                "row_count": 0,
                "execution_time": 0,
                "error": str(e)
            }
```

### 9.2 CLIコマンド実装例

```python
# src/cli/commands/query.py

import click
from rich.console import Console
from rich.table import Table

from src.services.query_service import QueryService
from src.services.llm_service import LLMService
from src.database.sqlite_handler import SQLiteDatabase

console = Console()

@click.command()
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
@click.option("--question", "-q", help="Question to ask")
@click.option("--output", "-o", type=click.Choice(["table", "json", "csv"]), default="table")
@click.option("--explain", "-e", is_flag=True, help="Show generated SQL")
@click.option("--dry-run", is_flag=True, help="Generate SQL only")
@click.pass_context
def query(ctx, interactive, question, output, explain, dry_run):
    """Ask questions in natural language."""

    # Initialize services
    config = ctx.obj.get("config")
    database = SQLiteDatabase(config.get("databases.sqlite"))
    llm_service = LLMService(config.get("llm"))
    query_service = QueryService(database, llm_service)

    if interactive:
        # Start interactive mode
        interactive_shell(query_service, output, explain)
    elif question:
        # One-shot query
        result = query_service.ask(
            question=question,
            dry_run=dry_run,
            explain=explain
        )

        # Display result
        if output == "table":
            display_table(result)
        elif output == "json":
            display_json(result)
        elif output == "csv":
            display_csv(result)
    else:
        console.print("[red]Error:[/red] Please specify --interactive or --question")

def display_table(result: Dict):
    """Display results as table."""
    if result["error"]:
        console.print(f"[red]Error:[/red] {result['error']}")
        return

    if result["sql"]:
        console.print("\n[bold cyan]Generated SQL:[/bold cyan]")
        console.print(result["sql"])
        console.print()

    if result["row_count"] == 0:
        console.print("[yellow]No results found[/yellow]")
        return

    # Create rich table
    table = Table(show_header=True, header_style="bold cyan")

    # Add columns
    for col in result["results"][0].keys():
        table.add_column(col)

    # Add rows
    for row in result["results"]:
        table.add_row(*[str(v) for v in row.values()])

    console.print(table)
    console.print(f"\n[green]✓[/green] {result['row_count']} rows ({result['execution_time']:.2f}s)")

def interactive_shell(query_service: QueryService, output: str, explain: bool):
    """Start interactive query shell."""
    console.print("[bold cyan]JRVLTSQL Interactive Query Shell[/bold cyan]")
    console.print("Type /help for commands, /exit to quit\n")

    while True:
        try:
            question = console.input("[bold blue]🔍 >[/bold blue] ")

            if not question.strip():
                continue

            # Handle special commands
            if question.startswith("/"):
                handle_command(question, query_service)
                continue

            # Process question
            result = query_service.ask(
                question=question,
                explain=explain
            )

            display_table(result)
            console.print()

        except KeyboardInterrupt:
            console.print("\n[yellow]Use /exit to quit[/yellow]")
        except EOFError:
            break

def handle_command(command: str, query_service: QueryService):
    """Handle special commands."""
    if command == "/exit":
        console.print("[cyan]Goodbye![/cyan]")
        raise SystemExit(0)

    elif command == "/help":
        console.print("""
[bold cyan]Available Commands:[/bold cyan]
  /help      - Show this help
  /history   - Show query history
  /examples  - Show example questions
  /exit      - Exit interactive mode
        """)

    elif command == "/history":
        display_history(query_service.history)

    elif command == "/examples":
        display_examples()

    else:
        console.print(f"[red]Unknown command:[/red] {command}")
```

---

## 10. まとめ

この設計書では、競馬データ分析アプリJRVLTSQLのUI/UXを以下の観点から設計しました：

### 主要な設計ポイント

1. **CLIファーストアプローチ**
   - 技術ユーザー向けの使いやすいコマンド体系
   - インタラクティブ/バッチ両モード対応
   - 豊富な出力フォーマット

2. **ユーザーエクスペリエンス**
   - 明確なプログレス表示
   - 親切なエラーメッセージ
   - 履歴・例文によるガイド

3. **拡張性**
   - GUI化を見据えたアーキテクチャ分離
   - 複数LLMプロバイダー対応
   - プラグイン可能な出力フォーマット

4. **実用性**
   - 実際のユーザーフローに基づく設計
   - 具体的なコマンド例
   - 段階的な実装ロードマップ

### 次のステップ

1. `QueryService`と`LLMService`の実装
2. `jrvltsql query`コマンドの実装
3. OpenAI API統合
4. インタラクティブシェルの実装
5. テーブル出力フォーマッターの実装

この設計に基づいて実装を進めることで、使いやすく拡張性の高い競馬データ分析ツールを構築できます。
