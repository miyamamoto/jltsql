import sqlite3
import os

db_path = r"C:\Users\mitsu\work\jrvltsql\data\keiba.db"

# データベースファイルの存在確認
if not os.path.exists(db_path):
    print(f"Error: Database file not found at {db_path}")
    exit(1)

print(f"Database file size: {os.path.getsize(db_path) / 1024 / 1024:.2f} MB")
print("-" * 80)

# データベース接続
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 全テーブル名を取得
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"\n=== 全テーブル一覧 (合計: {len(tables)}テーブル) ===\n")

# テーブルごとのレコード数を取得
table_info = []
empty_tables = []
main_tables = ['NL_RA', 'NL_SE', 'NL_HR', 'NL_UM', 'NL_KI', 'NL_CH', 'NL_BR']

for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    table_info.append((table_name, count))

    if count == 0:
        empty_tables.append(table_name)

# 全テーブルのレコード数を表示
print(f"{'テーブル名':<30} {'レコード数':>15}")
print("-" * 80)
for table_name, count in table_info:
    marker = " [主要]" if table_name in main_tables else ""
    marker += " [空]" if count == 0 else ""
    print(f"{table_name:<30} {count:>15,}{marker}")

# 空のテーブルを特定
print("\n" + "=" * 80)
print(f"\n=== レコード数が0のテーブル (合計: {len(empty_tables)}テーブル) ===\n")
if empty_tables:
    for table_name in empty_tables:
        print(f"  - {table_name}")
else:
    print("  (なし - すべてのテーブルにデータがあります)")

# 主要テーブルのレコード数
print("\n" + "=" * 80)
print("\n=== 主要テーブルのレコード数 ===\n")
for table_name, count in table_info:
    if table_name in main_tables:
        print(f"  {table_name:<15} : {count:>15,} レコード")

# テーブルの構造情報（主要テーブルのみ）
print("\n" + "=" * 80)
print("\n=== 主要テーブルの構造 ===\n")
for table_name in main_tables:
    # テーブルが存在するか確認
    if table_name not in [t[0] for t in tables]:
        print(f"{table_name}: (テーブルが存在しません)")
        continue

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"\n{table_name} ({len(columns)} カラム):")
    for col in columns[:5]:  # 最初の5カラムのみ表示
        col_id, col_name, col_type, not_null, default_val, pk = col
        print(f"  - {col_name} ({col_type})")
    if len(columns) > 5:
        print(f"  ... 他 {len(columns) - 5} カラム")

# 統計情報
print("\n" + "=" * 80)
print("\n=== 統計情報 ===\n")
total_records = sum(count for _, count in table_info)
non_empty_tables = len([t for t in table_info if t[1] > 0])
print(f"  総テーブル数      : {len(tables)}")
print(f"  データ有テーブル  : {non_empty_tables}")
print(f"  空テーブル        : {len(empty_tables)}")
print(f"  総レコード数      : {total_records:,}")

conn.close()
print("\n" + "=" * 80)
print("検査完了")
