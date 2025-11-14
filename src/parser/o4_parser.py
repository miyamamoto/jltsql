"""Parser for O4 record (１０．オッズ4（馬単）)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class O4Parser(BaseParser):
    """Parser for O4 record (Format 10).

    Record type: １０．オッズ4（馬単）
    Total fields: 16
    """

    record_type = "O4"

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
            (28, 8, '発表月日時分'),  # 発表月日時分
            (36, 2, '登録頭数'),  # 登録頭数
            (38, 2, '出走頭数'),  # 出走頭数
            (40, 1, '発売フラグ馬単'),  # 発売フラグ　馬単
            (41, 13, '馬単オッズ'),  # <馬単オッズ>
            (4019, 11, '馬単票数合計'),  # 馬単票数合計
            (4030, 2, 'レコード区切'),  # レコード区切
        ]
