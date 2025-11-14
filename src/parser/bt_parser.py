"""Parser for BT record (２６．系統情報)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class BTParser(BaseParser):
    """Parser for BT record (Format 26).

    Record type: ２６．系統情報
    Total fields: 8
    """

    record_type = "BT"

    def _define_fields(self) -> List[Tuple[int, int, str]]:
        """Define field positions and lengths.

        Returns:
            List of tuples: (position, length, field_name)
        """
        return [
            (1, 2, 'レコード種別ID'),  # レコード種別ID
            (3, 1, 'データ区分'),  # データ区分
            (4, 8, 'データ作成年月日'),  # データ作成年月日
            (12, 10, '繁殖登録番号'),  # 繁殖登録番号
            (22, 30, '系統ID'),  # 系統ID
            (52, 36, '系統名'),  # 系統名
            (88, 6800, '系統説明'),  # 系統説明
            (6888, 2, 'レコード区切'),  # レコード区切
        ]
