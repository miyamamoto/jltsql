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

    # Table mapping from record type
    RECORD_TYPE_TABLE = {
        "RA": "NL_RA_RACE",
        "SE": "NL_SE_RACE_UMA",
        "HR": "NL_HR_PAY",
        "UM": "NL_UM_UMA",
        "KS": "NL_KS_KISYU",
        "CH": "NL_CH_CHOKYOSI",
        "BR": "NL_BR_BANUSI",
        "BN": "NL_BN_BREEDER",
        "HN": "NL_HN_HANSYOKU",
        "SK": "NL_SK_SANKU",
        "RC": "NL_RC_RECORD",
        "HC": "NL_HC_HANRO",
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
