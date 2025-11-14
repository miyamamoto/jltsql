"""Parser for RC record (２１．レコードマスタ)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class RCParser(BaseParser):
    """Parser for RC record (Format 21).

    Record type: ２１．レコードマスタ
    Total fields: 23
    """

    record_type = "RC"

    def _define_fields(self) -> List[Tuple[int, int, str]]:
        """Define field positions and lengths.

        Returns:
            List of tuples: (position, length, field_name)
        """
        return [
            (1, 2, 'レコード種別ID'),  # レコード種別ID
            (3, 1, 'データ区分'),  # データ区分
            (4, 8, 'データ作成年月日'),  # データ作成年月日
            (12, 1, 'レコード識別区分'),  # レコード識別区分
            (13, 4, '開催年'),  # 開催年
            (17, 4, '開催月日'),  # 開催月日
            (21, 2, '競馬場コード'),  # 競馬場コード
            (23, 2, '開催回第N回'),  # 開催回[第N回]
            (25, 2, '開催日目N日目'),  # 開催日目[N日目]
            (27, 2, 'レース番号'),  # レース番号
            (29, 4, '特別競走番号'),  # 特別競走番号
            (33, 60, '競走名本題'),  # 競走名本題
            (93, 1, 'グレードコード'),  # グレードコード
            (94, 2, '競走種別コード'),  # 競走種別コード
            (96, 4, '距離'),  # 距離
            (100, 2, 'トラックコード'),  # トラックコード
            (102, 1, 'レコード区分'),  # レコード区分
            (103, 4, 'レコードタイム'),  # レコードタイム
            (107, 1, '天候コード'),  # 天候コード
            (108, 1, '芝馬場状態コード'),  # 芝馬場状態コード
            (109, 1, 'ダート馬場状態コード'),  # ダート馬場状態コード
            (110, 130, 'レコード保持馬情報'),  # <レコード保持馬情報>
            (500, 2, 'レコード区切'),  # レコード区切
        ]
