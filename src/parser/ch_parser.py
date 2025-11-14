"""Parser for CH record (１５．調教師マスタ)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class CHParser(BaseParser):
    """Parser for CH record (Format 15).

    Record type: １５．調教師マスタ
    Total fields: 18
    """

    record_type = "CH"

    def _define_fields(self) -> List[Tuple[int, int, str]]:
        """Define field positions and lengths.

        Returns:
            List of tuples: (position, length, field_name)
        """
        return [
            (1, 2, 'レコード種別ID'),  # レコード種別ID
            (3, 1, 'データ区分'),  # データ区分
            (4, 8, 'データ作成年月日'),  # データ作成年月日
            (12, 5, '調教師コード'),  # 調教師コード
            (17, 1, '調教師抹消区分'),  # 調教師抹消区分
            (18, 8, '調教師免許交付年月日'),  # 調教師免許交付年月日
            (26, 8, '調教師免許抹消年月日'),  # 調教師免許抹消年月日
            (34, 8, '生年月日'),  # 生年月日
            (42, 34, '調教師名'),  # 調教師名
            (76, 30, '調教師名半角ｶﾅ'),  # 調教師名半角ｶﾅ
            (106, 8, '調教師名略称'),  # 調教師名略称
            (114, 80, '調教師名欧字'),  # 調教師名欧字
            (194, 1, '性別区分'),  # 性別区分
            (195, 1, '調教師東西所属コード'),  # 調教師東西所属コード
            (196, 20, '招待地域名'),  # 招待地域名
            (216, 163, '最近重賞勝利情報'),  # <最近重賞勝利情報>
            (705, 1052, '本年前年累計成績情報'),  # <本年･前年･累計成績情報>
            (3861, 2, 'レコード区切'),  # レコード区切
        ]
