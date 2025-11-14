"""Parser for HN record (１８．繁殖馬マスタ)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class HNParser(BaseParser):
    """Parser for HN record (Format 18).

    Record type: １８．繁殖馬マスタ
    Total fields: 20
    """

    record_type = "HN"

    def _define_fields(self) -> List[Tuple[int, int, str]]:
        """Define field positions and lengths.

        Returns:
            List of tuples: (position, length, field_name)
        """
        return [
            (1, 2, 'レコード種別ID'),  # レコード種別ID
            (3, 1, 'データ区分'),  # データ区分
            (4, 8, 'データ作成年月日'),  # データ作成年月日
            (12, 10, '繁殖登録番号'),  # 繁殖登録番号
            (22, 8, '予備'),  # 予備
            (30, 10, '血統登録番号'),  # 血統登録番号
            (40, 1, '予備'),  # 予備
            (41, 36, '馬名'),  # 馬名
            (77, 40, '馬名半角ｶﾅ'),  # 馬名半角ｶﾅ
            (117, 80, '馬名欧字'),  # 馬名欧字
            (197, 4, '生年'),  # 生年
            (201, 1, '性別コード'),  # 性別コード
            (202, 1, '品種コード'),  # 品種コード
            (203, 2, '毛色コード'),  # 毛色コード
            (205, 1, '繁殖馬持込区分'),  # 繁殖馬持込区分
            (206, 4, '輸入年'),  # 輸入年
            (210, 20, '産地名'),  # 産地名
            (230, 10, '父馬繁殖登録番号'),  # 父馬繁殖登録番号
            (240, 10, '母馬繁殖登録番号'),  # 母馬繁殖登録番号
            (250, 2, 'レコード区切'),  # レコード区切
        ]
