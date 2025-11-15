"""Parser for UM record - JRA-VAN Standard compliant.

This parser uses JRA-VAN standard field names and type conversions.
Generated from jv_data_formats.json and JRA-VAN standard schema.
"""

from typing import List

from src.parser.base import BaseParser, FieldDef


class UMParser(BaseParser):
    """Parser for UM record with JRA-VAN standard schema.

    Uses English/Romanized field names matching JRA-VAN standard database.
    """

    record_type = "UM"

    def _define_fields(self) -> List[FieldDef]:
        """Define field positions with JRA-VAN standard names and types.

        Returns:
            List of FieldDef objects with type conversion settings
        """
        return [
            FieldDef("RecordSpec", 0, 2, description="レコード種別ID"),
            FieldDef("DataKubun", 2, 1, description="データ区分"),
            FieldDef("MakeDate", 3, 8, convert_type="DATE", description="データ作成年月日"),
            FieldDef("DelKubun", 11, 10, description="血統登録番号"),
            FieldDef("RegDate", 21, 1, convert_type="DATE", description="競走馬抹消区分"),
            FieldDef("DelDate", 22, 8, convert_type="DATE", description="競走馬登録年月日"),
            FieldDef("BirthDate", 30, 8, convert_type="DATE", description="競走馬抹消年月日"),
            FieldDef("Bamei", 38, 8, description="生年月日"),
            FieldDef("BameiKana", 46, 36, description="馬名"),
            FieldDef("BameiEng", 82, 36, description="馬名半角ｶﾅ"),
            FieldDef("ZaikyuFlag", 118, 60, description="馬名欧字"),
            FieldDef("Reserved", 178, 1, description="JRA施設在きゅうフラグ"),
            FieldDef("UmaKigoCD", 179, 19, description="予備"),
            FieldDef("SexCD", 198, 2, description="馬記号コード"),
            FieldDef("HinsyuCD", 200, 1, description="性別コード"),
            FieldDef("KeiroCD", 201, 1, description="品種コード"),
            FieldDef("Ketto3InfoHansyokuNum1", 202, 2, description="毛色コード"),
            FieldDef("Ketto3InfoBamei1", 204, 46, description="<3代血統情報>"),
            FieldDef("Ketto3InfoHansyokuNum2", 848, 1, description="東西所属コード"),
            FieldDef("Ketto3InfoBamei2", 849, 5, description="調教師コード"),
            FieldDef("Ketto3InfoHansyokuNum3", 854, 8, description="調教師名略称"),
            FieldDef("Ketto3InfoBamei3", 862, 20, description="招待地域名"),
            FieldDef("Ketto3InfoHansyokuNum4", 882, 8, description="生産者コード"),
            FieldDef("Ketto3InfoBamei4", 890, 72, description="生産者名(法人格無)"),
            FieldDef("Ketto3InfoHansyokuNum5", 962, 20, description="産地名"),
            FieldDef("Ketto3InfoBamei5", 982, 6, description="馬主コード"),
            FieldDef("Ketto3InfoHansyokuNum6", 988, 64, description="馬主名(法人格無)"),
            FieldDef("Ketto3InfoBamei6", 1052, 9, description="平地本賞金累計"),
            FieldDef("Ketto3InfoHansyokuNum7", 1061, 9, description="障害本賞金累計"),
            FieldDef("Ketto3InfoBamei7", 1070, 9, description="平地付加賞金累計"),
            FieldDef("Ketto3InfoHansyokuNum8", 1079, 9, description="障害付加賞金累計"),
            FieldDef("Ketto3InfoBamei8", 1088, 9, description="平地収得賞金累計"),
            FieldDef("Ketto3InfoHansyokuNum9", 1097, 9, description="障害収得賞金累計"),
            FieldDef("Ketto3InfoBamei9", 1106, 3, description="総合着回数"),
            FieldDef("Ketto3InfoHansyokuNum10", 1124, 3, description="中央合計着回数"),
            FieldDef("Ketto3InfoBamei10", 1142, 3, description="芝直・着回数"),
            FieldDef("Ketto3InfoHansyokuNum11", 1160, 3, description="芝右・着回数"),
            FieldDef("Ketto3InfoBamei11", 1178, 3, description="芝左・着回数"),
            FieldDef("Ketto3InfoHansyokuNum12", 1196, 3, description="ダ直・着回数"),
            FieldDef("Ketto3InfoBamei12", 1214, 3, description="ダ右・着回数"),
            FieldDef("Ketto3InfoHansyokuNum13", 1232, 3, description="ダ左・着回数"),
            FieldDef("Ketto3InfoBamei13", 1250, 3, description="障害・着回数"),
            FieldDef("Ketto3InfoHansyokuNum14", 1268, 3, description="芝良・着回数"),
            FieldDef("Ketto3InfoBamei14", 1286, 3, description="芝稍・着回数"),
            FieldDef("TozaiCD", 1304, 3, description="芝重・着回数"),
            FieldDef("ChokyosiCode", 1322, 3, description="芝不・着回数"),
            FieldDef("ChokyosiRyakusyo", 1340, 3, description="ダ良・着回数"),
            FieldDef("Syotai", 1358, 3, description="ダ稍・着回数"),
            FieldDef("BreederCode", 1376, 3, description="ダ重・着回数"),
            FieldDef("BreederName", 1394, 3, description="ダ不・着回数"),
            FieldDef("SanchiName", 1412, 3, description="障良・着回数"),
            FieldDef("BanusiCode", 1430, 3, description="障稍・着回数"),
            FieldDef("BanusiName", 1448, 3, description="障重・着回数"),
            FieldDef("RuikeiHonsyoHeiti", 1466, 3, description="障不・着回数"),
            FieldDef("RuikeiHonsyoSyogai", 1484, 3, description="芝16下・着回数"),
            FieldDef("RuikeiFukaHeichi", 1502, 3, description="芝22下・着回数"),
            FieldDef("RuikeiFukaSyogai", 1520, 3, description="芝22超・着回数"),
            FieldDef("RuikeiSyutokuHeichi", 1538, 3, description="ダ16下・着回数"),
            FieldDef("RuikeiSyutokuSyogai", 1556, 3, description="ダ22下・着回数"),
            FieldDef("SogoChakukaisu1", 1574, 3, description="ダ22超・着回数"),
            FieldDef("SogoChakukaisu2", 1592, 3, description="脚質傾向"),
            FieldDef("SogoChakukaisu3", 1604, 3, description="登録レース数"),
            FieldDef("SogoChakukaisu4", 1607, 2, description="レコード区切"),
        ]
