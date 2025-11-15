"""Parser for KS record - JRA-VAN Standard compliant.

This parser uses JRA-VAN standard field names and type conversions.
Generated from jv_data_formats.json and JRA-VAN standard schema.
"""

from typing import List

from src.parser.base import BaseParser, FieldDef


class KSParser(BaseParser):
    """Parser for KS record with JRA-VAN standard schema.

    Uses English/Romanized field names matching JRA-VAN standard database.
    """

    record_type = "KS"

    def _define_fields(self) -> List[FieldDef]:
        """Define field positions with JRA-VAN standard names and types.

        Returns:
            List of FieldDef objects with type conversion settings
        """
        return [
            FieldDef("RecordSpec", 0, 2, description="レコード種別ID"),
            FieldDef("DataKubun", 2, 1, description="データ区分"),
            FieldDef("MakeDate", 3, 8, convert_type="DATE", description="データ作成年月日"),
            FieldDef("DelKubun", 11, 5, description="騎手コード"),
            FieldDef("IssueDate", 16, 1, convert_type="DATE", description="騎手抹消区分"),
            FieldDef("DelDate", 17, 8, convert_type="DATE", description="騎手免許交付年月日"),
            FieldDef("BirthDate", 25, 8, convert_type="DATE", description="騎手免許抹消年月日"),
            FieldDef("KisyuName", 33, 8, description="生年月日"),
            FieldDef("reserved", 41, 34, description="騎手名"),
            FieldDef("KisyuNameKana", 75, 34, description="予備"),
            FieldDef("KisyuRyakusyo", 109, 30, description="騎手名半角ｶﾅ"),
            FieldDef("KisyuNameEng", 139, 8, description="騎手名略称"),
            FieldDef("SexCD", 147, 80, description="騎手名欧字"),
            FieldDef("SikakuCD", 227, 1, description="性別区分"),
            FieldDef("MinaraiCD", 228, 1, description="騎乗資格コード"),
            FieldDef("TozaiCD", 229, 1, description="騎手見習コード"),
            FieldDef("Syotai", 230, 1, description="騎手東西所属コード"),
            FieldDef("ChokyosiCode", 231, 20, description="招待地域名"),
            FieldDef("ChokyosiRyakusyo", 251, 5, description="所属調教師コード"),
            FieldDef("HatuKiJyo1Hatukijyoid", 256, 8, description="所属調教師名略称"),
            FieldDef("HatuKiJyo1SyussoTosu", 264, 67, description="<初騎乗情報>"),
            FieldDef("HatuKiJyo1KettoNum", 398, 64, description="<初勝利情報>"),
            FieldDef("HatuKiJyo1Bamei", 526, 163, description="<最近重賞勝利情報>"),
            FieldDef("HatuKiJyo1KakuteiJyuni", 1015, 1052, description="<本年･前年･累計成績情報>"),
            FieldDef("HatuKiJyo1IJyoCD", 4171, 2, description="レコード区切"),
        ]
