#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyze the current state of data in keiba.db
"""

import sqlite3
import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r'C:\Users\mitsu\work\jrvltsql\data\keiba.db'

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return

    print(f"📊 Analyzing database: {DB_PATH}\n")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Check NL_SE table
    print("\n🔍 1. NL_SE TABLE ANALYSIS")
    print("-" * 80)

    try:
        # Total record count
        cursor.execute("SELECT COUNT(*) FROM NL_SE")
        total_count = cursor.fetchone()[0]
        print(f"Total records: {total_count:,}")

        if total_count > 0:
            # Count records with valid Bamei (no '?' characters)
            cursor.execute("SELECT COUNT(*) FROM NL_SE WHERE Bamei NOT LIKE '%?%'")
            valid_bamei = cursor.fetchone()[0]
            print(f"Records with valid Bamei (no '?' chars): {valid_bamei:,} ({valid_bamei/total_count*100:.1f}%)")

            # Count records with corrupted Bamei (has '?' characters)
            corrupted_bamei = total_count - valid_bamei
            print(f"Records with corrupted Bamei (has '?' chars): {corrupted_bamei:,} ({corrupted_bamei/total_count*100:.1f}%)")

            # Count records with valid IJyoCD (values 0-6 only)
            cursor.execute("SELECT COUNT(*) FROM NL_SE WHERE IJyoCD IN ('0','1','2','3','4','5','6')")
            valid_ijyocd = cursor.fetchone()[0]
            print(f"Records with valid IJyoCD (0-6): {valid_ijyocd:,} ({valid_ijyocd/total_count*100:.1f}%)")

            # Count records with valid KakuteiJyuni (non-null, non-zero)
            cursor.execute("SELECT COUNT(*) FROM NL_SE WHERE KakuteiJyuni IS NOT NULL AND KakuteiJyuni != '' AND KakuteiJyuni != '0' AND KakuteiJyuni != '00'")
            valid_kakutei = cursor.fetchone()[0]
            print(f"Records with valid KakuteiJyuni (non-null, non-zero): {valid_kakutei:,} ({valid_kakutei/total_count*100:.1f}%)")

            # Sample some Bamei values to show examples
            print("\n📝 Sample Bamei values (first 10):")
            cursor.execute("SELECT Bamei, Year, MonthDay, JyoCD FROM NL_SE LIMIT 10")
            for i, row in enumerate(cursor.fetchall(), 1):
                bamei, year, monthday, jyocd = row
                print(f"  {i}. {bamei} (Year: {year}, MonthDay: {monthday}, JyoCD: {jyocd})")

            # Check for recent records (if Year field exists and is recent)
            print("\n📅 Recent records check:")
            cursor.execute("SELECT Year, COUNT(*) as cnt FROM NL_SE GROUP BY Year ORDER BY Year DESC LIMIT 5")
            year_counts = cursor.fetchall()
            for year, cnt in year_counts:
                print(f"  Year {year}: {cnt:,} records")

    except sqlite3.Error as e:
        print(f"❌ Error analyzing NL_SE: {e}")

    # 2. Check NL_RA table
    print("\n\n🔍 2. NL_RA TABLE ANALYSIS")
    print("-" * 80)

    try:
        cursor.execute("SELECT COUNT(*) FROM NL_RA")
        total_ra = cursor.fetchone()[0]
        print(f"Total records: {total_ra:,}")

        if total_ra > 0:
            # Sample Bamei values
            print("\n📝 Sample Bamei values (first 10):")
            cursor.execute("SELECT Bamei, KettoNum FROM NL_RA LIMIT 10")
            for i, row in enumerate(cursor.fetchall(), 1):
                bamei, kettonum = row
                print(f"  {i}. {bamei} (KettoNum: {kettonum})")

            # Count valid vs corrupted Bamei
            cursor.execute("SELECT COUNT(*) FROM NL_RA WHERE Bamei NOT LIKE '%?%'")
            valid_bamei_ra = cursor.fetchone()[0]
            corrupted_bamei_ra = total_ra - valid_bamei_ra
            print(f"\nValid Bamei (no '?'): {valid_bamei_ra:,} ({valid_bamei_ra/total_ra*100:.1f}%)")
            print(f"Corrupted Bamei (has '?'): {corrupted_bamei_ra:,} ({corrupted_bamei_ra/total_ra*100:.1f}%)")

    except sqlite3.Error as e:
        print(f"❌ Error analyzing NL_RA: {e}")

    # 3. Check for RT_* tables (realtime tables)
    print("\n\n🔍 3. REALTIME TABLES (RT_*) ANALYSIS")
    print("-" * 80)

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'RT_%' ORDER BY name")
        rt_tables = cursor.fetchall()

        if rt_tables:
            print(f"Found {len(rt_tables)} realtime tables:\n")
            for (table_name,) in rt_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  📋 {table_name}: {count:,} records")

                # If it's RT_SE, check Bamei encoding
                if table_name == 'RT_SE' and count > 0:
                    print(f"     Sample Bamei from {table_name}:")
                    cursor.execute(f"SELECT Bamei FROM {table_name} LIMIT 5")
                    for i, (bamei,) in enumerate(cursor.fetchall(), 1):
                        print(f"       {i}. {bamei}")
        else:
            print("No realtime tables (RT_*) found in database.")

    except sqlite3.Error as e:
        print(f"❌ Error checking RT_* tables: {e}")

    # 4. List all tables in database
    print("\n\n🔍 4. ALL TABLES IN DATABASE")
    print("-" * 80)

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        all_tables = cursor.fetchall()
        print(f"Total tables: {len(all_tables)}\n")
        for (table_name,) in all_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count:,} records")
    except sqlite3.Error as e:
        print(f"❌ Error listing tables: {e}")

    # 5. Summary
    print("\n\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)

    try:
        cursor.execute("SELECT COUNT(*) FROM NL_SE")
        nl_se_total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM NL_SE WHERE Bamei NOT LIKE '%?%'")
        nl_se_valid = cursor.fetchone()[0]

        if nl_se_total > 0:
            corruption_rate = (nl_se_total - nl_se_valid) / nl_se_total * 100

            print(f"\n✅ NL_SE table exists with {nl_se_total:,} records")
            print(f"   - Valid Bamei: {nl_se_valid:,} ({100-corruption_rate:.1f}%)")
            print(f"   - Corrupted Bamei: {nl_se_total - nl_se_valid:,} ({corruption_rate:.1f}%)")

            if corruption_rate > 50:
                print("\n⚠️  CONCLUSION: Most data appears to be corrupted (pre-encoding-fix)")
                print("   Recommendation: Re-import data with the fixed importer to resolve encoding issues")
            elif corruption_rate > 0:
                print("\n⚠️  CONCLUSION: Some data is corrupted (mixed old and new data)")
                print("   Some records may have been imported before the encoding fix")
            else:
                print("\n✅ CONCLUSION: All data appears valid (post-encoding-fix)")
                print("   The encoding fix has been successfully applied!")
        else:
            print("\n⚠️  Database is empty or NL_SE table has no records")

    except sqlite3.Error as e:
        print(f"❌ Error generating summary: {e}")

    conn.close()
    print("\n" + "=" * 80)
    print("✅ Analysis complete!")

if __name__ == '__main__':
    main()
