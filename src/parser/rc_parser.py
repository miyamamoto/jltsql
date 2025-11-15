"""Parser for RC record - JRA-VAN Standard compliant.

This parser uses JRA-VAN standard field names and type conversions.
Generated from jv_data_formats.json and JRA-VAN standard schema.
"""

from typing import List

from src.parser.base import BaseParser, FieldDef


class RCParser(BaseParser):
    """Parser for RC record with JRA-VAN standard schema.

    Uses English/Romanized field names matching JRA-VAN standard database.
    """

    record_type = "RC"

    def _define_fields(self) -> List[FieldDef]:
        """Define field positions with JRA-VAN standard names and types.

        Returns:
            List of FieldDef objects with type conversion settings
        """
        return [
            FieldDef("RecordSpec", 0, 2, description="レコード種別ID"),
            FieldDef("DataKubun", 2, 1, description="データ区分"),
            FieldDef("MakeDate", 3, 8, convert_type="DATE", description="データ作成年月日"),
            FieldDef("RecInfoKubun", 11, 1, description="レコード識別区分"),
            FieldDef("Year", 12, 4, convert_type="SMALLINT", description="開催年"),
            FieldDef("MonthDay", 16, 4, convert_type="MONTH_DAY", description="開催月日"),
            FieldDef("JyoCD", 20, 2, description="競馬場コード"),
            FieldDef("Kaiji", 22, 2, convert_type="SMALLINT", description="開催回[第N回]"),
            FieldDef("Nichiji", 24, 2, convert_type="SMALLINT", description="開催日目[N日目]"),
            FieldDef("RaceNum", 26, 2, convert_type="SMALLINT", description="レース番号"),
            FieldDef("TokuNum", 28, 4, description="特別競走番号"),
            FieldDef("Hondai", 32, 60, description="競走名本題"),
            FieldDef("GradeCD", 92, 1, description="グレードコード"),
            FieldDef("SyubetuCD_TrackCD", 93, 2, description="競走種別コード"),
            FieldDef("Kyori", 95, 4, convert_type="SMALLINT", description="距離"),
            FieldDef("RecKubun", 99, 2, description="トラックコード"),
            FieldDef("RecTime", 101, 1, description="レコード区分"),
            FieldDef("TenkoCD", 102, 4, description="レコードタイム"),
            FieldDef("SibaBabaCD", 106, 1, description="天候コード"),
            FieldDef("DirtBabaCD", 107, 1, description="芝馬場状態コード"),
            FieldDef("RecUmaKettoNum1", 108, 1, description="ダート馬場状態コード"),
            FieldDef("RecUmaBamei1", 109, 130, description="<レコード保持馬情報>"),
            FieldDef("RecUmaUmaKigoCD1", 499, 2, description="レコード区切"),
        ]
