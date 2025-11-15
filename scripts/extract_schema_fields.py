#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Extract field names from JRA-VAN standard schema."""

import re
from pathlib import Path
from typing import Dict, List

def extract_table_fields(schema_file: Path) -> Dict[str, List[str]]:
    """Extract field names for each table from schema file.

    Returns:
        Dict mapping table name to list of field names
    """
    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()

    tables = {}

    # Split by table sections
    table_sections = re.split(r'^Table: (.+)$', content, flags=re.MULTILINE)

    for i in range(1, len(table_sections), 2):
        table_name = table_sections[i].strip()
        table_content = table_sections[i + 1]

        # Extract field names
        field_pattern = r'^\d+\s+(\w+)\s+TEXT'
        fields = re.findall(field_pattern, table_content, re.MULTILINE)

        if fields:
            tables[table_name] = fields

    return tables

def main():
    """Extract and display field names."""
    project_root = Path(__file__).parent.parent
    schema_file = project_root / "reference_data" / "jravan_standard_schema.txt"

    tables = extract_table_fields(schema_file)

    print(f"Extracted {len(tables)} tables")
    print()

    # Map record types to table names
    record_to_table = {
        "RA": "RACE",
        "SE": "UMA_RACE",
        "HR": "HARAI",
        "UM": "UMA",
        "KS": "KISYU",
        "CH": "CHOKYOSI",
        "BR": "KEIBABREEDER",
        "BN": "BANUSI",
        "HN": "HANRO",
    }

    # Display field mappings for key tables
    for record_type, table_name in record_to_table.items():
        if table_name in tables:
            fields = tables[table_name]
            print(f"\n{record_type} -> {table_name} ({len(fields)} fields):")
            for i, field in enumerate(fields[:20], 1):  # First 20 fields
                print(f"  {i:2d}. {field}")
            if len(fields) > 20:
                print(f"  ... and {len(fields) - 20} more")

if __name__ == '__main__':
    main()
