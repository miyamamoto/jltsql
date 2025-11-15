"""Parser for AV record - JRA-VAN Standard compliant.

This parser uses JRA-VAN standard field names and type conversions.
Generated from jv_data_formats.json and JRA-VAN standard schema.
"""

from typing import List

from src.parser.base import BaseParser, FieldDef


class AVParser(BaseParser):
    """Parser for AV record with JRA-VAN standard schema.

    Uses English/Romanized field names matching JRA-VAN standard database.
    """

    record_type = "AV"

    def _define_fields(self) -> List[FieldDef]:
        """Define field positions with JRA-VAN standard names and types.

        Returns:
            List of FieldDef objects with type conversion settings
        """
        return [
            FieldDef("RecordSpec", 0, 2, description="レコード種別ID"),
            FieldDef("DataKubun", 2, 1, description="データ区分"),
            FieldDef("MakeDate", 3, 8, convert_type="DATE", description="データ作成年月日"),
            FieldDef("KettoNum", 11, 4, description="開催年"),
            FieldDef("HansyokuFNum", 15, 4, description="開催月日"),
            FieldDef("HansyokuMNum", 19, 2, description="競馬場コード"),
            FieldDef("BirthYear", 21, 2, description="開催回[第N回]"),
            FieldDef("SaleCode", 23, 2, description="開催日目[N日目]"),
            FieldDef("SaleHostName", 25, 2, description="レース番号"),
            FieldDef("SaleName", 27, 8, description="発表月日時分"),
            FieldDef("FromDate", 35, 2, description="馬番"),
            FieldDef("ToDate", 37, 36, description="馬名"),
            FieldDef("Barei", 73, 3, convert_type="SMALLINT", description="事由区分"),
            FieldDef("Price", 76, 2, description="レコード区切"),
        ]
