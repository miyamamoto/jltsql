"""Parser for RA record (２．レース詳細) - JRA-VAN Standard compliant.

This parser uses JRA-VAN standard field names and type conversions.
"""

from typing import List

from src.parser.base import BaseParser, FieldDef


class RAParserJRAVAN(BaseParser):
    """Parser for RA record with JRA-VAN standard schema.

    Record type: ２．レース詳細 (RACE table)
    Uses English/Romanized field names matching JRA-VAN standard database.
    """

    record_type = "RA"

    def _define_fields(self) -> List[FieldDef]:
        """Define field positions with JRA-VAN standard names and types.

        Returns:
            List of FieldDef objects with type conversion settings
        """
        return [
            # Header fields
            FieldDef("RecordSpec", 0, 2, description="レコード種別ID"),
            FieldDef("DataKubun", 2, 1, description="データ区分"),
            FieldDef("MakeDate", 3, 8, convert_type="DATE", description="データ作成年月日"),

            # Race identification
            FieldDef("Year", 11, 4, convert_type="SMALLINT", description="開催年"),
            FieldDef("MonthDay", 15, 4, convert_type="MONTH_DAY", description="開催月日"),
            FieldDef("JyoCD", 19, 2, description="競馬場コード"),
            FieldDef("Kaiji", 21, 2, convert_type="SMALLINT", description="開催回"),
            FieldDef("Nichiji", 23, 2, convert_type="SMALLINT", description="開催日目"),
            FieldDef("RaceNum", 25, 2, convert_type="SMALLINT", description="レース番号"),
            FieldDef("YoubiCD", 27, 1, description="曜日コード"),
            FieldDef("TokuNum", 28, 4, description="特別競走番号"),

            # Race names
            FieldDef("Hondai", 32, 60, description="競走名本題"),
            FieldDef("Fukudai", 92, 60, description="競走名副題"),
            FieldDef("Kakko", 152, 60, description="競走名カッコ内"),
            FieldDef("HondaiEng", 212, 120, description="競走名本題欧字"),
            FieldDef("FukudaiEng", 332, 120, description="競走名副題欧字"),
            FieldDef("KakkoEng", 452, 120, description="競走名カッコ内欧字"),
            FieldDef("Ryakusyo10", 572, 20, description="競走名略称10文字"),
            FieldDef("Ryakusyo6", 592, 12, description="競走名略称6文字"),
            FieldDef("Ryakusyo3", 604, 6, description="競走名略称3文字"),

            # Race classification
            FieldDef("Kubun", 610, 1, description="競走名区分"),
            FieldDef("Nkai", 611, 3, convert_type="SMALLINT", description="重賞回次"),
            FieldDef("GradeCD", 614, 1, description="グレードコード"),
            FieldDef("GradeCDBefore", 615, 1, description="変更前グレードコード"),
            FieldDef("SyubetuCD", 616, 2, description="競走種別コード"),
            FieldDef("KigoCD", 618, 3, description="競走記号コード"),
            FieldDef("JyuryoCD", 621, 1, description="重量種別コード"),

            # Race conditions
            FieldDef("JyokenCD1", 622, 3, description="競走条件コード_2歳条件"),
            FieldDef("JyokenCD2", 625, 3, description="競走条件コード_3歳条件"),
            FieldDef("JyokenCD3", 628, 3, description="競走条件コード_4歳条件"),
            FieldDef("JyokenCD4", 631, 3, description="競走条件コード_5歳以上条件"),
            FieldDef("JyokenCD5", 634, 3, description="競走条件コード_最若年条件"),
            FieldDef("JyokenName", 637, 60, description="競走条件名称"),

            # Distance and track
            FieldDef("Kyori", 697, 4, convert_type="SMALLINT", description="距離"),
            FieldDef("KyoriBefore", 701, 4, convert_type="SMALLINT", description="変更前距離"),
            FieldDef("TrackCD", 705, 2, description="トラックコード"),
            FieldDef("TrackCDBefore", 707, 2, description="変更前トラックコード"),
            FieldDef("CourseKubunCD", 709, 2, description="コース区分"),
            FieldDef("CourseKubunCDBefore", 711, 2, description="変更前コース区分"),

            # Prize money (本賞金1-7着, 付加賞金1-5着)
            FieldDef("Honsyokin1", 713, 8, convert_type="PRIZE_MONEY", description="1着本賞金"),
            FieldDef("Honsyokin2", 721, 8, convert_type="PRIZE_MONEY", description="2着本賞金"),
            FieldDef("Honsyokin3", 729, 8, convert_type="PRIZE_MONEY", description="3着本賞金"),
            FieldDef("Honsyokin4", 737, 8, convert_type="PRIZE_MONEY", description="4着本賞金"),
            FieldDef("Honsyokin5", 745, 8, convert_type="PRIZE_MONEY", description="5着本賞金"),
            FieldDef("Honsyokin6", 753, 8, convert_type="PRIZE_MONEY", description="6着本賞金"),
            FieldDef("Honsyokin7", 761, 8, convert_type="PRIZE_MONEY", description="7着本賞金"),
            FieldDef("HonsyokinBefore1", 769, 8, description="変更前本賞金1"),
            FieldDef("HonsyokinBefore2", 777, 8, description="変更前本賞金2"),
            FieldDef("HonsyokinBefore3", 785, 8, description="変更前本賞金3"),
            FieldDef("HonsyokinBefore4", 793, 8, description="変更前本賞金4"),
            FieldDef("HonsyokinBefore5", 801, 8, description="変更前本賞金5"),
            FieldDef("Fukasyokin1", 809, 8, convert_type="PRIZE_MONEY", description="1着付加賞金"),
            FieldDef("Fukasyokin2", 817, 8, convert_type="PRIZE_MONEY", description="2着付加賞金"),
            FieldDef("Fukasyokin3", 825, 8, convert_type="PRIZE_MONEY", description="3着付加賞金"),
            FieldDef("Fukasyokin4", 833, 8, convert_type="PRIZE_MONEY", description="4着付加賞金"),
            FieldDef("Fukasyokin5", 841, 8, convert_type="PRIZE_MONEY", description="5着付加賞金"),
            FieldDef("FukasyokinBefore1", 849, 8, description="変更前付加賞金1"),
            FieldDef("FukasyokinBefore2", 857, 8, description="変更前付加賞金2"),
            FieldDef("FukasyokinBefore3", 865, 8, description="変更前付加賞金3"),

            # Start time and horse counts
            FieldDef("HassoTime", 873, 4, convert_type="TIME", description="発走時刻"),
            FieldDef("HassoTimeBefore", 877, 4, description="変更前発走時刻"),
            FieldDef("TorokuTosu", 881, 2, convert_type="SMALLINT", description="登録頭数"),
            FieldDef("SyussoTosu", 883, 2, convert_type="SMALLINT", description="出走頭数"),
            FieldDef("NyusenTosu", 885, 2, convert_type="SMALLINT", description="入線頭数"),

            # Weather and track conditions
            FieldDef("TenkoCD", 887, 1, description="天候コード"),
            FieldDef("SibaBabaCD", 888, 1, description="芝馬場状態コード"),
            FieldDef("DirtBabaCD", 889, 1, description="ダート馬場状態コード"),

            # Lap times (25 laps)
            FieldDef("LapTime1", 890, 3, convert_type="LAP_TIME", description="ラップタイム1"),
            FieldDef("LapTime2", 893, 3, convert_type="LAP_TIME", description="ラップタイム2"),
            FieldDef("LapTime3", 896, 3, convert_type="LAP_TIME", description="ラップタイム3"),
            FieldDef("LapTime4", 899, 3, convert_type="LAP_TIME", description="ラップタイム4"),
            FieldDef("LapTime5", 902, 3, convert_type="LAP_TIME", description="ラップタイム5"),
            FieldDef("LapTime6", 905, 3, convert_type="LAP_TIME", description="ラップタイム6"),
            FieldDef("LapTime7", 908, 3, convert_type="LAP_TIME", description="ラップタイム7"),
            FieldDef("LapTime8", 911, 3, convert_type="LAP_TIME", description="ラップタイム8"),
            FieldDef("LapTime9", 914, 3, convert_type="LAP_TIME", description="ラップタイム9"),
            FieldDef("LapTime10", 917, 3, convert_type="LAP_TIME", description="ラップタイム10"),
            FieldDef("LapTime11", 920, 3, convert_type="LAP_TIME", description="ラップタイム11"),
            FieldDef("LapTime12", 923, 3, convert_type="LAP_TIME", description="ラップタイム12"),
            FieldDef("LapTime13", 926, 3, convert_type="LAP_TIME", description="ラップタイム13"),
            FieldDef("LapTime14", 929, 3, convert_type="LAP_TIME", description="ラップタイム14"),
            FieldDef("LapTime15", 932, 3, convert_type="LAP_TIME", description="ラップタイム15"),
            FieldDef("LapTime16", 935, 3, convert_type="LAP_TIME", description="ラップタイム16"),
            FieldDef("LapTime17", 938, 3, convert_type="LAP_TIME", description="ラップタイム17"),
            FieldDef("LapTime18", 941, 3, convert_type="LAP_TIME", description="ラップタイム18"),
            FieldDef("LapTime19", 944, 3, convert_type="LAP_TIME", description="ラップタイム19"),
            FieldDef("LapTime20", 947, 3, convert_type="LAP_TIME", description="ラップタイム20"),
            FieldDef("LapTime21", 950, 3, convert_type="LAP_TIME", description="ラップタイム21"),
            FieldDef("LapTime22", 953, 3, convert_type="LAP_TIME", description="ラップタイム22"),
            FieldDef("LapTime23", 956, 3, convert_type="LAP_TIME", description="ラップタイム23"),
            FieldDef("LapTime24", 959, 3, convert_type="LAP_TIME", description="ラップタイム24"),
            FieldDef("LapTime25", 962, 3, convert_type="LAP_TIME", description="ラップタイム25"),

            # Special times
            FieldDef("SyogaiMileTime", 965, 4, convert_type="RACE_TIME", description="障害マイルタイム"),
            FieldDef("HaronTimeS3", 969, 3, convert_type="LAP_TIME", description="前3ハロン"),
            FieldDef("HaronTimeS4", 972, 3, convert_type="LAP_TIME", description="前4ハロン"),
            FieldDef("HaronTimeL3", 975, 3, convert_type="LAP_TIME", description="後3ハロン"),
            FieldDef("HaronTimeL4", 978, 3, convert_type="LAP_TIME", description="後4ハロン"),

            # Corner positions (composite field)
            FieldDef("Corner1", 981, 1, description="1コーナー"),
            FieldDef("Syukaisu1", 982, 1, description="周回数1"),
            FieldDef("Jyuni1", 983, 70, description="通過順位1"),
            FieldDef("Corner2", 1053, 1, description="2コーナー"),
            FieldDef("Syukaisu2", 1054, 1, description="周回数2"),
            FieldDef("Jyuni2", 1055, 70, description="通過順位2"),
            FieldDef("Corner3", 1125, 1, description="3コーナー"),
            FieldDef("Syukaisu3", 1126, 1, description="周回数3"),
            FieldDef("Jyuni3", 1127, 70, description="通過順位3"),
            FieldDef("Corner4", 1197, 1, description="4コーナー"),
            FieldDef("Syukaisu4", 1198, 1, description="周回数4"),
            FieldDef("Jyuni4", 1199, 70, description="通過順位4"),

            # Record update flag
            FieldDef("RecordUpKubun", 1269, 1, description="レコード更新区分"),
        ]
