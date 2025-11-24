# 3データベース実装の整合性問題レポート

## 発見された整合性問題

### 1. PostgreSQLハンドラーのプレースホルダー不一致【重大】

#### 問題の詳細

`postgresql_handler.py`内で**2つの異なるプレースホルダー形式**が混在:

**パターンA: `?` プレースホルダー（変換あり）**
```python
# base.py の insert() / insert_many()
sql = f"INSERT INTO {table_name} ({', '.join(quoted_columns)}) VALUES ({placeholders})"
placeholders = ", ".join(["?" for _ in columns])  # ? を使用

# postgresql_handler.py の _convert_placeholders_and_params() で変換
# pg8000: ? → :param1, :param2, :param3
# psycopg: ? → %s
```

**パターンB: `%s` プレースホルダー（変換なし）**
```python
# postgresql_handler.py 行364-369
def table_exists(self, table_name: str) -> bool:
    sql = """
        SELECT tablename
        FROM pg_tables
        WHERE tablename = %s  # 直接 %s を使用
    """
    row = self.fetch_one(sql, (table_name,))
    return row is not None

# postgresql_handler.py 行388-394
def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = %s  # 直接 %s を使用
        ORDER BY ordinal_position
    """
    return self.fetch_all(sql, (table_name,))
```

#### 問題の影響

**pg8000ドライバー使用時**:
- `%s`が`:param1`に変換されず、SQLエラー発生
- エラーメッセージ: `"%"またはその近辺で構文エラー`
- `table_exists()` → 常にFalse返却（テーブルが存在しても検出不可）
- `get_table_columns()` → DatabaseError例外

**psycopgドライバー使用時**:
- `%s`がそのまま使用されるため、正常動作

#### 実際のエラーログ
```
2025-11-18 15:22:48 [error] SQL query failed:
    SELECT tablename
    FROM pg_tables
    WHERE tablename = %  # %s が % に誤認識
error={'S': 'ERROR', 'C': '42601', 'M': '"%"またはその近辺で構文エラー'}
```

#### 根本原因

`fetch_one()` / `fetch_all()` が `_convert_placeholders_and_params()` を呼び出す前に、ハードコードされた `%s` プレースホルダーが含まれるSQL文を渡している。

```python
# postgresql_handler.py 行272-289 (fetch_one)
def fetch_one(self, sql: str, parameters: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
    try:
        # プレースホルダー変換を実行
        sql, params = self._convert_placeholders_and_params(sql, parameters)

        if DRIVER == "pg8000":
            # %s が含まれたままのSQLを実行 → エラー
            rows = self._connection.run(sql, **params)
```

#### 修正提案

**オプション1: `table_exists()` / `get_table_columns()` を `?` に統一**
```python
def table_exists(self, table_name: str) -> bool:
    sql = """
        SELECT tablename
        FROM pg_tables
        WHERE tablename = ?  # %s → ? に変更
    """
    row = self.fetch_one(sql, (table_name,))
    return row is not None
```

**オプション2: `_convert_placeholders_and_params()` を改良**
```python
def _convert_placeholders_and_params(self, sql: str, parameters: Optional[tuple] = None):
    if DRIVER == "pg8000":
        # %s と ? の両方を :param1, :param2 に変換
        import re
        placeholders = re.findall(r'(\?|%s)', sql)
        result = sql
        for i, placeholder in enumerate(placeholders):
            result = result.replace(placeholder, f":param{i+1}", 1)
        # ...
```

**推奨**: オプション1（シンプル、既存の変換ロジックを活用）

---

### 2. SQLiteのKeyError（軽微、修正済み）

#### 問題の詳細

統計収集スクリプトで `KeyError: 0` が発生。

#### 原因推定

`fetch_all()` の戻り値の型不一致:
- 期待: `List[Dict[str, Any]]`
- 実際: タプルとしてアクセスされた箇所が存在

#### 影響

データ挿入は成功（136,468レコード）、統計収集のみエラー。

#### 修正済み

現在は正常動作。

---

### 3. DuckDBのexecutemany戻り値問題【重要】

#### 問題の詳細

```python
# duckdb_handler.py 行146-147
def executemany(self, sql: str, parameters_list: List[tuple]) -> int:
    self._cursor.executemany(sql, parameters_list)
    return len(parameters_list)  # 実際の挿入成功数でなく、要求数を返す
```

#### 影響

- 挿入失敗時も成功したように見える
- `importer.py` の統計が不正確
- タイムアウト問題のデバッグを困難にする

#### 修正提案

```python
def executemany(self, sql: str, parameters_list: List[tuple]) -> int:
    self._cursor.executemany(sql, parameters_list)
    # DuckDBがrowcountをサポートしているか確認
    if hasattr(self._cursor, 'rowcount') and self._cursor.rowcount >= 0:
        return self._cursor.rowcount
    else:
        # フォールバック: 要求数（警告ログ出力推奨）
        logger.warning("DuckDB rowcount unavailable, returning requested count")
        return len(parameters_list)
```

---

### 4. 識別子クォーティングの不統一【中程度】

#### 現状

| データベース | 実装 | 方式 |
|------------|------|------|
| PostgreSQL | `return identifier.lower()` | lowercase、クォートなし |
| SQLite | `return f"\`{identifier}\`"` | バッククォート（MySQL互換） |
| DuckDB | `return f'"{identifier}"'` | ダブルクォート（ケースセンシティブ） |

#### 問題

- **PostgreSQL**: 正しい（標準SQL準拠、ケース問題なし）
- **SQLite**: バッククォートはSQLite拡張、標準SQLではない
- **DuckDB**: ダブルクォートでケースセンシティブになり、スキーマ不一致の可能性

#### 実例

スキーマ定義:
```sql
CREATE TABLE IF NOT EXISTS NL_BN (
    RecordSpec TEXT,  -- 大文字
    DataKubun TEXT    -- 大文字
)
```

挿入時:
```python
# PostgreSQL
quoted = _quote_identifier("RecordSpec")  # → "recordspec"（lowercase）
# SQL: INSERT INTO nl_bn (recordspec, datakubun) VALUES (...)
# 結果: 成功（PostgreSQLが自動lowercase化）

# DuckDB
quoted = _quote_identifier("RecordSpec")  # → "RecordSpec"（そのまま）
# SQL: INSERT INTO NL_BN ("RecordSpec", "DataKubun") VALUES (...)
# 結果: ケースセンシティブマッチが必要 → 失敗の可能性
```

#### 修正提案

**すべてのDBハンドラーでPostgreSQL方式に統一**:
```python
def _quote_identifier(self, identifier: str) -> str:
    """PostgreSQL標準方式: lowercase、クォートなし"""
    return identifier.lower()
```

---

### 5. トランザクション戦略の不統一【中程度】

#### 現状

| データベース | commit() | トランザクション管理 |
|------------|----------|------------------|
| PostgreSQL (pg8000) | no-op | autocommit mode |
| PostgreSQL (psycopg) | 手動commit | 明示的トランザクション |
| SQLite | 手動commit | 明示的トランザクション |
| DuckDB | 手動commit | 明示的トランザクション |

#### 問題

- **importer.py** で `auto_commit=True` を前提とした設計
- 実際には pg8000 のみ真のautocommit、他は手動commit必要
- 大量データ挿入時の動作が3DB間で異なる

#### 実際の挙動

**PostgreSQL (pg8000)**:
```python
for batch in batches:
    db.insert_many(table_name, batch)  # 即座にコミット
    # db.commit()  # 呼んでも無害（no-op）
```

**SQLite / DuckDB**:
```python
for batch in batches:
    db.insert_many(table_name, batch)  # トランザクション内に蓄積
# db.commit()  # ここで初めてコミット（全バッチまとめて）
```

#### 影響

- PostgreSQL: 各バッチが独立、失敗時の影響最小
- SQLite/DuckDB: 最後のcommit()まで全データがメモリ/ログに蓄積 → パフォーマンス低下

#### 修正提案

**オプション1: バッチ毎にcommit（統一性重視）**
```python
# importer.py の _flush_batch()
def _flush_batch(self, table_name: str, batch: List[Dict[str, Any]]):
    rows = self.database.insert_many(table_name, batch)
    self.database.commit()  # 全DBでバッチ毎にコミット
    self._records_imported += rows
```

**オプション2: SQLite/DuckDBでautocommit有効化**
```python
# sqlite_handler.py
self._connection.isolation_level = None  # autocommit mode

# duckdb_handler.py
# DuckDB 0.9.0以降でautocommitサポート確認
```

---

## 整合性チェックリスト

### 必須修正（重大）

- [ ] **PostgreSQL**: `table_exists()` / `get_table_columns()` のプレースホルダーを `?` に統一
- [ ] **DuckDB**: `executemany()` の戻り値を実際のrowcountに修正
- [ ] **全DB**: 識別子クォーティングをlowercase統一

### 推奨修正（重要）

- [ ] **全DB**: トランザクション戦略統一（バッチ毎commit）
- [ ] **DuckDB**: タイムアウト問題の根本対策（バッチサイズ削減 or DataFrame挿入）

### 任意修正（改善）

- [ ] **PostgreSQL**: `_convert_placeholders_and_params()` で `%s` も変換対象に追加
- [ ] **SQLite**: WALモード有効化（パフォーマンス向上）

---

## 優先順位付き修正ロードマップ

### Phase 1: 緊急修正（即座実施）

1. **PostgreSQL プレースホルダー統一**
   - ファイル: `src/database/postgresql_handler.py`
   - 対象メソッド: `table_exists()`, `get_table_columns()`
   - 修正内容: `%s` → `?`
   - 影響: pg8000使用時のバグ修正

### Phase 2: 安定性向上（1週間以内）

2. **識別子クォーティング統一**
   - ファイル: `src/database/sqlite_handler.py`, `duckdb_handler.py`
   - 対象メソッド: `_quote_identifier()`
   - 修正内容: バッククォート/ダブルクォート → lowercase
   - 影響: 3DB間の完全互換性確保

3. **DuckDB executemany戻り値修正**
   - ファイル: `src/database/duckdb_handler.py`
   - 対象メソッド: `executemany()`
   - 修正内容: `len(parameters_list)` → `self._cursor.rowcount`
   - 影響: 挿入統計の正確性向上

### Phase 3: パフォーマンス最適化（2週間以内）

4. **トランザクション戦略統一**
   - ファイル: `src/importer/importer.py`
   - 対象メソッド: `_flush_batch()`
   - 修正内容: バッチ毎にcommit追加
   - 影響: SQLite/DuckDBのパフォーマンス向上

5. **DuckDB最適化**
   - ファイル: `src/database/duckdb_handler.py`
   - 新規メソッド: `insert_many_optimized()` (DataFrame挿入)
   - 修正内容: OLTP型挿入をOLAP最適化
   - 影響: タイムアウト問題解決

---

## テスト計画

### Phase 1テスト
```python
# test_postgresql_placeholders.py
def test_table_exists_with_pg8000():
    db = PostgreSQLDatabase(config)
    db.connect()
    assert db.table_exists("nl_jg") == True  # 修正前: False

def test_get_table_columns_with_pg8000():
    db = PostgreSQLDatabase(config)
    db.connect()
    columns = db.get_table_columns("nl_jg")
    assert len(columns) > 0  # 修正前: DatabaseError
```

### Phase 2テスト
```python
# test_identifier_consistency.py
def test_quote_identifier_consistency():
    pg_db = PostgreSQLDatabase(config)
    sqlite_db = SQLiteDatabase(config)
    duckdb_db = DuckDBDatabase(config)

    # すべて同じ結果を返す
    assert pg_db._quote_identifier("RecordSpec") == "recordspec"
    assert sqlite_db._quote_identifier("RecordSpec") == "recordspec"
    assert duckdb_db._quote_identifier("RecordSpec") == "recordspec"
```

### Phase 3テスト
```python
# test_transaction_consistency.py
def test_batch_commit_all_databases():
    for db in [pg_db, sqlite_db, duckdb_db]:
        importer = DataImporter(db, batch_size=1000)
        importer.import_records(test_records)

        # 各バッチ後にデータが即座にコミットされる
        count = db.fetch_one("SELECT COUNT(*) as cnt FROM NL_JG")['cnt']
        assert count > 0
```

---

## まとめ

### 発見された問題数

- **重大**: 2件（PostgreSQL プレースホルダー、DuckDB executemany）
- **重要**: 2件（識別子クォーティング、トランザクション戦略）
- **軽微**: 1件（SQLite KeyError、修正済み）

### PostgreSQL 100%成功の真の理由

1. **autocommit mode**: トランザクション問題を回避
2. **lowercase identifier**: ケース問題を完全回避
3. **プレースホルダー変換**: `?` → 適切な形式
4. **エンタープライズ品質**: MVCC、WAL

**ただし**、`table_exists()` / `get_table_columns()` はpg8000でバグ（Phase 1修正必須）

### 次のアクション

1. Phase 1修正を即座実施（PostgreSQLバグ修正）
2. 統合テストでPhase 2/3の影響範囲を検証
3. 修正後に3DB完全互換性を確認

---

**作成日**: 2025-11-18
**分析者**: Database Optimization Expert
**優先度**: 高（Phase 1）、中（Phase 2/3）
