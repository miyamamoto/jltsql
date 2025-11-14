"""Parser for BN record (１７．馬主マスタ)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class BNParser(BaseParser):
    """Parser for BN record (Format 17).

    Record type: １７．馬主マスタ
    Total fields: 11
    """

    record_type = "BN"

    def _define_fields(self) -> List[Tuple[int, int, str]]:
        """Define field positions and lengths.

        Returns:
            List of tuples: (position, length, field_name)
        """
        return [
            (1, 2, 'レコード種別ID'),  # レコード種別ID
            (3, 1, 'データ区分'),  # データ区分
            (4, 8, 'データ作成年月日'),  # データ作成年月日
            (12, 6, '馬主コード'),  # 馬主コード
            (18, 64, '馬主名法人格有'),  # 馬主名(法人格有)
            (82, 64, '馬主名法人格無'),  # 馬主名(法人格無)
            (146, 50, '馬主名半角ｶﾅ'),  # 馬主名半角ｶﾅ
            (196, 100, '馬主名欧字'),  # 馬主名欧字
            (296, 60, '服色標示'),  # 服色標示
            (356, 60, '本年累計成績情報'),  # <本年･累計成績情報>
            (476, 2, 'レコード区切'),  # レコード区切
        ]
