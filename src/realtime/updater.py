"""Real-time data updater for JLTSQL.

This module handles real-time data updates to the database.
"""

from typing import Dict, Optional

from src.database.base import BaseDatabase
from src.parser.factory import ParserFactory
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RealtimeUpdater:
    """Real-time data updater.

    Processes real-time data records and updates the database
    based on headDataKubun (new/update/delete).

    Examples:
        >>> from src.database.sqlite_handler import SQLiteDatabase
        >>> from src.realtime.updater import RealtimeUpdater
        >>>
        >>> db = SQLiteDatabase({"path": "./keiba.db"})
        >>> with db:
        ...     updater = RealtimeUpdater(db)
        ...     result = updater.process_record(buff)
    """

    # headDataKubun constants
    DATA_KUBUN_NEW = "1"  # 新規データ
    DATA_KUBUN_UPDATE = "2"  # 更新データ
    DATA_KUBUN_DELETE = "3"  # 削除データ

    # Table mapping from record type to RT_ tables (Real-Time data)
    # Real-time updates use RT_ prefix, historical data uses NL_ prefix
    RECORD_TYPE_TABLE = {
        # Race data (Format 1-6)
        "TK": "RT_TK",  # Format 1: 特別登録馬
        "RA": "RT_RA",  # Format 2: レース詳細
        "SE": "RT_SE",  # Format 3: 馬毎レース情報
        "HR": "RT_HR",  # Format 4: 払戻
        "H1": "RT_H1",  # Format 5: 票数（単勝・複勝）
        "H6": "RT_H6",  # Format 6: 票数（３連単）

        # Odds data (Format 11-16)
        "O1": "RT_O1",  # Format 11: オッズ（単勝・複勝）
        "O2": "RT_O2",  # Format 12: オッズ（枠連）
        "O3": "RT_O3",  # Format 13: オッズ（馬連）
        "O4": "RT_O4",  # Format 14: オッズ（ワイド）
        "O5": "RT_O5",  # Format 15: オッズ（馬単）
        "O6": "RT_O6",  # Format 16: オッズ（３連複・３連単）

        # Master data (Format 21-32)
        "UM": "RT_UM",  # Format 21: 馬マスタ
        "KS": "RT_KS",  # Format 22: 騎手マスタ
        "CH": "RT_CH",  # Format 23: 調教師マスタ
        "BR": "RT_BR",  # Format 24: 馬主マスタ
        "BN": "RT_BN",  # Format 25: 生産者マスタ
        "HN": "RT_HN",  # Format 26: 繁殖馬マスタ
        "SK": "RT_SK",  # Format 27: 産駒マスタ
        "RC": "RT_RC",  # Format 28: レコードマスタ
        "CK": "RT_CK",  # Format 29: 競走馬条件クラス
        "HC": "RT_HC",  # Format 30: 馬場状態コード
        "HS": "RT_HS",  # Format 31: 配当・返還・コーナー順位
        "HY": "RT_HY",  # Format 32: 東西所属変更

        # Change data (Format 41-56)
        "YS": "RT_YS",  # Format 41: 抹消馬
        "BT": "RT_BT",  # Format 43: 繁殖馬馬産地
        "CS": "RT_CS",  # Format 45: 競走条件
        "DM": "RT_DM",  # Format 47: 場外発売馬券発売日
        "TM": "RT_TM",  # Format 51: タイム記録
        "WF": "RT_WF",  # Format 52: 追い切り
        "JG": "RT_JG",  # Format 53: 重賞
        "WC": "RT_WC",  # Format 54: 天候コード
        "WH": "RT_WH",  # Format 55: 勝ち馬
        "WE": "RT_WE",  # Format 56: 勝ち馬（地方交流）

        # Other data
        "AV": "RT_AV",  # Format 81: 場外発売情報
        "JC": "RT_JC",  # Format 91: 騎手成績
        "TC": "RT_TC",  # Format 92: 調教師成績
        "CC": "RT_CC",  # Format 106: 競走馬成績
    }

    def __init__(self, database: BaseDatabase):
        """Initialize real-time updater.

        Args:
            database: Database handler instance
        """
        self.database = database
        self.parser_factory = ParserFactory()

        logger.info("RealtimeUpdater initialized")

    def process_record(self, buff: str) -> Optional[Dict]:
        """Process real-time data record.

        Args:
            buff: Raw JV-Data record buffer

        Returns:
            Dictionary with processing result, or None if failed

        Raises:
            Exception: If processing fails
        """
        try:
            # Parse record
            parsed_data = self.parser_factory.parse(buff)
            if not parsed_data:
                logger.warning("Failed to parse record")
                return None

            record_type = parsed_data.get("RecordSpec")
            if not record_type:
                logger.warning("Missing RecordSpec in parsed data")
                return None

            # Get table name
            table_name = self.RECORD_TYPE_TABLE.get(record_type)
            if not table_name:
                logger.warning(f"Unknown record type: {record_type}")
                return None

            # Get headDataKubun
            head_data_kubun = parsed_data.get("headDataKubun", "1")

            logger.debug(
                "Processing record",
                record_type=record_type,
                table=table_name,
                kubun=head_data_kubun,
            )

            # Process based on headDataKubun
            if head_data_kubun == self.DATA_KUBUN_NEW:
                return self._handle_new_record(table_name, parsed_data)
            elif head_data_kubun == self.DATA_KUBUN_UPDATE:
                return self._handle_update_record(table_name, parsed_data)
            elif head_data_kubun == self.DATA_KUBUN_DELETE:
                return self._handle_delete_record(table_name, parsed_data)
            else:
                logger.warning(f"Unknown headDataKubun: {head_data_kubun}")
                return None

        except Exception as e:
            logger.error(f"Error processing record: {e}", exc_info=True)
            raise

    def _handle_new_record(self, table_name: str, data: Dict) -> Dict:
        """Handle new record insertion.

        Args:
            table_name: Table name
            data: Parsed record data

        Returns:
            Result dictionary with operation details
        """
        try:
            # Remove metadata fields
            clean_data = {k: v for k, v in data.items() if not k.startswith("_")}

            # Insert into database
            # TODO: Implement UPSERT to handle duplicates
            self.database.insert(table_name, clean_data)

            logger.debug(f"Inserted new record into {table_name}")

            return {
                "operation": "insert",
                "table": table_name,
                "record_type": data.get("RecordSpec"),
                "success": True,
            }

        except Exception as e:
            logger.error(f"Failed to insert record: {e}")
            return {
                "operation": "insert",
                "table": table_name,
                "success": False,
                "error": str(e),
            }

    def _handle_update_record(self, table_name: str, data: Dict) -> Dict:
        """Handle record update.

        Args:
            table_name: Table name
            data: Parsed record data

        Returns:
            Result dictionary with operation details
        """
        try:
            # Remove metadata fields
            clean_data = {k: v for k, v in data.items() if not k.startswith("_")}

            # Update record
            # TODO: Implement proper UPDATE based on primary key
            # For now, use INSERT (may cause duplicate key error)
            self.database.insert(table_name, clean_data)

            logger.debug(f"Updated record in {table_name}")

            return {
                "operation": "update",
                "table": table_name,
                "record_type": data.get("RecordSpec"),
                "success": True,
            }

        except Exception as e:
            logger.error(f"Failed to update record: {e}")
            return {
                "operation": "update",
                "table": table_name,
                "success": False,
                "error": str(e),
            }

    def _handle_delete_record(self, table_name: str, data: Dict) -> Dict:
        """Handle record deletion.

        Args:
            table_name: Table name
            data: Parsed record data

        Returns:
            Result dictionary with operation details

        Note:
            Instead of physical deletion, we set a delete flag if available,
            or perform physical deletion based on primary key.
        """
        try:
            # Build WHERE clause from primary key fields
            # For now, we'll use a simplified approach
            # TODO: Implement proper primary key detection

            # Option 1: Set delete flag (if table has DeleteFlag column)
            # Option 2: Physical deletion

            # For simplicity, we'll do physical deletion based on key fields
            # This is a simplified implementation

            logger.warning(
                f"Delete operation not fully implemented for {table_name}",
                data=data,
            )

            return {
                "operation": "delete",
                "table": table_name,
                "record_type": data.get("RecordSpec"),
                "success": False,
                "error": "Delete operation not fully implemented",
            }

        except Exception as e:
            logger.error(f"Failed to delete record: {e}")
            return {
                "operation": "delete",
                "table": table_name,
                "success": False,
                "error": str(e),
            }
