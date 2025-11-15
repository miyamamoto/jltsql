#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Extract CREATE TABLE statements from VB source code."""

import re
import sys

def extract_table_definitions(vb_file_path):
    """Extract CREATE TABLE statements from VB file."""
    with open(vb_file_path, 'r', encoding='shift_jis', errors='ignore') as f:
        content = f.read()

    # Find all CREATE TABLE statements
    # Pattern: strSql = "CREATE TABLE tablename (" followed by multiple strSql = strSql & "field TEXT(n),"

    # Split by CREATE TABLE
    tables = {}
    current_table = None
    current_fields = []

    for line in content.split('\n'):
        # Check for CREATE TABLE
        create_match = re.search(r'strSql = "CREATE TABLE (\w+) \(', line)
        if create_match:
            # Save previous table if exists
            if current_table:
                tables[current_table] = current_fields

            current_table = create_match.group(1)
            current_fields = []
            continue

        # Check for field definitions
        field_match = re.search(r'strSql = strSql & "(\[?\w+\]?)\s+(TEXT\(\d+\)|TEXT|INTEGER|DATETIME|REAL|YESNO)(?:\s*\(\d+\))?,?"', line)
        if field_match and current_table:
            field_name = field_match.group(1).strip('[]')
            field_type = field_match.group(2)
            current_fields.append((field_name, field_type))
            continue

        # Check for ExecuteNonQuery (end of table definition)
        if 'ExecuteNonQuery' in line and current_table:
            tables[current_table] = current_fields
            current_table = None
            current_fields = []

    return tables

def main():
    vb_file = r'C:\Users\mitsu\jltsql\reference_data\VB2019-Builder\データベース作成VisualBasic2019\clsDBBuilder.vb'
    output_file = r'C:\Users\mitsu\jltsql\reference_data\jravan_standard_schema.txt'

    print(f"Extracting table definitions from: {vb_file}")
    tables = extract_table_definitions(vb_file)

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("JRA-VAN Standard Database Schema (extracted from VB2019-Builder)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total Tables: {len(tables)}\n\n")

        for table_name, fields in sorted(tables.items()):
            f.write("-" * 80 + "\n")
            f.write(f"Table: {table_name}\n")
            f.write("-" * 80 + "\n")
            f.write(f"Fields: {len(fields)}\n\n")

            f.write(f"{'No':<5} {'Field Name':<40} {'Data Type':<20}\n")
            f.write(f"{'---':<5} {'-----------':<40} {'---------':<20}\n")

            for idx, (field_name, field_type) in enumerate(fields, 1):
                f.write(f"{idx:<5} {field_name:<40} {field_type:<20}\n")

            f.write("\n")

    print(f"\nExtraction completed!")
    print(f"Output saved to: {output_file}")
    print(f"Total tables extracted: {len(tables)}")

    # Print summary
    print("\nTable names:")
    for table_name in sorted(tables.keys()):
        field_count = len(tables[table_name])
        print(f"  - {table_name}: {field_count} fields")

if __name__ == '__main__':
    main()
