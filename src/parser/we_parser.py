"""Parser for WE record (１０２．天候馬場状態)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class WEParser(BaseParser):
    """Parser for WE record (Format 102).

    Record type: １０２．天候馬場状態
    Total fields: 17
    """

    record_type = "WE"

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
            (26, 8, '発表月日時分'),  # 発表月日時分
            (34, 1, '変更識別'),  # 変更識別
            (35, 1, '天候状態'),  # 天候状態
            (36, 1, '馬場状態芝'),  # 馬場状態・芝
            (37, 1, '馬場状態ダート'),  # 馬場状態・ダート
            (38, 1, '天候状態'),  # 天候状態
            (39, 1, '馬場状態芝'),  # 馬場状態・芝
            (40, 1, '馬場状態ダート'),  # 馬場状態・ダート
            (41, 2, 'レコード区切'),  # レコード区切
        ]
