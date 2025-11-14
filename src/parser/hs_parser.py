"""Parser for HS record (２３．競走馬市場取引価格)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class HSParser(BaseParser):
    """Parser for HS record (Format 23).

    Record type: ２３．競走馬市場取引価格
    Total fields: 15
    """

    record_type = "HS"

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
            (22, 10, '父馬_繁殖登録番号'),  # 父馬 繁殖登録番号
            (32, 10, '母馬_繁殖登録番号'),  # 母馬 繁殖登録番号
            (42, 4, '生年'),  # 生年
            (46, 6, '主催者市場コード'),  # 主催者・市場コード
            (52, 40, '主催者名称'),  # 主催者名称
            (92, 80, '市場の名称'),  # 市場の名称
            (172, 8, '市場の開催期間開始日'),  # 市場の開催期間(開始日)
            (180, 8, '市場の開催期間終了日'),  # 市場の開催期間(終了日)
            (188, 1, '取引時の競走馬の年齢'),  # 取引時の競走馬の年齢
            (189, 10, '取引価格'),  # 取引価格
            (199, 2, 'レコード区切'),  # レコード区切
        ]
