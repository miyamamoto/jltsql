"""Parser for HN record - JRA-VAN Standard compliant.

This parser uses JRA-VAN standard field names and type conversions.
Generated from jv_data_formats.json and JRA-VAN standard schema.
"""

from typing import List

from src.parser.base import BaseParser, FieldDef


class HNParser(BaseParser):
    """Parser for HN record with JRA-VAN standard schema.

    Uses English/Romanized field names matching JRA-VAN standard database.
    """

    record_type = "HN"

    def _define_fields(self) -> List[FieldDef]:
        """Define field positions with JRA-VAN standard names and types.

        Returns:
            List of FieldDef objects with type conversion settings
        """
        return [
            FieldDef("RecordSpec", 0, 2, description="レコード種別ID"),
            FieldDef("DataKubun", 2, 1, description="データ区分"),
            FieldDef("MakeDate", 3, 8, convert_type="DATE", description="データ作成年月日"),
            FieldDef("BanusiName", 11, 10, description="繁殖登録番号"),
            FieldDef("BanusiName_Co", 21, 8, description="予備"),
            FieldDef("BanusiNameKana", 29, 10, description="血統登録番号"),
            FieldDef("BanusiNameEng", 39, 1, description="予備"),
            FieldDef("Fukusyoku", 40, 36, description="馬名"),
            FieldDef("H_SetYear", 76, 40, description="馬名半角ｶﾅ"),
            FieldDef("H_HonSyokinTotal", 116, 80, description="馬名欧字"),
            FieldDef("H_FukaSyokin", 196, 4, description="生年"),
            FieldDef("H_ChakuKaisu1", 200, 1, description="性別コード"),
            FieldDef("H_ChakuKaisu2", 201, 1, description="品種コード"),
            FieldDef("H_ChakuKaisu3", 202, 2, description="毛色コード"),
            FieldDef("H_ChakuKaisu4", 204, 1, description="繁殖馬持込区分"),
            FieldDef("H_ChakuKaisu5", 205, 4, description="輸入年"),
            FieldDef("H_ChakuKaisu6", 209, 20, description="産地名"),
            FieldDef("R_SetYear", 229, 10, description="父馬繁殖登録番号"),
            FieldDef("R_HonSyokinTotal", 239, 10, description="母馬繁殖登録番号"),
            FieldDef("R_FukaSyokin", 249, 2, description="レコード区切"),
        ]
