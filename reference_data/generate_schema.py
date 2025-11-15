#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate Python schema definitions from VB Builder source code."""

import re
from pathlib import Path

# Data type mapping: JV-Data -> PostgreSQL/DuckDB types
TYPE_MAPPING = {
    # 日付・時刻系
    'MakeDate': ('DATE', 'YYYYMMDD形式の日付'),
    'Year': ('SMALLINT', '年(4桁)'),
    'MonthDay': ('SMALLINT', '月日(MMDD)'),
    'HassoTime': ('TIME', '発走時刻(HHMM)'),
    'HappyoTime': ('TIMESTAMP', '発表時刻'),
    'IssueDate': ('DATE', '免許交付年月日'),
    'DelDate': ('DATE', '抹消年月日'),
    'BirthDate': ('DATE', '生年月日'),

    # 整数系（コード・番号）
    'RecordSpec': ('CHAR(2)', 'レコード種別ID'),
    'DataKubun': ('CHAR(1)', 'データ区分'),
    'JyoCD': ('CHAR(2)', '競馬場コード'),
    'Kaiji': ('SMALLINT', '開催回'),
    'Nichiji': ('SMALLINT', '開催日目'),
    'RaceNum': ('SMALLINT', 'レース番号'),
    'Umaban': ('SMALLINT', '馬番'),
    'Wakuban': ('SMALLINT', '枠番'),

    # 整数系（頭数・回数）
    'TorokuTosu': ('SMALLINT', '登録頭数'),
    'SyussoTosu': ('SMALLINT', '出走頭数'),
    'NyusenTosu': ('SMALLINT', '入選頭数'),
    'Barei': ('SMALLINT', '馬齢'),
    'Nkai': ('SMALLINT', '第N回'),

    # 整数系（距離・体重）
    'Kyori': ('SMALLINT', '距離(m)'),
    'KyoriBefore': ('SMALLINT', '変更前距離'),
    'BaTaijyu': ('SMALLINT', '馬体重(kg)'),
    'ZogenSa': ('SMALLINT', '増減(kg)'),

    # 整数系（着順・人気）
    'NyusenJyuni': ('SMALLINT', '入線順位'),
    'KakuteiJyuni': ('SMALLINT', '確定着順'),
    'Ninki': ('SMALLINT', '人気'),
    'Jyuni1c': ('SMALLINT', '1コーナー順位'),
    'Jyuni2c': ('SMALLINT', '2コーナー順位'),
    'Jyuni3c': ('SMALLINT', '3コーナー順位'),
    'Jyuni4c': ('SMALLINT', '4コーナー順位'),

    # 整数系（賞金 - 千円単位）
    'Honsyokin': ('INTEGER', '本賞金(千円)'),
    'Fukasyokin': ('INTEGER', '付加賞金(千円)'),
    'Honsyokin1': ('INTEGER', '1着本賞金'),
    'Honsyokin2': ('INTEGER', '2着本賞金'),
    'Honsyokin3': ('INTEGER', '3着本賞金'),
    'Honsyokin4': ('INTEGER', '4着本賞金'),
    'Honsyokin5': ('INTEGER', '5着本賞金'),
    'Honsyokin6': ('INTEGER', '6着本賞金'),
    'Honsyokin7': ('INTEGER', '7着本賞金'),
    'Fukasyokin1': ('INTEGER', '1着付加賞金'),
    'Fukasyokin2': ('INTEGER', '2着付加賞金'),
    'Fukasyokin3': ('INTEGER', '3着付加賞金'),
    'Fukasyokin4': ('INTEGER', '4着付加賞金'),
    'Fukasyokin5': ('INTEGER', '5着付加賞金'),

    # DECIMAL系（斤量）
    'Futan': ('DECIMAL(4,1)', '斤量(kg)'),
    'FutanBefore': ('DECIMAL(4,1)', '変更前斤量'),

    # DECIMAL系（タイム）
    'Time': ('DECIMAL(5,1)', '走破タイム(秒)'),
    'HaronTimeL3': ('DECIMAL(4,1)', '後3F(秒)'),
    'HaronTimeL4': ('DECIMAL(4,1)', '後4F(秒)'),
    'HaronTimeS3': ('DECIMAL(4,1)', '前3F(秒)'),
    'HaronTimeS4': ('DECIMAL(4,1)', '前4F(秒)'),
    'LapTime1': ('DECIMAL(4,1)', 'ラップタイム1(秒)'),
    'LapTime2': ('DECIMAL(4,1)', 'ラップタイム2'),
    'LapTime3': ('DECIMAL(4,1)', 'ラップタイム3'),
    'SyogaiMileTime': ('DECIMAL(5,1)', '障害マイルタイム'),
    'DMTime': ('DECIMAL(6,1)', 'DMタイム'),

    # DECIMAL系（オッズ）
    'Odds': ('DECIMAL(6,1)', 'オッズ'),

    # その他TEXT型
    # (ここにリストされていないフィールドはデフォルトでVARCHAR)
}

def get_pg_type(field_name, vb_type):
    """Get PostgreSQL type for a field."""
    # Check if field has specific type mapping
    if field_name in TYPE_MAPPING:
        pg_type, comment = TYPE_MAPPING[field_name]
        return pg_type, comment

    # Pattern matching for repetitive fields (e.g. LapTime4, LapTime5, ...)
    for pattern, (pg_type, comment) in TYPE_MAPPING.items():
        if re.match(pattern + r'\d+', field_name):
            return pg_type, comment.replace('1', field_name[-1])

    # Default mapping based on VB type
    if 'TEXT(' in vb_type:
        size = re.search(r'TEXT\((\d+)\)', vb_type)
        if size:
            length = int(size.group(1))
            if length <= 10:
                return f'VARCHAR({length})', f'文字列({length})'
            else:
                return f'VARCHAR({length})', f'文字列({length})'

    return 'VARCHAR(255)', 'テキスト'

def extract_create_table_statements(vb_file):
    """Extract CREATE TABLE statements from VB file."""
    with open(vb_file, 'r', encoding='shift_jis', errors='ignore') as f:
        content = f.read()

    tables = {}
    current_table = None
    current_fields = []

    for line in content.split('\n'):
        # CREATE TABLE
        create_match = re.search(r'strSql = "CREATE TABLE (\w+) \(', line)
        if create_match:
            if current_table:
                tables[current_table] = current_fields
            current_table = create_match.group(1)
            current_fields = []
            continue

        # Field definitions
        field_match = re.search(r'strSql = strSql & "(\[?\w+\]?)\s+(TEXT\(\d+\)|TEXT|INTEGER|DATETIME|REAL|YESNO)(?:\s*\(\d+\))?,?"', line)
        if field_match and current_table:
            field_name = field_match.group(1).strip('[]')
            vb_type = field_match.group(2)
            pg_type, comment = get_pg_type(field_name, vb_type)
            current_fields.append((field_name, pg_type, comment))
            continue

        # End of table
        if 'ExecuteNonQuery' in line and current_table:
            tables[current_table] = current_fields
            current_table = None
            current_fields = []

    return tables

def generate_schema_python(tables, output_file):
    """Generate Python schema definition file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('"""JRA-VAN Standard Database Schema Definitions.\n\n')
        f.write('Auto-generated from VB2019-Builder source code.\n')
        f.write('Compatible with PostgreSQL, DuckDB, MySQL.\n')
        f.write('"""\n\n')
        f.write('from typing import Dict\n\n\n')
        f.write('# JRA-VAN Standard Schema (52 tables)\n')
        f.write('JRAVAN_SCHEMAS: Dict[str, str] = {\n')

        for table_name in sorted(tables.keys()):
            fields = tables[table_name]
            f.write(f'    "{table_name}": """\n')
            f.write(f'        CREATE TABLE IF NOT EXISTS {table_name} (\n')

            # Write fields
            for i, (field_name, pg_type, comment) in enumerate(fields):
                comma = ',' if i < len(fields) - 1 else ''
                f.write(f'            {field_name:<30} {pg_type:<20}{comma}  -- {comment}\n')

            # TODO: Add PRIMARY KEY based on table structure
            # For now, we'll add it manually for important tables

            f.write('        )\n')
            f.write('    """,\n')

        f.write('}\n')

def generate_table_mapping(tables, output_file):
    """Generate table name mapping file (old jltsql -> JRA-VAN standard)."""
    # Manual mapping of known tables
    KNOWN_MAPPINGS = {
        'RACE': 'NL_RA',
        'UMA_RACE': 'NL_SE',
        'HARAI': 'NL_HR',
        'UMA': 'NL_UM',
        'KISYU': 'NL_KS',
        'CHOKYO': 'NL_CH',
        'BANUSI': 'NL_HN',
        'SEISAN': 'NL_BN',
        'HANSYOKU': 'NL_BR',
        'SCHEDULE': 'NL_YS',
        'TOKU_RACE': 'NL_TK',
        'TOKU': 'NL_TK',
        'ODDS_TANPUKU': 'NL_H1',
        'ODDS_UMAREN': 'NL_O1',
        'ODDS_WIDE': 'NL_O2',
        'ODDS_WAKU': 'NL_O3',
        'ODDS_UMATAN': 'NL_O4',
        'ODDS_SANREN': 'NL_O5',
        'ODDS_SANRENTAN': 'NL_O6',
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('"""Table name mapping: jltsql -> JRA-VAN Standard."""\n\n')
        f.write('from typing import Dict\n\n\n')
        f.write('# Mapping from JRA-VAN standard table names to jltsql table names\n')
        f.write('JRAVAN_TO_JLTSQL: Dict[str, str] = {\n')

        for jravan_table, jltsql_table in sorted(KNOWN_MAPPINGS.items()):
            f.write(f'    "{jravan_table}": "{jltsql_table}",\n')

        f.write('}\n\n')
        f.write('# Reverse mapping\n')
        f.write('JLTSQL_TO_JRAVAN: Dict[str, str] = {\n')
        f.write('    v: k for k, v in JRAVAN_TO_JLTSQL.items()\n')
        f.write('}\n')

def main():
    vb_file = Path(r'C:\Users\mitsu\jltsql\reference_data\VB2019-Builder\データベース作成VisualBasic2019\clsDBBuilder.vb')
    schema_output = Path(r'C:\Users\mitsu\jltsql\src\database\schema_jravan.py')
    mapping_output = Path(r'C:\Users\mitsu\jltsql\src\database\table_mappings.py')

    print(f"Extracting table definitions from: {vb_file}")
    tables = extract_create_table_statements(vb_file)

    print(f"\nGenerating schema file: {schema_output}")
    generate_schema_python(tables, schema_output)

    print(f"Generating mapping file: {mapping_output}")
    generate_table_mapping(tables, mapping_output)

    print(f"\n✓ Generated schema for {len(tables)} tables")
    print(f"✓ Schema file: {schema_output}")
    print(f"✓ Mapping file: {mapping_output}")

    # Print summary
    print("\nTable summary:")
    for table_name in sorted(tables.keys()):
        field_count = len(tables[table_name])
        print(f"  - {table_name}: {field_count} fields")

if __name__ == '__main__':
    main()
