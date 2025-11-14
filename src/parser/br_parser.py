"""Parser for BR record (１６．生産者マスタ)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class BRParser(BaseParser):
    """Parser for BR record (Format 16).

    Record type: １６．生産者マスタ
    Total fields: 11
    """

    record_type = "BR"

    def _define_fields(self) -> List[Tuple[int, int, str]]:
        """Define field positions and lengths.

        Returns:
            List of tuples: (position, length, field_name)
        """
        return [
            (1, 2, 'レコード種別ID'),  # レコード種別ID
            (3, 1, 'データ区分'),  # データ区分
            (4, 8, 'データ作成年月日'),  # データ作成年月日
            (12, 8, '生産者コード'),  # 生産者コード
            (20, 72, '生産者名法人格有'),  # 生産者名(法人格有)
            (92, 72, '生産者名法人格無'),  # 生産者名(法人格無)
            (164, 72, '生産者名半角ｶﾅ'),  # 生産者名半角ｶﾅ
            (236, 168, '生産者名欧字'),  # 生産者名欧字
            (404, 20, '生産者住所自治省名'),  # 生産者住所自治省名
            (424, 60, '本年累計成績情報'),  # <本年･累計成績情報>
            (544, 2, 'レコード区切'),  # レコード区切
        ]
