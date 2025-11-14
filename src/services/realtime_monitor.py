"""Realtime data monitoring service for JLTSQL.

This module provides a background service that continuously monitors
JV-Link realtime data streams and imports updates into the database.
"""

from typing import Dict, List, Optional, Set
import threading
import time
from datetime import datetime

from src.fetcher.realtime import RealtimeFetcher
from src.importer.importer import DataImporter
from src.database.base import BaseDatabase
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MonitorStatus:
    """Monitor status tracking."""

    def __init__(self):
        self.started_at: Optional[datetime] = None
        self.stopped_at: Optional[datetime] = None
        self.is_running: bool = False
        self.records_imported: int = 0
        self.records_failed: int = 0
        self.errors: List[Dict[str, str]] = []
        self.monitored_specs: Set[str] = set()

    def to_dict(self) -> Dict:
        """Convert status to dictionary."""
        return {
            "is_running": self.is_running,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "uptime_seconds": (
                (datetime.now() - self.started_at).total_seconds()
                if self.started_at and self.is_running
                else 0
            ),
            "records_imported": self.records_imported,
            "records_failed": self.records_failed,
            "error_count": len(self.errors),
            "monitored_specs": sorted(self.monitored_specs),
        }


class RealtimeMonitor:
    """Realtime data monitoring service.

    This service continuously monitors JV-Link realtime data streams
    and automatically imports new data into the database as it arrives.

    Examples:
        >>> from src.database.sqlite_handler import SQLiteDatabase
        >>>
        >>> # Configure database
        >>> db_config = {"path": "data/realtime.db"}
        >>> database = SQLiteDatabase(db_config)
        >>>
        >>> # Configure monitor
        >>> monitor = RealtimeMonitor(
        ...     database=database,
        ...     data_specs=["0B12", "0B15"],  # Race results and payouts
        ...     sid="JLTSQL"
        ... )
        >>>
        >>> # Start monitoring in background
        >>> monitor.start()
        >>>
        >>> # Check status
        >>> status = monitor.get_status()
        >>> print(f"Imported: {status['records_imported']}")
        >>>
        >>> # Stop monitoring
        >>> monitor.stop()
    """

    def __init__(
        self,
        database: BaseDatabase,
        data_specs: Optional[List[str]] = None,
        sid: str = "JLTSQL",
        batch_size: int = 100,
        auto_create_tables: bool = True,
    ):
        """Initialize realtime monitor.

        Args:
            database: Database instance for storing data
            data_specs: List of data specs to monitor (default: ["0B12"])
            sid: JV-Link session ID
            batch_size: Batch size for database imports
            auto_create_tables: Automatically create missing tables
        """
        self.database = database
        self.data_specs = data_specs or ["0B12"]  # Default: race results
        self.sid = sid
        self.batch_size = batch_size
        self.auto_create_tables = auto_create_tables

        # Status tracking
        self.status = MonitorStatus()
        self.status.monitored_specs = set(self.data_specs)

        # Threading
        self._threads: List[threading.Thread] = []
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def start(self) -> bool:
        """Start monitoring service.

        Returns:
            True if started successfully, False otherwise
        """
        if self.status.is_running:
            logger.warning("Monitor is already running")
            return False

        try:
            # Ensure database is connected
            if not self.database._connection:
                self.database.connect()

            # Auto-create tables if needed
            if self.auto_create_tables:
                self._ensure_tables()

            # Clear stop event
            self._stop_event.clear()

            # Start monitoring threads (one per data spec)
            for data_spec in self.data_specs:
                thread = threading.Thread(
                    target=self._monitor_spec,
                    args=(data_spec,),
                    daemon=True,
                    name=f"Monitor-{data_spec}"
                )
                thread.start()
                self._threads.append(thread)
                logger.info(f"Started monitoring thread for {data_spec}")

            # Update status
            self.status.is_running = True
            self.status.started_at = datetime.now()
            self.status.stopped_at = None

            logger.info(
                "Realtime monitor started",
                data_specs=self.data_specs,
                thread_count=len(self._threads)
            )

            return True

        except Exception as e:
            logger.error("Failed to start monitor", error=str(e))
            self._add_error("start", str(e))
            return False

    def stop(self, timeout: float = 10.0) -> bool:
        """Stop monitoring service.

        Args:
            timeout: Maximum time to wait for threads to stop (seconds)

        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.status.is_running:
            logger.warning("Monitor is not running")
            return False

        try:
            logger.info("Stopping realtime monitor...")

            # Signal threads to stop
            self._stop_event.set()

            # Wait for threads to finish
            for thread in self._threads:
                thread.join(timeout=timeout / len(self._threads))
                if thread.is_alive():
                    logger.warning(f"Thread {thread.name} did not stop gracefully")

            # Clear threads
            self._threads.clear()

            # Update status
            self.status.is_running = False
            self.status.stopped_at = datetime.now()

            logger.info(
                "Realtime monitor stopped",
                records_imported=self.status.records_imported,
                records_failed=self.status.records_failed
            )

            return True

        except Exception as e:
            logger.error("Failed to stop monitor", error=str(e))
            self._add_error("stop", str(e))
            return False

    def get_status(self) -> Dict:
        """Get current monitor status.

        Returns:
            Dictionary with status information
        """
        with self._lock:
            return self.status.to_dict()

    def add_data_spec(self, data_spec: str) -> bool:
        """Add a new data spec to monitor.

        Args:
            data_spec: Data specification code to add

        Returns:
            True if added successfully, False otherwise
        """
        if not self.status.is_running:
            logger.warning("Cannot add data spec - monitor is not running")
            return False

        if data_spec in self.status.monitored_specs:
            logger.warning(f"Data spec {data_spec} is already being monitored")
            return False

        try:
            # Start new monitoring thread
            thread = threading.Thread(
                target=self._monitor_spec,
                args=(data_spec,),
                daemon=True,
                name=f"Monitor-{data_spec}"
            )
            thread.start()
            self._threads.append(thread)

            # Update status
            with self._lock:
                self.status.monitored_specs.add(data_spec)

            logger.info(f"Added monitoring for data spec: {data_spec}")
            return True

        except Exception as e:
            logger.error(f"Failed to add data spec {data_spec}", error=str(e))
            self._add_error("add_spec", str(e))
            return False

    def _monitor_spec(self, data_spec: str):
        """Monitor a single data spec (runs in separate thread).

        Args:
            data_spec: Data specification code to monitor
        """
        logger.info(f"Starting monitoring for {data_spec}")

        fetcher = RealtimeFetcher(sid=self.sid)
        importer = DataImporter(
            database=self.database,
            batch_size=self.batch_size
        )

        retry_count = 0
        max_retries = 3

        while not self._stop_event.is_set():
            try:
                # Fetch realtime data continuously
                for record in fetcher.fetch(data_spec=data_spec, continuous=True):
                    # Check stop signal
                    if self._stop_event.is_set():
                        break

                    # Import record
                    success = importer.import_single_record(record)

                    # Update statistics
                    with self._lock:
                        if success:
                            self.status.records_imported += 1
                        else:
                            self.status.records_failed += 1

                    # Reset retry count on success
                    if success:
                        retry_count = 0

                # If loop exits normally, break
                break

            except Exception as e:
                retry_count += 1
                error_msg = f"Error monitoring {data_spec}: {e}"
                logger.error(error_msg)
                self._add_error(data_spec, str(e))

                # Check if should retry
                if retry_count >= max_retries:
                    logger.error(
                        f"Max retries reached for {data_spec}, stopping thread",
                        retry_count=retry_count
                    )
                    break

                # Wait before retry
                wait_time = min(5 * retry_count, 30)  # Max 30 seconds
                logger.info(f"Retrying {data_spec} in {wait_time} seconds...")
                time.sleep(wait_time)

        logger.info(f"Stopped monitoring for {data_spec}")

    def _ensure_tables(self):
        """Ensure required database tables exist."""
        try:
            from src.database.schema import SchemaManager

            schema_mgr = SchemaManager(self.database)
            missing_tables = schema_mgr.get_missing_tables()

            if missing_tables:
                logger.info(
                    f"Creating {len(missing_tables)} missing tables",
                    tables=missing_tables
                )
                schema_mgr.create_all_tables()

        except Exception as e:
            logger.warning(f"Could not create tables: {e}")

    def _add_error(self, context: str, error: str):
        """Add error to status tracking.

        Args:
            context: Error context (e.g., data spec or operation)
            error: Error message
        """
        with self._lock:
            self.status.errors.append({
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "error": error
            })

            # Keep only last 100 errors
            if len(self.status.errors) > 100:
                self.status.errors = self.status.errors[-100:]

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False
