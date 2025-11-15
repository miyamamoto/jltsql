"""Parser for RA record - JRA-VAN Standard compliant.

This parser uses JRA-VAN standard field names and type conversions.
Generated from jv_data_formats.json and JRA-VAN standard schema.
"""

from typing import List

from src.parser.base import BaseParser, FieldDef


class RAParser(BaseParser):
    """Parser for RA record with JRA-VAN standard schema.

    Uses English/Romanized field names matching JRA-VAN standard database.
    """

    record_type = "RA"

    def _define_fields(self) -> List[FieldDef]:
        """Define field positions with JRA-VAN standard names and types.

        Returns:
            List of FieldDef objects with type conversion settings
        """
        return [
            FieldDef("RecordSpec", 0, 2, description="レコード種別ID"),
            FieldDef("DataKubun", 2, 1, description="データ区分"),
            FieldDef("MakeDate", 3, 8, convert_type="DATE", description="データ作成年月日"),
            FieldDef("Year", 11, 4, convert_type="SMALLINT", description="開催年"),
            FieldDef("MonthDay", 15, 4, convert_type="MONTH_DAY", description="開催月日"),
            FieldDef("JyoCD", 19, 2, description="競馬場コード"),
            FieldDef("Kaiji", 21, 2, convert_type="SMALLINT", description="開催回[第N回]"),
            FieldDef("Nichiji", 23, 2, convert_type="SMALLINT", description="開催日目[N日目]"),
            FieldDef("RaceNum", 25, 2, convert_type="SMALLINT", description="レース番号"),
            FieldDef("YoubiCD", 27, 1, description="曜日コード"),
            FieldDef("TokuNum", 28, 4, description="特別競走番号"),
            FieldDef("Hondai", 32, 60, description="競走名本題"),
            FieldDef("Fukudai", 92, 60, description="競走名副題"),
            FieldDef("Kakko", 152, 60, description="競走名カッコ内"),
            FieldDef("HondaiEng", 212, 120, description="競走名本題欧字"),
            FieldDef("FukudaiEng", 332, 120, description="競走名副題欧字"),
            FieldDef("KakkoEng", 452, 120, description="競走名カッコ内欧字"),
            FieldDef("Ryakusyo10", 572, 20, description="競走名略称10文字"),
            FieldDef("Ryakusyo6", 592, 12, description="競走名略称6文字"),
            FieldDef("Ryakusyo3", 604, 6, description="競走名略称3文字"),
            FieldDef("Kubun", 610, 1, description="競走名区分"),
            FieldDef("Nkai", 611, 3, convert_type="SMALLINT", description="重賞回次[第N回]"),
            FieldDef("GradeCD", 614, 1, description="グレードコード"),
            FieldDef("GradeCDBefore", 615, 1, description="変更前グレードコード"),
            FieldDef("SyubetuCD", 616, 2, description="競走種別コード"),
            FieldDef("KigoCD", 618, 3, description="競走記号コード"),
            FieldDef("JyuryoCD", 621, 1, description="重量種別コード"),
            FieldDef("JyokenCD1", 622, 3, description="競走条件コード 2歳条件"),
            FieldDef("JyokenCD2", 625, 3, description="競走条件コード 3歳条件"),
            FieldDef("JyokenCD3", 628, 3, description="競走条件コード 4歳条件"),
            FieldDef("JyokenCD4", 631, 3, description="競走条件コード 5歳以上条件"),
            FieldDef("JyokenCD5", 634, 3, description="競走条件コード 最若年条件"),
            FieldDef("JyokenName", 637, 60, description="競走条件名称"),
            FieldDef("Kyori", 697, 4, convert_type="SMALLINT", description="距離"),
            FieldDef("KyoriBefore", 701, 4, convert_type="SMALLINT", description="変更前距離"),
            FieldDef("TrackCD", 705, 2, description="トラックコード"),
            FieldDef("TrackCDBefore", 707, 2, description="変更前トラックコード"),
            FieldDef("CourseKubunCD", 709, 2, description="コース区分"),
            FieldDef("CourseKubunCDBefore", 711, 2, description="変更前コース区分"),
            FieldDef("Honsyokin1", 713, 8, convert_type="PRIZE_MONEY", description="本賞金"),
            FieldDef("Honsyokin2", 769, 8, convert_type="PRIZE_MONEY", description="変更前本賞金"),
            FieldDef("Honsyokin3", 809, 8, convert_type="PRIZE_MONEY", description="付加賞金"),
            FieldDef("Honsyokin4", 849, 8, convert_type="PRIZE_MONEY", description="変更前付加賞金"),
            FieldDef("Honsyokin5", 873, 4, convert_type="PRIZE_MONEY", description="発走時刻"),
            FieldDef("Honsyokin6", 877, 4, convert_type="PRIZE_MONEY", description="変更前発走時刻"),
            FieldDef("Honsyokin7", 881, 2, convert_type="PRIZE_MONEY", description="登録頭数"),
            FieldDef("HonsyokinBefore1", 883, 2, description="出走頭数"),
            FieldDef("HonsyokinBefore2", 885, 2, description="入線頭数"),
            FieldDef("HonsyokinBefore3", 887, 1, description="天候コード"),
            FieldDef("HonsyokinBefore4", 888, 1, description="芝馬場状態コード"),
            FieldDef("HonsyokinBefore5", 889, 1, description="ダート馬場状態コード"),
            FieldDef("Fukasyokin1", 890, 3, convert_type="PRIZE_MONEY", description="ラップタイム"),
            FieldDef("Fukasyokin2", 965, 4, convert_type="PRIZE_MONEY", description="障害マイルタイム"),
            FieldDef("Fukasyokin3", 969, 3, convert_type="PRIZE_MONEY", description="前3ハロン"),
            FieldDef("Fukasyokin4", 972, 3, convert_type="PRIZE_MONEY", description="前4ハロン"),
            FieldDef("Fukasyokin5", 975, 3, convert_type="PRIZE_MONEY", description="後3ハロン"),
            FieldDef("FukasyokinBefore1", 978, 3, description="後4ハロン"),
            FieldDef("FukasyokinBefore2", 981, 72, description="<コーナー通過順位>"),
            FieldDef("FukasyokinBefore3", 1269, 1, description="レコード更新区分"),
            FieldDef("HassoTime", 1270, 2, convert_type="TIME", description="レコード区切"),
        ]
