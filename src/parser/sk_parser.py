"""Parser for SK record (１９．産駒マスタ)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class SKParser(BaseParser):
    """Parser for SK record (Format 19).

    Record type: １９．産駒マスタ
    Total fields: 14
    """

    record_type = "SK"

    def _define_fields(self) -> List[Tuple[int, int, str]]:
        """Define field positions and lengths.

        Returns:
            List of tuples: (position, length, field_name)
        """
        return [
            (1, 2, 'レコード種別ID'),  # レコード種別ID
            (3, 1, 'データ区分'),  # データ区分
            (4, 8, 'データ作成年月日'),  # データ作成年月日
            (12, 10, '血統登録番号'),  # 血統登録番号
            (22, 8, '生年月日'),  # 生年月日
            (30, 1, '性別コード'),  # 性別コード
            (31, 1, '品種コード'),  # 品種コード
            (32, 2, '毛色コード'),  # 毛色コード
            (34, 1, '産駒持込区分'),  # 産駒持込区分
            (35, 4, '輸入年'),  # 輸入年
            (39, 8, '生産者コード'),  # 生産者コード
            (47, 20, '産地名'),  # 産地名
            (67, 10, '3代血統_繁殖登録番号'),  # 3代血統 繁殖登録番号
            (207, 2, 'レコード区切'),  # レコード区切
        ]
