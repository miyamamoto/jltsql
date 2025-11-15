# JV-Data標準データベース準拠 実装計画

## 1. 調査結果サマリー

### JRA-VAN標準データベースの特徴

- **総テーブル数**: 52テーブル
- **主要テーブル**: RACE (110フィールド), UMA_RACE (73フィールド), HARAI, UMA等
- **データ型**: すべてTEXT型（サイズ指定あり: TEXT(2), TEXT(8), etc.)
- **命名規則**:
  - テーブル名: 英語/ローマ字（RACE, UMA_RACE, HARAI等）
  - カラム名: 英語/ローマ字（MakeDate, Year, MonthDay, JyoCD, Kaiji等）

### 現在のjltsqlスキーマの特徴

- **総テーブル数**: 57テーブル
- **テーブル名**: `NL_**`, `RT_**`形式（例: NL_RA, NL_SE, NL_HR）
- **データ型**: すべてTEXT型
- **カラム名**: 日本語（データ作成年月日、開催年、開催月日等）

### 主要な差分

| 項目 | jltsql現在 | JRA-VAN標準 | 対応方針 |
|------|-----------|-------------|---------|
| テーブル名 | NL_RA, NL_SE | RACE, UMA_RACE | 標準に準拠 |
| カラム名 | データ作成年月日, 開催年 | MakeDate, Year | 標準に準拠 |
| データ型 | TEXT | TEXT → 適切な型へ変換 | 拡張（型変換実装） |

## 2. テーブル名・カラム名マッピング

### 主要テーブルマッピング

| jltsql | JRA-VAN標準 | 説明 |
|--------|------------|------|
| NL_RA | RACE | レース詳細 |
| NL_SE | UMA_RACE | 馬毎レース情報 |
| NL_HR | HARAI | 払戻 |
| NL_UM | UMA | 馬マスター |
| NL_KS | KISYU | 騎手マスター |
| NL_CH | CHOKYO | 調教師マスター |
| NL_HN | BANUSI | 馬主マスター |
| NL_BN | SEISAN | 生産者マスター |
| NL_BR | HANSYOKU | 繁殖馬マスター |
| NL_YS | SCHEDULE | スケジュール |
| NL_H1 | ODDS_TANPUKU | 単勝・複勝オッズ |
| NL_O1 | ODDS_UMAREN | 馬連オッズ |
| NL_O2 | ODDS_WIDE | ワイドオッズ |
| NL_O3 | ODDS_WAKU | 枠連オッズ |
| NL_O4 | ODDS_UMATAN | 馬単オッズ |
| NL_O5 | ODDS_SANREN | 三連複オッズ |
| NL_O6 | ODDS_SANRENTAN | 三連単オッズ |

### カラム名マッピング（主要フィールド）

#### 共通フィールド

| jltsql (日本語) | JRA-VAN標準 | 型 | 変換方針 |
|----------------|------------|----|----|
| レコード種別ID | RecordSpec | TEXT(2) | そのまま |
| データ区分 | DataKubun | TEXT(1) | そのまま |
| データ作成年月日 | MakeDate | TEXT(8) → DATE | YYYYMMDD形式から DATE型へ |
| 開催年 | Year | TEXT(4) → INTEGER | 4桁年 → INTEGER |
| 開催月日 | MonthDay | TEXT(4) → INTEGER | MMDD形式 → INTEGER |
| 競馬場コード | JyoCD | TEXT(2) | そのまま |
| 開催回第N回 | Kaiji | TEXT(2) → INTEGER | 回次 → INTEGER |
| 開催日目N日目 | Nichiji | TEXT(2) → INTEGER | 日次 → INTEGER |
| レース番号 | RaceNum | TEXT(2) → INTEGER | レース番号 → INTEGER |

#### RACE テーブル固有

| jltsql (日本語) | JRA-VAN標準 | 型 | 変換方針 |
|----------------|------------|----|----|
| 距離 | Kyori | TEXT(4) → INTEGER | 距離(m) → INTEGER |
| 発走時刻 | HassoTime | TEXT(4) → TIME | HHMM → TIME |
| 登録頭数 | TorokuTosu | TEXT(2) → INTEGER | 頭数 → INTEGER |
| 出走頭数 | SyussoTosu | TEXT(2) → INTEGER | 頭数 → INTEGER |
| 本賞金1着 | Honsyokin1 | TEXT(8) → INTEGER | 賞金(千円) → INTEGER |
| ラップタイム1 | LapTime1 | TEXT(3) → DECIMAL(4,1) | ラップ(秒) → DECIMAL |

#### UMA_RACE テーブル固有

| jltsql (日本語) | JRA-VAN標準 | 型 | 変換方針 |
|----------------|------------|----|----|
| 馬番 | Umaban | TEXT(2) → INTEGER | 馬番 → INTEGER |
| 斤量 | Futan | TEXT(3) → DECIMAL(4,1) | 斤量(kg) → DECIMAL |
| 馬体重 | BaTaijyu | TEXT(3) → INTEGER | 体重(kg) → INTEGER |
| 増減差 | ZogenSa | TEXT(3) → INTEGER | 増減(kg) → INTEGER |
| 確定着順 | KakuteiJyuni | TEXT(2) → INTEGER | 着順 → INTEGER |
| タイム | Time | TEXT(4) → DECIMAL(5,1) | タイム(秒) → DECIMAL |
| オッズ | Odds | TEXT(4) → DECIMAL(6,1) | オッズ → DECIMAL |
| 人気 | Ninki | TEXT(2) → INTEGER | 人気順 → INTEGER |
| 本賞金 | Honsyokin | TEXT(8) → INTEGER | 賞金(千円) → INTEGER |

## 3. 型変換戦略

### データ型マッピング

| JV-Data型 | PostgreSQL | DuckDB | SQLite | MySQL | 変換ロジック |
|----------|-----------|---------|--------|-------|------------|
| TEXT(8) 日付 | DATE | DATE | TEXT | DATE | YYYYMMDD → DATE('YYYY-MM-DD') |
| TEXT(4) 年 | SMALLINT | SMALLINT | INTEGER | SMALLINT | int(s) |
| TEXT(4) MMDD | SMALLINT | SMALLINT | INTEGER | SMALLINT | int(s) if s else None |
| TEXT(2) 整数 | SMALLINT | SMALLINT | INTEGER | SMALLINT | int(s) if s and s.strip() else None |
| TEXT(3) 体重 | SMALLINT | SMALLINT | INTEGER | SMALLINT | int(s) if s and s.strip() else None |
| TEXT(4) 距離 | SMALLINT | SMALLINT | INTEGER | SMALLINT | int(s) |
| TEXT(4) 時刻 | TIME | TIME | TEXT | TIME | HHMM → TIME('HH:MM:00') |
| TEXT(4) タイム | DECIMAL(5,1) | DECIMAL(5,1) | REAL | DECIMAL(5,1) | "1234" → 123.4秒 |
| TEXT(3) ラップ | DECIMAL(4,1) | DECIMAL(4,1) | REAL | DECIMAL(4,1) | "123" → 12.3秒 |
| TEXT(3) 斤量 | DECIMAL(4,1) | DECIMAL(4,1) | REAL | DECIMAL(4,1) | "550" → 55.0kg |
| TEXT(4) オッズ | DECIMAL(6,1) | DECIMAL(6,1) | REAL | DECIMAL(6,1) | "0123" → 12.3倍 |
| TEXT(8) 賞金 | INTEGER | INTEGER | INTEGER | INTEGER | int(s) * 1000 (千円単位) |

### 変換優先度

#### 優先度 HIGH（必須）

- **日付系**: MakeDate, Year, MonthDay
- **整数系**: Kaiji, Nichiji, RaceNum, Kyori, TorokuTosu, SyussoTosu
- **馬番・着順**: Umaban, KakuteiJyuni, NyusenJyuni, Ninki

#### 優先度 MEDIUM（推奨）

- **数値系**: Futan, BaTaijyu, ZogenSa, Honsyokin, Fukasyokin
- **タイム系**: Time, HaronTimeL3, HaronTimeL4
- **オッズ系**: Odds

#### 優先度 LOW（保留可）

- **コメント系**: そのままTEXT
- **名称系**: そのままTEXT（全角/半角混在のため）
- **コード系**: TEXT維持（マスターテーブル結合用）

## 4. 実装フェーズ

### Phase 1: スキーマ定義更新

**目的**: JRA-VAN標準に準拠したスキーマ定義を作成

**タスク**:
1. 新しいスキーマ定義ファイル `src/database/schema_jravan.py` を作成
2. 主要52テーブルの定義を生成（テーブル名・カラム名・型定義）
3. 既存schema.pyとの互換性維持（移行期間用）

**成果物**:
- `src/database/schema_jravan.py`
- `src/database/table_mappings.py`（旧→新テーブル名マッピング）

### Phase 2: Parser型変換機能実装

**目的**: Parserレベルでの型変換を実装

**タスク**:
1. `FieldDef` クラス拡張（type, format属性追加）
2. 型変換関数の実装 (`converters.py`)
3. BaseParserでの型変換処理追加
4. 各パーサーのFieldDef更新

**成果物**:
- `src/parser/converters.py`（型変換関数）
- `src/parser/base.py`（型変換ロジック追加）
- 更新されたパーサー定義

### Phase 3: Importer更新

**目的**: 新しいテーブル名・型に対応

**タスク**:
1. テーブル名マッピング更新（RA → RACE等）
2. 型付きデータの挿入対応
3. エラーハンドリング強化

**成果物**:
- `src/importer/importer.py`（更新版）

### Phase 4: マイグレーション・テスト

**目的**: 既存データの移行とテスト

**タスク**:
1. 既存データのマイグレーションスクリプト作成
2. 型変換のユニットテスト作成
3. 統合テスト実施

**成果物**:
- `scripts/migrate_to_jravan_schema.py`
- `tests/test_type_conversion.py`
- `tests/test_jravan_schema.py`

## 5. 技術的考慮事項

### データベース互換性

- **PostgreSQL**: 完全な型サポート（DATE, TIME, DECIMAL等）
- **DuckDB**: 完全な型サポート
- **SQLite**: 限定的型サポート（DATE → TEXT, DECIMAL → REAL）
- **MySQL**: ほぼ完全サポート

→ **対応**: データベースごとの型マッピングを実装

### パフォーマンス

- 型変換のオーバーヘッド: Parserレベルで1回のみ
- インデックス効率: INTEGER/DATE型により向上
- ストレージ: 型指定により削減の可能性

### 互換性維持

- 既存のNL_*テーブルとの互換性
- 段階的移行の可能性
- ビュー定義による旧テーブル名のエイリアス

## 6. 次のステップ

1. ✅ JRA-VAN標準データベースファイル入手・分析（完了）
2. ✅ 差分分析・実装計画策定（完了）
3. ⏳ Phase 1: スキーマ定義更新の実装
4. ⏳ Phase 2: Parser型変換機能の実装
5. ⏳ Phase 3: Importer更新
6. ⏳ Phase 4: テスト・マイグレーション

---

**作成日**: 2025-11-15
**参照**:
- JRA-VAN標準データベースファイル (Data.mdb)
- VB2019-Builder プログラミングパーツ
- jltsql 現行スキーマ (src/database/schema.py)
