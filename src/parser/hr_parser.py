"""Parser for HR record - JRA-VAN Standard compliant.

This parser uses JRA-VAN standard field names and type conversions.
Generated from jv_data_formats.json and JRA-VAN standard schema.
"""

from typing import List

from src.parser.base import BaseParser, FieldDef


class HRParser(BaseParser):
    """Parser for HR record with JRA-VAN standard schema.

    Uses English/Romanized field names matching JRA-VAN standard database.
    """

    record_type = "HR"

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
            FieldDef("TorokuTosu", 27, 2, convert_type="SMALLINT", description="登録頭数"),
            FieldDef("SyussoTosu", 29, 2, convert_type="SMALLINT", description="出走頭数"),
            FieldDef("FuseirituFlag1", 31, 1, description="不成立フラグ　単勝"),
            FieldDef("FuseirituFlag2", 32, 1, description="不成立フラグ　複勝"),
            FieldDef("FuseirituFlag3", 33, 1, description="不成立フラグ　枠連"),
            FieldDef("FuseirituFlag4", 34, 1, description="不成立フラグ　馬連"),
            FieldDef("FuseirituFlag5", 35, 1, description="不成立フラグ　ワイド"),
            FieldDef("FuseirituFlag6", 36, 1, description="予備"),
            FieldDef("FuseirituFlag7", 37, 1, description="不成立フラグ　馬単"),
            FieldDef("FuseirituFlag8", 38, 1, description="不成立フラグ　3連複"),
            FieldDef("FuseirituFlag9", 39, 1, description="不成立フラグ　3連単"),
            FieldDef("TokubaraiFlag1", 40, 1, description="特払フラグ　単勝"),
            FieldDef("TokubaraiFlag2", 41, 1, description="特払フラグ　複勝"),
            FieldDef("TokubaraiFlag3", 42, 1, description="特払フラグ　枠連"),
            FieldDef("TokubaraiFlag4", 43, 1, description="特払フラグ　馬連"),
            FieldDef("TokubaraiFlag5", 44, 1, description="特払フラグ　ワイド"),
            FieldDef("TokubaraiFlag6", 45, 1, description="予備"),
            FieldDef("TokubaraiFlag7", 46, 1, description="特払フラグ　馬単"),
            FieldDef("TokubaraiFlag8", 47, 1, description="特払フラグ　3連複"),
            FieldDef("TokubaraiFlag9", 48, 1, description="特払フラグ　3連単"),
            FieldDef("HenkanFlag1", 49, 1, description="返還フラグ　単勝"),
            FieldDef("HenkanFlag2", 50, 1, description="返還フラグ　複勝"),
            FieldDef("HenkanFlag3", 51, 1, description="返還フラグ　枠連"),
            FieldDef("HenkanFlag4", 52, 1, description="返還フラグ　馬連"),
            FieldDef("HenkanFlag5", 53, 1, description="返還フラグ　ワイド"),
            FieldDef("HenkanFlag6", 54, 1, description="予備"),
            FieldDef("HenkanFlag7", 55, 1, description="返還フラグ　馬単"),
            FieldDef("HenkanFlag8", 56, 1, description="返還フラグ　3連複"),
            FieldDef("HenkanFlag9", 57, 1, description="返還フラグ　3連単"),
            FieldDef("HenkanUma1", 58, 1, description="返還馬番情報(馬番01～28)"),
            FieldDef("HenkanUma2", 86, 1, description="返還枠番情報(枠番1～8)"),
            FieldDef("HenkanUma3", 94, 1, description="返還同枠情報(枠番1～8)"),
            FieldDef("HenkanUma4", 102, 13, description="<単勝払戻>"),
            FieldDef("HenkanUma5", 141, 13, description="<複勝払戻>"),
            FieldDef("HenkanUma6", 206, 13, description="<枠連払戻>"),
            FieldDef("HenkanUma7", 245, 16, description="<馬連払戻>"),
            FieldDef("HenkanUma8", 293, 16, description="<ワイド払戻>"),
            FieldDef("HenkanUma9", 405, 16, description="<予備>"),
            FieldDef("HenkanUma10", 453, 16, description="<馬単払戻>"),
            FieldDef("HenkanUma11", 549, 18, description="<3連複払戻>"),
            FieldDef("HenkanUma12", 603, 19, description="<3連単払戻>"),
            FieldDef("HenkanUma13", 717, 2, description="レコード区切"),
        ]
