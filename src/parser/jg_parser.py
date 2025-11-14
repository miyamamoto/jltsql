"""Parser for JG record (３１．競走馬除外情報)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class JGParser(BaseParser):
    """Parser for JG record (Format 31).

    Record type: ３１．競走馬除外情報
    Total fields: 15
    """

    record_type = "JG"

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
            (28, 10, '血統登録番号'),  # 血統登録番号
            (38, 36, '馬名'),  # 馬名
            (74, 3, '出馬投票受付順番'),  # 出馬投票受付順番
            (77, 1, '出走区分'),  # 出走区分
            (78, 1, '除外状態区分'),  # 除外状態区分
            (79, 2, 'レコード区切'),  # レコード区切
        ]
