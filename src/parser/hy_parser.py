"""Parser for HY record (２４．馬名の意味由来)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class HYParser(BaseParser):
    """Parser for HY record (Format 24).

    Record type: ２４．馬名の意味由来
    Total fields: 7
    """

    record_type = "HY"

    def _define_fields(self) -> List[Tuple[int, int, str]]:
        """Define field positions and lengths.

        Returns:
            List of tuples: (position, length, field_name)
        """
        return [
            (1, 2, 'レコード種別ID'),  # レコード種別ID
            (3, 1, 'データ区分'),  # データ区分
            (4, 8, 'データ作成年月日'),  # データ作成年月日
            (12, 10, '血統登録番号'),  # 血統登録番号
            (22, 36, '馬名'),  # 馬名
            (58, 64, '馬名の意味由来'),  # 馬名の意味由来
            (122, 2, 'レコード区切'),  # レコード区切
        ]
