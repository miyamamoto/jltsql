"""Parser for WF record (３０．重勝式(WIN5))."""

from typing import List, Tuple

from src.parser.base import BaseParser


class WFParser(BaseParser):
    """Parser for WF record (Format 30).

    Record type: ３０．重勝式(WIN5)
    Total fields: 17
    """

    record_type = "WF"

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
            (20, 2, '予備'),  # 予備
            (22, 8, '重勝式対象レース情報'),  # <重勝式対象レース情報>
            (62, 6, '予備'),  # 予備
            (68, 11, '重勝式発売票数'),  # 重勝式発売票数
            (79, 11, '有効票数情報'),  # <有効票数情報>
            (134, 1, '返還フラグ'),  # 返還フラグ
            (135, 1, '不成立フラグ'),  # 不成立フラグ
            (136, 1, '的中無フラグ'),  # 的中無フラグ
            (137, 15, 'キャリーオーバー金額初期'),  # キャリーオーバー金額初期
            (152, 15, 'キャリーオーバー金額残高'),  # キャリーオーバー金額残高
            (167, 29, '重勝式払戻情報'),  # <重勝式払戻情報>
            (7214, 2, 'レコード区切'),  # レコード区切
        ]
