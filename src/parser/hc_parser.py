"""Parser for HC record (２２．坂路調教)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class HCParser(BaseParser):
    """Parser for HC record (Format 22).

    Record type: ２２．坂路調教
    Total fields: 15
    """

    record_type = "HC"

    def _define_fields(self) -> List[Tuple[int, int, str]]:
        """Define field positions and lengths.

        Returns:
            List of tuples: (position, length, field_name)
        """
        return [
            (1, 2, 'レコード種別ID'),  # レコード種別ID
            (3, 1, 'データ区分'),  # データ区分
            (4, 8, 'データ作成年月日'),  # データ作成年月日
            (12, 1, 'トレセン区分'),  # トレセン区分
            (13, 8, '調教年月日'),  # 調教年月日
            (21, 4, '調教時刻'),  # 調教時刻
            (25, 10, '血統登録番号'),  # 血統登録番号
            (35, 4, '4ハロンタイム合計800M0M'),  # 4ハロンタイム合計(800M～0M)
            (39, 3, 'ラップタイム800M600M'),  # ラップタイム(800M～600M)
            (42, 4, '3ハロンタイム合計600M0M'),  # 3ハロンタイム合計(600M～0M)
            (46, 3, 'ラップタイム600M400M'),  # ラップタイム(600M～400M)
            (49, 4, '2ハロンタイム合計400M0M'),  # 2ハロンタイム合計(400M～0M)
            (53, 3, 'ラップタイム400M200M'),  # ラップタイム(400M～200M)
            (56, 3, 'ラップタイム200M0M'),  # ラップタイム(200M～0M)
            (59, 2, 'レコード区切'),  # レコード区切
        ]
