"""Parser for YS record (２５．開催スケジュール)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class YSParser(BaseParser):
    """Parser for YS record (Format 25).

    Record type: ２５．開催スケジュール
    Total fields: 11
    """

    record_type = "YS"

    def _define_fields(self) -> List[Tuple[int, int, str]]:
        """Define field positions and lengths.

        Returns:
            List of tuples: (position, length, field_name)
        """
        return [
            (1, 2, 'レコード種別ID'),  # レコード種別ID
            (3, 1, 'データ区分'),  # データ区分
            (4, 8, 'データ作成年月日'),  # データ作成年月日
            (12, 4, '開催年'),  # 開催年
            (16, 4, '開催月日'),  # 開催月日
            (20, 2, '競馬場コード'),  # 競馬場コード
            (22, 2, '開催回第N回'),  # 開催回[第N回]
            (24, 2, '開催日目N日目'),  # 開催日目[N日目]
            (26, 1, '曜日コード'),  # 曜日コード
            (27, 118, '重賞案内'),  # <重賞案内>
            (381, 2, 'レコード区切'),  # レコード区切
        ]
