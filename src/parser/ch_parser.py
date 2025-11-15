"""Parser for CH record - JRA-VAN Standard compliant.

This parser uses JRA-VAN standard field names and type conversions.
Generated from jv_data_formats.json and JRA-VAN standard schema.
"""

from typing import List

from src.parser.base import BaseParser, FieldDef


class CHParser(BaseParser):
    """Parser for CH record with JRA-VAN standard schema.

    Uses English/Romanized field names matching JRA-VAN standard database.
    """

    record_type = "CH"

    def _define_fields(self) -> List[FieldDef]:
        """Define field positions with JRA-VAN standard names and types.

        Returns:
            List of FieldDef objects with type conversion settings
        """
        return [
            FieldDef("RecordSpec", 0, 2, description="レコード種別ID"),
            FieldDef("DataKubun", 2, 1, description="データ区分"),
            FieldDef("MakeDate", 3, 8, convert_type="DATE", description="データ作成年月日"),
            FieldDef("DelKubun", 11, 5, description="調教師コード"),
            FieldDef("IssueDate", 16, 1, convert_type="DATE", description="調教師抹消区分"),
            FieldDef("DelDate", 17, 8, convert_type="DATE", description="調教師免許交付年月日"),
            FieldDef("BirthDate", 25, 8, convert_type="DATE", description="調教師免許抹消年月日"),
            FieldDef("ChokyosiName", 33, 8, description="生年月日"),
            FieldDef("ChokyosiNameKana", 41, 34, description="調教師名"),
            FieldDef("ChokyosiRyakusyo", 75, 30, description="調教師名半角ｶﾅ"),
            FieldDef("ChokyosiNameEng", 105, 8, description="調教師名略称"),
            FieldDef("SexCD", 113, 80, description="調教師名欧字"),
            FieldDef("TozaiCD", 193, 1, description="性別区分"),
            FieldDef("Syotai", 194, 1, description="調教師東西所属コード"),
            FieldDef("SaikinJyusyo1SaikinJyusyoid", 195, 20, description="招待地域名"),
            FieldDef("SaikinJyusyo1Hondai", 215, 163, description="<最近重賞勝利情報>"),
            FieldDef("SaikinJyusyo1Ryakusyo10", 704, 1052, description="<本年･前年･累計成績情報>"),
            FieldDef("SaikinJyusyo1Ryakusyo6", 3860, 2, description="レコード区切"),
        ]
