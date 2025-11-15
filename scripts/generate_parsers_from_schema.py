#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate JRA-VAN standard compliant parsers using schema field names."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

# Record type to JRA-VAN table name mapping
# Based on src/database/table_mappings.py and JRA-VAN standard schema
RECORD_TO_TABLE = {
    # Main records (100% coverage achieved)
    "RA": "RACE",
    "SE": "UMA_RACE",
    "HR": "HARAI",
    "UM": "UMA",
    "KS": "KISYU",
    "CH": "CHOKYO",
    "BR": "HANSYOKU",
    "BN": "SEISAN",
    "HN": "BANUSI",
    "YS": "SCHEDULE",

    # Odds records
    "H1": "ODDS_TANPUKU",
    "H6": "ODDS_TANPUKUWAKU_HEAD",
    "O1": "ODDS_UMAREN",
    "O2": "ODDS_WIDE",
    "O3": "ODDS_WAKU",
    "O4": "ODDS_UMATAN",
    "O5": "ODDS_SANREN",
    "O6": "ODDS_SANRENTAN",

    # Info/Change records
    "AV": "SALE",
    "JC": "KISYU_CHANGE",
    "JG": "TORIKESI_JYOGAI",
    "TC": "HASSOU_JIKOKU_CHANGE",
    "CC": "COURSE_CHANGE",
    "TK": "TOKU",
    "SK": "COURSE",
    "WH": "TENKO_BABA",

    # Mining/Data records
    "DM": "TAISENGATA_MINING",
    "TM": "MINING",
    "BT": "CHOKYO",
    "RC": "RECORD",

    # Note: Still need manual mapping for complex records
    # CK (勝利騎手コメント), CS, HC, HS, HY, WC, WE, WF
}

# Type conversion mapping based on field semantics
TYPE_CONVERSION_MAPPING = {
    "MakeDate": "DATE",
    "RegDate": "DATE",
    "DelDate": "DATE",
    "BirthDate": "DATE",
    "IssueDate": "DATE",
    "ChokyoDate": "DATE",

    "Year": "SMALLINT",
    "MonthDay": "MONTH_DAY",
    "Kaiji": "SMALLINT",
    "Nichiji": "SMALLINT",
    "RaceNum": "SMALLINT",
    "Nkai": "SMALLINT",
    "Kyori": "SMALLINT",
    "KyoriBefore": "SMALLINT",
    "TorokuTosu": "SMALLINT",
    "SyussoTosu": "SMALLINT",
    "NyusenTosu": "SMALLINT",
    "NyusenJyuni": "SMALLINT",
    "KakuteiJyuni": "SMALLINT",
    "Ninki": "SMALLINT",
    "Barei": "SMALLINT",
    "BaTaijyu": "SMALLINT",
    "ZogenSa": "SMALLINT",
    "Wakuban": "SMALLINT",
    "Umaban": "SMALLINT",
    "Jyuni1c": "SMALLINT",
    "Jyuni2c": "SMALLINT",
    "Jyuni3c": "SMALLINT",
    "Jyuni4c": "SMALLINT",

    "HassoTime": "TIME",
    "ChokyoTime": "TIME",
    "HappyoTime": "TIME",

    "Futan": "WEIGHT",
    "FutanBefore": "WEIGHT",

    "Time": "RACE_TIME",
    "SyogaiMileTime": "RACE_TIME",
    "DMTime": "RACE_TIME",

    "Odds": "ODDS",

    "Honsyokin": "PRIZE_MONEY",
    "Honsyokin1": "PRIZE_MONEY",
    "Honsyokin2": "PRIZE_MONEY",
    "Honsyokin3": "PRIZE_MONEY",
    "Honsyokin4": "PRIZE_MONEY",
    "Honsyokin5": "PRIZE_MONEY",
    "Honsyokin6": "PRIZE_MONEY",
    "Honsyokin7": "PRIZE_MONEY",
    "Fukasyokin": "PRIZE_MONEY",
    "Fukasyokin1": "PRIZE_MONEY",
    "Fukasyokin2": "PRIZE_MONEY",
    "Fukasyokin3": "PRIZE_MONEY",
    "Fukasyokin4": "PRIZE_MONEY",
    "Fukasyokin5": "PRIZE_MONEY",

    "HaronTimeS3": "LAP_TIME",
    "HaronTimeS4": "LAP_TIME",
    "HaronTimeL3": "LAP_TIME",
    "HaronTimeL4": "LAP_TIME",
    "HaronTime2": "LAP_TIME",
    "HaronTime3": "LAP_TIME",
    "HaronTime4": "LAP_TIME",
}

# Add LapTime1-25
for i in range(1, 26):
    TYPE_CONVERSION_MAPPING[f"LapTime{i}"] = "LAP_TIME"


def extract_schema_fields(schema_file: Path) -> Dict[str, List[str]]:
    """Extract field names from JRA-VAN standard schema.

    Returns:
        Dict mapping table name to list of field names
    """
    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()

    tables = {}
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


def get_convert_type(field_name: str) -> Optional[str]:
    """Get convert_type for a field based on field name."""
    return TYPE_CONVERSION_MAPPING.get(field_name)


def generate_parser(
    record_type: str,
    jv_fields: List[Dict],
    schema_fields: List[str],
    output_dir: Path
) -> None:
    """Generate a JRA-VAN standard compliant parser.

    Args:
        record_type: Record type code (e.g., "RA", "SE")
        jv_fields: Field definitions from jv_data_formats.json
        schema_fields: Field names from JRA-VAN standard schema (in order)
        output_dir: Output directory for parser file
    """
    parser_name = f"{record_type}Parser"
    output_file = output_dir / f"{record_type.lower()}_parser.py"

    # Generate field definitions
    field_defs = []
    for i, jv_field in enumerate(jv_fields):
        # Get field name from schema (by order/index)
        if i < len(schema_fields):
            field_name = schema_fields[i]
        else:
            # Fallback: use Japanese name if schema doesn't have enough fields
            field_name = jv_field["name"]
            print(f"  Warning: Using Japanese name for field {i+1}: {field_name}")

        position = jv_field["position"] - 1  # Convert to 0-indexed
        length = jv_field["length"]
        japanese_desc = jv_field["name"]
        convert_type = get_convert_type(field_name)

        if convert_type:
            field_def = f'            FieldDef("{field_name}", {position}, {length}, convert_type="{convert_type}", description="{japanese_desc}"),'
        else:
            field_def = f'            FieldDef("{field_name}", {position}, {length}, description="{japanese_desc}"),'

        field_defs.append(field_def)

    # Generate parser class
    parser_code = f'''"""Parser for {record_type} record - JRA-VAN Standard compliant.

This parser uses JRA-VAN standard field names and type conversions.
Generated from jv_data_formats.json and JRA-VAN standard schema.
"""

from typing import List

from src.parser.base import BaseParser, FieldDef


class {parser_name}(BaseParser):
    """Parser for {record_type} record with JRA-VAN standard schema.

    Uses English/Romanized field names matching JRA-VAN standard database.
    """

    record_type = "{record_type}"

    def _define_fields(self) -> List[FieldDef]:
        """Define field positions with JRA-VAN standard names and types.

        Returns:
            List of FieldDef objects with type conversion settings
        """
        return [
{chr(10).join(field_defs)}
        ]
'''

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(parser_code)

    print(f"  Generated: {output_file.name}")


def main():
    """Generate all parsers from JRA-VAN standard schema."""
    project_root = Path(__file__).parent.parent
    formats_file = project_root / "jv_data_formats.json"
    schema_file = project_root / "reference_data" / "jravan_standard_schema.txt"
    output_dir = project_root / "src" / "parser"

    # Load JV-Data formats
    with open(formats_file, 'r', encoding='utf-8') as f:
        formats = json.load(f)

    # Load JRA-VAN standard schema
    schema_tables = extract_schema_fields(schema_file)

    print(f"Generating JRA-VAN standard parsers...")
    print(f"  JV formats: {formats_file}")
    print(f"  Schema: {schema_file}")
    print(f"  Output: {output_dir}")
    print()

    generated_count = 0
    for record_type, record_info in formats.items():
        jv_fields = record_info.get("fields", [])
        if not jv_fields:
            print(f"Skipping {record_type}: No fields defined")
            continue

        # Get corresponding table from schema
        table_name = RECORD_TO_TABLE.get(record_type)
        if not table_name:
            print(f"Skipping {record_type}: No table mapping")
            continue

        schema_fields = schema_tables.get(table_name)
        if not schema_fields:
            print(f"Skipping {record_type}: Table {table_name} not found in schema")
            continue

        print(f"{record_type} -> {table_name} ({len(jv_fields)} JV fields, {len(schema_fields)} schema fields)")

        generate_parser(record_type, jv_fields, schema_fields, output_dir)
        generated_count += 1

    print()
    print(f"Generated {generated_count} parsers successfully")


if __name__ == '__main__':
    main()
