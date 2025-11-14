"""Parser for DM record (２８．タイム型データマイニング予想)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class DMParser(BaseParser):
    """Parser for DM record (Format 28).

    Record type: ２８．タイム型データマイニング予想
    Total fields: 12
    """

    record_type = "DM"

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
            (26, 2, 'レース番号'),  # レース番号
            (28, 4, 'データ作成時分'),  # データ作成時分
            (32, 15, 'マイニング予想'),  # <マイニング予想>
            (302, 2, 'レコード区切'),  # レコード区切
        ]
