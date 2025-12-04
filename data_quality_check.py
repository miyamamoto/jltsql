import sqlite3
import os
import sys
from datetime import datetime

# Windows cp932対策
if sys.platform == "win32":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def check_data_quality(db_path):
    """
    JLTSQLプロジェクトのマスターデータ品質チェック
    """
    if not os.path.exists(db_path):
        print(f"エラー: データベースファイルが見つかりません: {db_path}")
        return

    print("=" * 80)
    print("JLTSQL マスターデータ品質チェックレポート")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"データベース: {db_path}")
    print("=" * 80)
    print()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. NL_UM（馬マスター）テーブルのチェック
    print("【1. NL_UM（馬マスター）テーブル】")
    print("-" * 80)

    try:
        # レコード数
        cursor.execute("SELECT COUNT(*) FROM NL_UM")
        record_count = cursor.fetchone()[0]
        print(f"[OK] レコード数: {record_count:,} 件")

        # KettoNum（血統登録番号）の一意性チェック
        cursor.execute("""
            SELECT KettoNum, COUNT(*) as cnt
            FROM NL_UM
            GROUP BY KettoNum
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"[NG] KettoNumの重複: {len(duplicates)} 件")
            for dup in duplicates[:5]:
                print(f"  - KettoNum: {dup[0]}, 重複数: {dup[1]}")
        else:
            print("[OK] KettoNumの一意性: OK（重複なし）")

        # BirthDate（生年月日）の範囲チェック（1980〜2025）
        cursor.execute("""
            SELECT COUNT(*)
            FROM NL_UM
            WHERE CAST(SUBSTR(BirthDate, 1, 4) AS INTEGER) < 1980
               OR CAST(SUBSTR(BirthDate, 1, 4) AS INTEGER) > 2025
        """)
        invalid_birth_year = cursor.fetchone()[0]
        if invalid_birth_year > 0:
            print(f"[NG] BirthDateの範囲外: {invalid_birth_year} 件（1980〜2025の範囲外）")
            cursor.execute("""
                SELECT KettoNum, Bamei, BirthDate
                FROM NL_UM
                WHERE CAST(SUBSTR(BirthDate, 1, 4) AS INTEGER) < 1980
                   OR CAST(SUBSTR(BirthDate, 1, 4) AS INTEGER) > 2025
                LIMIT 5
            """)
            for row in cursor.fetchall():
                print(f"  - KettoNum: {row[0]}, 馬名: {row[1]}, 生年月日: {row[2]}")
        else:
            print("[OK] BirthDateの範囲チェック: OK（1980〜2025の範囲内）")

        # BirthDateの統計情報
        cursor.execute("""
            SELECT
                MIN(CAST(SUBSTR(BirthDate, 1, 4) AS INTEGER)) as min_year,
                MAX(CAST(SUBSTR(BirthDate, 1, 4) AS INTEGER)) as max_year,
                COUNT(*) as total
            FROM NL_UM
            WHERE BirthDate IS NOT NULL AND BirthDate != ''
        """)
        birth_stats = cursor.fetchone()
        if birth_stats[0]:
            print(f"[OK] 生年の範囲: {birth_stats[0]}年〜{birth_stats[1]}年（{birth_stats[2]:,}件）")

        # サンプルデータ5件を表示
        print("\n[OK] サンプルデータ（5件）:")
        cursor.execute("""
            SELECT KettoNum, Bamei, BirthDate, SexCD, KeiroCD
            FROM NL_UM
            LIMIT 5
        """)
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f"  {i}. KettoNum: {row[0]}, 馬名: {row[1]}, 生年月日: {row[2]}, 性別: {row[3]}, 毛色: {row[4]}")

    except sqlite3.Error as e:
        print(f"[NG] エラー: {e}")

    print()

    # 2. NL_KS（騎手マスター）テーブルのチェック
    print("【2. NL_KS（騎手マスター）テーブル】")
    print("-" * 80)

    try:
        # レコード数
        cursor.execute("SELECT COUNT(*) FROM NL_KS")
        record_count = cursor.fetchone()[0]
        print(f"[OK] レコード数: {record_count:,} 件")

        # KisyuCodeの一意性チェック
        cursor.execute("""
            SELECT KisyuCode, COUNT(*) as cnt
            FROM NL_KS
            GROUP BY KisyuCode
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"[NG] KisyuCodeの重複: {len(duplicates)} 件")
            for dup in duplicates[:5]:
                print(f"  - KisyuCode: {dup[0]}, 重複数: {dup[1]}")
        else:
            print("[OK] KisyuCodeの一意性: OK（重複なし）")

        # サンプルデータ3件を表示
        print("\n[OK] サンプルデータ（3件）:")
        cursor.execute("""
            SELECT KisyuCode, KisyuName, KisyuNameKana, TozaiCD, SexCD
            FROM NL_KS
            LIMIT 3
        """)
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f"  {i}. KisyuCode: {row[0]}, 騎手名: {row[1]}, カナ: {row[2]}, 東西: {row[3]}, 性別: {row[4]}")

    except sqlite3.Error as e:
        print(f"[NG] エラー: {e}")

    print()

    # 3. NL_CH（調教師マスター）テーブルのチェック
    print("【3. NL_CH（調教師マスター）テーブル】")
    print("-" * 80)

    try:
        # レコード数
        cursor.execute("SELECT COUNT(*) FROM NL_CH")
        record_count = cursor.fetchone()[0]
        print(f"[OK] レコード数: {record_count:,} 件")

        # ChokyosiCodeの一意性チェック
        cursor.execute("""
            SELECT ChokyosiCode, COUNT(*) as cnt
            FROM NL_CH
            GROUP BY ChokyosiCode
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"[NG] ChokyosiCodeの重複: {len(duplicates)} 件")
            for dup in duplicates[:5]:
                print(f"  - ChokyosiCode: {dup[0]}, 重複数: {dup[1]}")
        else:
            print("[OK] ChokyosiCodeの一意性: OK（重複なし）")

        # サンプルデータ3件を表示
        print("\n[OK] サンプルデータ（3件）:")
        cursor.execute("""
            SELECT ChokyosiCode, ChokyosiName, ChokyosiNameKana, TozaiCD, SexCD
            FROM NL_CH
            LIMIT 3
        """)
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f"  {i}. ChokyosiCode: {row[0]}, 調教師名: {row[1]}, カナ: {row[2]}, 東西: {row[3]}, 性別: {row[4]}")

    except sqlite3.Error as e:
        print(f"[NG] エラー: {e}")

    print()

    # 4. NL_BR（繁殖馬マスター）テーブルのチェック
    print("【4. NL_BR（繁殖馬マスター）テーブル】")
    print("-" * 80)

    try:
        # レコード数
        cursor.execute("SELECT COUNT(*) FROM NL_BR")
        record_count = cursor.fetchone()[0]
        print(f"[OK] レコード数: {record_count:,} 件")

        # サンプルデータ3件を表示
        print("\n[OK] サンプルデータ（3件）:")
        cursor.execute("""
            SELECT BreederCode, BreederName, BreederNameKana
            FROM NL_BR
            LIMIT 3
        """)
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f"  {i}. BreederCode: {row[0]}, 生産者名: {row[1]}, カナ: {row[2]}")

    except sqlite3.Error as e:
        print(f"[NG] エラー: {e}")

    print()

    # 5. 参照整合性チェック: NL_SEのKettoNumがNL_UMに存在するか
    print("【5. 参照整合性チェック】")
    print("-" * 80)

    try:
        # NL_SEテーブルの存在確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='NL_SE'")
        if cursor.fetchone():
            # NL_SEのレコード数
            cursor.execute("SELECT COUNT(*) FROM NL_SE")
            nl_se_count = cursor.fetchone()[0]
            print(f"[OK] NL_SE（成績）レコード数: {nl_se_count:,} 件")

            # サンプリングチェック（1000件をランダムにチェック）
            sample_size = min(1000, nl_se_count)
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM (
                    SELECT KettoNum
                    FROM NL_SE
                    LIMIT {sample_size}
                ) AS sample
                WHERE KettoNum NOT IN (SELECT KettoNum FROM NL_UM)
            """)
            missing_count = cursor.fetchone()[0]

            if missing_count > 0:
                print(f"[NG] 参照整合性エラー: サンプル{sample_size}件中、{missing_count}件のKettoNumがNL_UMに存在しません")

                # 具体例を表示
                cursor.execute(f"""
                    SELECT DISTINCT KettoNum
                    FROM (
                        SELECT KettoNum
                        FROM NL_SE
                        LIMIT {sample_size}
                    ) AS sample
                    WHERE KettoNum NOT IN (SELECT KettoNum FROM NL_UM)
                    LIMIT 5
                """)
                for row in cursor.fetchall():
                    print(f"  - 存在しないKettoNum: {row[0]}")
            else:
                print(f"[OK] 参照整合性チェック: OK（サンプル{sample_size}件すべてNL_UMに存在）")
        else:
            print("- NL_SEテーブルが存在しません（スキップ）")

    except sqlite3.Error as e:
        print(f"[NG] エラー: {e}")

    print()

    # テーブル一覧を表示
    print("【テーブル一覧】")
    print("-" * 80)
    try:
        cursor.execute("""
            SELECT name,
                   (SELECT COUNT(*) FROM sqlite_master sm2 WHERE sm2.name = sm1.name) as cnt
            FROM sqlite_master sm1
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        print(f"[OK] テーブル数: {len(tables)} 個")

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count:,} 件")
    except sqlite3.Error as e:
        print(f"[NG] エラー: {e}")

    print()
    print("=" * 80)
    print("チェック完了")
    print("=" * 80)

    conn.close()

if __name__ == "__main__":
    db_path = r"C:\Users\mitsu\work\jrvltsql\data\keiba.db"
    check_data_quality(db_path)
