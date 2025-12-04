#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Temporary validation script to check parser-schema mismatches
"""

import re
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.parser.factory import ALL_RECORD_TYPES
from src.database.schema import SCHEMAS


def extract_parser_fields(record_type):
    """Extract fields from parser file"""
    try:
        # Handle RT_ prefix
        parser_type = record_type.replace("RT_", "")

        # Read parser file
        parser_file = project_root / "src" / "parser" / f"{parser_type.lower()}_parser.py"
        if not parser_file.exists():
            return set()

        with open(parser_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract fields from result["FieldName"] = ...
        fields = set()

        # Remove comments
        lines = content.split('\n')
        clean_lines = []
        for line in lines:
            comment_pos = line.find('#')
            if comment_pos >= 0:
                line = line[:comment_pos]
            clean_lines.append(line)
        content = '\n'.join(clean_lines)

        # Pattern 1: result["FieldName"]
        pattern = r'result\["([^"]+)"\]'
        matches = re.findall(pattern, content)
        fields.update(matches)

        # Pattern 2: f-string result[f"...{i}..."]
        fstring_pattern = r'result\[f"([^"]+)\{([^}]+)\}([^"]*)"\]'
        fstring_matches = re.findall(fstring_pattern, content)
        for prefix, var, suffix in fstring_matches:
            # Find range
            range_pattern = rf'for\s+{var}\s+in\s+range\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)'
            range_match = re.search(range_pattern, content)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                for idx in range(start, end):
                    fields.add(f"{prefix}{idx}{suffix}")

        return fields
    except Exception as e:
        print(f"Warning: Failed to extract fields from {record_type}: {e}")
        return set()


def extract_schema_columns(table_name):
    """Extract columns from schema"""
    if table_name not in SCHEMAS:
        return set()

    schema_sql = SCHEMAS[table_name]
    columns = set()

    lines = schema_sql.split('\n')
    for line in lines:
        line = line.strip()

        # Skip non-column lines
        if (not line or
            line.startswith('--') or
            'CREATE TABLE' in line or
            'PRIMARY KEY' in line or
            line == ')'):
            continue

        # Extract column name
        match = re.match(r'(\w+)\s+(TEXT|INTEGER|REAL|BIGINT)', line)
        if match:
            column_name = match.group(1)
            columns.add(column_name)

    return columns


def get_table_mapping():
    """Build record type to table name mapping"""
    mapping = {}

    # NL_ tables
    for record_type in ALL_RECORD_TYPES:
        table_name = f"NL_{record_type}"
        if table_name in SCHEMAS:
            mapping[record_type] = table_name

    # RT_ tables
    rt_types = ['RA', 'SE', 'HR', 'O1', 'O2', 'O3', 'O4', 'O5', 'O6',
                'H1', 'H6', 'WE', 'WH', 'JC', 'CC', 'TC', 'TM', 'DM', 'AV']
    for rt_type in rt_types:
        rt_table_name = f"RT_{rt_type}"
        rt_record_type = f"RT_{rt_type}"
        if rt_table_name in SCHEMAS:
            mapping[rt_record_type] = rt_table_name

    return mapping


def main():
    print("=" * 60)
    print("Schema/Parser Validation Report")
    print("=" * 60)
    print()

    table_mapping = get_table_mapping()

    # Check all record types
    all_types = set(ALL_RECORD_TYPES)
    rt_types = ['RA', 'SE', 'HR', 'O1', 'O2', 'O3', 'O4', 'O5', 'O6',
                'H1', 'H6', 'WE', 'WH', 'JC', 'CC', 'TC', 'TM', 'DM', 'AV']
    for rt_type in rt_types:
        all_types.add(f"RT_{rt_type}")

    mismatches = []
    matches = 0

    for record_type in sorted(all_types):
        table_name = table_mapping.get(record_type)
        if not table_name:
            continue

        parser_fields = extract_parser_fields(record_type)
        schema_columns = extract_schema_columns(table_name)

        if not parser_fields or not schema_columns:
            continue

        # Case-insensitive comparison
        parser_fields_lower = {f.lower(): f for f in parser_fields}
        schema_columns_lower = {c.lower(): c for c in schema_columns}

        # Find differences
        extra_in_parser = []
        missing_in_parser = []

        for field_lower, field_original in parser_fields_lower.items():
            if field_lower not in schema_columns_lower:
                extra_in_parser.append(field_original)

        for column_lower, column_original in schema_columns_lower.items():
            if column_lower not in parser_fields_lower:
                missing_in_parser.append(column_original)

        if extra_in_parser or missing_in_parser:
            mismatches.append({
                'record_type': record_type,
                'table_name': table_name,
                'parser_count': len(parser_fields),
                'schema_count': len(schema_columns),
                'extra': sorted(extra_in_parser),
                'missing': sorted(missing_in_parser)
            })
        else:
            matches += 1

    print(f"Matched:    {matches}")
    print(f"Mismatched: {len(mismatches)}")
    print("=" * 60)
    print()

    if mismatches:
        print("MISMATCHES FOUND:")
        print()
        for mismatch in mismatches:
            print(f"[MISMATCH] {mismatch['record_type']}:")
            print(f"  Table:          {mismatch['table_name']}")
            print(f"  Parser fields:  {mismatch['parser_count']}")
            print(f"  Schema columns: {mismatch['schema_count']}")

            if mismatch['extra']:
                print(f"  Extra in parser ({len(mismatch['extra'])}):")
                for field in mismatch['extra']:
                    print(f"    - {field}")

            if mismatch['missing']:
                print(f"  Missing in parser ({len(mismatch['missing'])}):")
                for field in mismatch['missing']:
                    print(f"    - {field}")

            print()
    else:
        print("No mismatches found!")

    return 1 if mismatches else 0


if __name__ == '__main__':
    sys.exit(main())
