"""Parser for H6 record (６．票数6（3連単）)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class H6Parser(BaseParser):
    """Parser for H6 record (Format 6).

    Record type: ６．票数6（3連単）
    Total fields: 17
    """

    record_type = "H6"

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
            (28, 2, '登録頭数'),  # 登録頭数
            (30, 2, '出走頭数'),  # 出走頭数
            (32, 1, '発売フラグ3連単'),  # 発売フラグ　3連単
            (33, 1, '返還馬番情報馬番0118'),  # 返還馬番情報(馬番01～18)
            (51, 21, '3連単票数'),  # <3連単票数>
            (102867, 11, '3連単票数合計'),  # 3連単票数合計
            (102878, 11, '3連単返還票数合計'),  # 3連単返還票数合計
            (102889, 2, 'レコード区切'),  # レコード区切
        ]
