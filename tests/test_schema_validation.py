#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick script to identify failing table schemas."""

import sys
from pathlib import Path
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import tempfile

from src.database.schema import SCHEMAS, SchemaManager
from src.database.sqlite_handler import SQLiteDatabase

# Create temp database
temp_dir = tempfile.TemporaryDirectory()
db_path = Path(temp_dir.name) / 'test.db'

db = SQLiteDatabase({'path': str(db_path)})
db.connect()

schema_manager = SchemaManager(db)

print(f"\nTesting {len(SCHEMAS)} table schemas...\n")

success_count = 0
fail_count = 0
failed_tables = []

for table_name in sorted(SCHEMAS.keys()):
    try:
        result = schema_manager.create_table(table_name)
        if result:
            success_count += 1
            print(f"[OK] {table_name}")
        else:
            fail_count += 1
            failed_tables.append(table_name)
            print(f"[FAIL] {table_name} - Failed to create")
    except Exception as e:
        fail_count += 1
        failed_tables.append(table_name)
        print(f"[ERROR] {table_name} - {str(e)[:80]}")

print(f"\n" + "="*60)
print(f"Results: {success_count} succeeded, {fail_count} failed")
print(f"="*60)

if failed_tables:
    print(f"\nFailed tables ({len(failed_tables)}):")
    for table in failed_tables:
        print(f"  - {table}")

db.disconnect()
temp_dir.cleanup()
