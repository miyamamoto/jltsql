"""Parser for O1 record (７．オッズ1（単複枠）)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class O1Parser(BaseParser):
    """Parser for O1 record (Format 7).

    Record type: ７．オッズ1（単複枠）
    Total fields: 23
    """

    record_type = "O1"

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
            (40, 1, '発売フラグ単勝'),  # 発売フラグ　単勝
            (41, 1, '発売フラグ複勝'),  # 発売フラグ　複勝
            (42, 1, '発売フラグ枠連'),  # 発売フラグ　枠連
            (43, 1, '複勝着払キー'),  # 複勝着払キー
            (44, 8, '単勝オッズ'),  # <単勝オッズ>
            (268, 12, '複勝オッズ'),  # <複勝オッズ>
            (604, 9, '枠連オッズ'),  # <枠連オッズ>
            (928, 11, '単勝票数合計'),  # 単勝票数合計
            (939, 11, '複勝票数合計'),  # 複勝票数合計
            (950, 11, '枠連票数合計'),  # 枠連票数合計
            (961, 2, 'レコード区切'),  # レコード区切
        ]
