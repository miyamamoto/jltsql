#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check encoding issues in the database."""

import sqlite3
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = sqlite3.connect('C:/Users/mitsu/work/jrvltsql/data/keiba.db')
cursor = conn.cursor()

# Count records with question marks in Bamei
cursor.execute("SELECT COUNT(*) FROM NL_UM WHERE Bamei LIKE '%?%'")
qmark_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM NL_UM")
total = cursor.fetchone()[0]

print(f"NL_UM total: {total}")
print(f"NL_UM with '?': {qmark_count} ({100*qmark_count/total:.1f}%)")

# Get a few samples
cursor.execute("SELECT Bamei, BameiKana FROM NL_UM WHERE Bamei IS NOT NULL LIMIT 5")
print()
print("=== Samples (Bamei vs BameiKana) ===")
for row in cursor.fetchall():
    bamei = row[0] or ''
    kana = row[1] or ''
    print(f"  Bamei: {bamei}")
    print(f"  Kana:  {kana}")
    # Check byte representation
    if bamei:
        utf8_bytes = bamei.encode('utf-8', errors='replace')
        print(f"  Bytes: {utf8_bytes[:30].hex()}")
    print()

conn.close()
