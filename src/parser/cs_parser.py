"""Parser for CS record (２７．コース情報)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class CSParser(BaseParser):
    """Parser for CS record (Format 27).

    Record type: ２７．コース情報
    Total fields: 9
    """

    record_type = "CS"

    def _define_fields(self) -> List[Tuple[int, int, str]]:
        """Define field positions and lengths.

        Returns:
            List of tuples: (position, length, field_name)
        """
        return [
            (1, 2, 'レコード種別ID'),  # レコード種別ID
            (3, 1, 'データ区分'),  # データ区分
            (4, 8, 'データ作成年月日'),  # データ作成年月日
            (12, 2, '競馬場コード'),  # 競馬場コード
            (14, 4, '距離'),  # 距離
            (18, 2, 'トラックコード'),  # トラックコード
            (20, 8, 'コース改修年月日'),  # コース改修年月日
            (28, 6800, 'コース説明'),  # コース説明
            (6828, 2, 'レコード区切'),  # レコード区切
        ]
