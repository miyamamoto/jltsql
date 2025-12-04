#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Quality Summary Report
"""

import sqlite3
import os
import re
import sys
from datetime import datetime

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"C:\Users\mitsu\work\jrvltsql\data\keiba.db"

def get_file_size(path):
    """Get file size in human readable format"""
    size = os.path.getsize(path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def estimate_mojibake_rate(conn, table_name, text_columns, sample_size=1000):
    """Estimate mojibake (garbled text) rate"""
    if not text_columns:
        return 0.0

    column = text_columns[0]
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]

        if total_count == 0:
            return 0.0

        actual_sample = min(sample_size, total_count)
        cursor.execute(f"SELECT {column} FROM {table_name} WHERE {column} IS NOT NULL LIMIT {actual_sample}")

        mojibake_count = 0
        valid_count = 0

        for row in cursor.fetchall():
            value = row[0]
            if value and isinstance(value, str):
                valid_count += 1
                # Detect mojibake patterns
                if (re.search(r'[縺繧�?]+', value) or
                    re.search(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', value) or
                    re.search(r'[■�]{2,}', value)):
                    mojibake_count += 1

        if valid_count == 0:
            return 0.0

        return (mojibake_count / valid_count) * 100

    except Exception as e:
        return 0.0

def get_latest_dates(conn):
    """Get latest dates from all tables"""
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    latest_dates = []
    
    # Check MakeDate column in each table
    for table in tables:
        try:
            cursor.execute(f'SELECT MAX(MakeDate) FROM {table}')
            result = cursor.fetchone()[0]
            if result:
                latest_dates.append((table, result))
        except:
            pass
    
    return latest_dates

def format_date(date_str):
    """Format YYYYMMDD to YYYY-MM-DD"""
    if len(date_str) == 8:
        return f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
    return date_str

def analyze_database():
    """Analyze database and generate quality summary"""
    print("=" * 80)
    print("DATABASE QUALITY SUMMARY REPORT")
    print("=" * 80)
    print()

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. File size
    file_size = get_file_size(DB_PATH)
    file_size_raw = os.path.getsize(DB_PATH)
    
    # 2. Total tables
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    table_count = cursor.fetchone()[0]
    
    # Get table list
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    # 3. Total records
    total_records = 0
    table_records = {}
    tables_with_data = []
    empty_tables = []

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        table_records[table] = count
        total_records += count
        if count > 0:
            tables_with_data.append((table, count))
        else:
            empty_tables.append(table)

    # 4. Mojibake rate estimation
    mojibake_rates = []
    for table in tables:
        if table_records[table] == 0:
            continue
            
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()

        # Extract TEXT columns
        text_columns = [col[1] for col in columns if 'TEXT' in col[2].upper() or 'CHAR' in col[2].upper()]

        if text_columns:
            rate = estimate_mojibake_rate(conn, table, text_columns, sample_size=1000)
            mojibake_rates.append((table, text_columns[0], rate))

    avg_mojibake_rate = sum(r[2] for r in mojibake_rates) / len(mojibake_rates) if mojibake_rates else 0.0

    # 5. Latest dates
    latest_dates = get_latest_dates(conn)
    overall_latest = max(d[1] for d in latest_dates) if latest_dates else None

    # Print summary
    print("1. DB FILE SIZE")
    print(f"   Size: {file_size} ({file_size_raw:,} bytes)")
    print()

    print("2. TOTAL TABLES")
    print(f"   Total: {table_count} tables")
    print(f"   - Tables with data: {len(tables_with_data)}")
    print(f"   - Empty tables: {len(empty_tables)}")
    print()

    print("3. TOTAL RECORDS")
    print(f"   Total: {total_records:,} records")
    print()
    print("   Top 10 tables by record count:")
    for table, count in sorted(tables_with_data, key=lambda x: x[1], reverse=True)[:10]:
        print(f"   - {table}: {count:,} records")
    print()

    print("4. DATA QUALITY - MOJIBAKE RATE")
    print(f"   Average mojibake rate: {avg_mojibake_rate:.2f}%")
    if avg_mojibake_rate > 10:
        print("   Status: ⚠️  WARNING - High mojibake rate detected")
    elif avg_mojibake_rate > 0:
        print("   Status: ℹ️  NOTE - Some mojibake detected")
    else:
        print("   Status: ✅ OK - No mojibake detected")
    print(f"   (Sampled from {len(mojibake_rates)} tables with text columns)")
    print()

    print("5. LATEST DATA DATE")
    if overall_latest:
        formatted_date = format_date(overall_latest)
        print(f"   Latest date: {formatted_date} ({overall_latest})")
        print()
        print("   Top 5 tables with latest dates:")
        for table, date in sorted(latest_dates, key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - {table}: {format_date(date)}")
    else:
        print("   No date information found")
    print()

    # Final summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ File Size:         {file_size}")
    print(f"✓ Tables:            {table_count} ({len(tables_with_data)} with data)")
    print(f"✓ Total Records:     {total_records:,}")
    print(f"✓ Data Quality:      {avg_mojibake_rate:.2f}% mojibake rate")
    if overall_latest:
        print(f"✓ Latest Data:       {format_date(overall_latest)}")
    print("=" * 80)

    conn.close()

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found: {DB_PATH}")
        exit(1)

    analyze_database()
