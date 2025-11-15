"""Parser for BT record - JRA-VAN Standard compliant.

This parser uses JRA-VAN standard field names and type conversions.
Generated from jv_data_formats.json and JRA-VAN standard schema.
"""

from typing import List

from src.parser.base import BaseParser, FieldDef


class BTParser(BaseParser):
    """Parser for BT record with JRA-VAN standard schema.

    Uses English/Romanized field names matching JRA-VAN standard database.
    """

    record_type = "BT"

    def _define_fields(self) -> List[FieldDef]:
        """Define field positions with JRA-VAN standard names and types.

        Returns:
            List of FieldDef objects with type conversion settings
        """
        return [
            FieldDef("RecordSpec", 0, 2, description="レコード種別ID"),
            FieldDef("DataKubun", 2, 1, description="データ区分"),
            FieldDef("MakeDate", 3, 8, convert_type="DATE", description="データ作成年月日"),
            FieldDef("DelKubun", 11, 10, description="繁殖登録番号"),
            FieldDef("IssueDate", 21, 30, convert_type="DATE", description="系統ID"),
            FieldDef("DelDate", 51, 36, convert_type="DATE", description="系統名"),
            FieldDef("BirthDate", 87, 6800, convert_type="DATE", description="系統説明"),
            FieldDef("ChokyosiName", 6887, 2, description="レコード区切"),
        ]
