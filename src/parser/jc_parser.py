"""Parser for JC record (１０４．騎手変更)."""

from typing import List, Tuple

from src.parser.base import BaseParser


class JCParser(BaseParser):
    """Parser for JC record (Format 104).

    Record type: １０４．騎手変更
    Total fields: 21
    """

    record_type = "JC"

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
            (36, 2, '馬番'),  # 馬番
            (38, 36, '馬名'),  # 馬名
            (74, 3, '負担重量'),  # 負担重量
            (77, 5, '騎手コード'),  # 騎手コード
            (82, 34, '騎手名'),  # 騎手名
            (116, 1, '騎手見習コード'),  # 騎手見習コード
            (117, 3, '負担重量'),  # 負担重量
            (120, 5, '騎手コード'),  # 騎手コード
            (125, 34, '騎手名'),  # 騎手名
            (159, 1, '騎手見習コード'),  # 騎手見習コード
            (160, 2, 'レコード区切'),  # レコード区切
        ]
