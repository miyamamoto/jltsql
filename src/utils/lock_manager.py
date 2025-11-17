#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Process lock manager to prevent concurrent execution.

This module provides a simple file-based locking mechanism to prevent
multiple instances of the same process from running simultaneously.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProcessLockError(Exception):
    """Raised when a process lock cannot be acquired."""
    pass


class ProcessLock:
    """File-based process lock to prevent concurrent execution.

    Usage:
        with ProcessLock("quickstart"):
            # Your code here
            pass

    Or:
        lock = ProcessLock("quickstart")
        if lock.acquire():
            try:
                # Your code here
                pass
            finally:
                lock.release()
    """

    def __init__(self, lock_name: str, lock_dir: Optional[Path] = None, timeout: int = 0):
        """Initialize process lock.

        Args:
            lock_name: Name of the lock (e.g., "quickstart", "fetch")
            lock_dir: Directory to store lock files (default: project_root/.locks)
            timeout: Seconds to wait for lock acquisition (0 = no wait, raise immediately)
        """
        self.lock_name = lock_name
        self.timeout = timeout

        # Determine lock directory
        if lock_dir is None:
            project_root = Path(__file__).parent.parent.parent
            lock_dir = project_root / ".locks"

        self.lock_dir = lock_dir
        self.lock_file = self.lock_dir / f"{lock_name}.lock"
        self._lock_fd = None

        # Create lock directory if it doesn't exist
        self.lock_dir.mkdir(parents=True, exist_ok=True)

    def acquire(self, blocking: bool = False) -> bool:
        """Acquire the lock.

        Args:
            blocking: If True, wait for lock. If False, raise immediately if locked.

        Returns:
            True if lock acquired, False otherwise (only when blocking=True and timeout expires)

        Raises:
            ProcessLockError: If lock is already held (when blocking=False or timeout expires)
        """
        start_time = time.time()

        while True:
            try:
                # Check if lock file exists and is still valid
                if self.lock_file.exists():
                    # Read PID from lock file
                    try:
                        with open(self.lock_file, 'r') as f:
                            pid = int(f.read().strip())

                        # Check if process is still running
                        if self._is_process_running(pid):
                            elapsed = time.time() - start_time
                            if not blocking or (self.timeout > 0 and elapsed >= self.timeout):
                                raise ProcessLockError(
                                    f"Process '{self.lock_name}' is already running (PID: {pid}). "
                                    f"Please wait for it to complete or manually remove: {self.lock_file}"
                                )
                            logger.debug(f"Waiting for lock '{self.lock_name}' (held by PID {pid})...")
                            time.sleep(1)
                            continue
                        else:
                            # Stale lock file, remove it
                            logger.warning(f"Removing stale lock file: {self.lock_file} (PID {pid} not running)")
                            self.lock_file.unlink()
                    except (ValueError, IOError) as e:
                        logger.warning(f"Invalid lock file {self.lock_file}: {e}, removing...")
                        self.lock_file.unlink()

                # Create lock file with current PID
                with open(self.lock_file, 'w') as f:
                    f.write(str(os.getpid()))

                logger.info(f"Acquired lock: {self.lock_name}")
                return True

            except ProcessLockError:
                raise
            except Exception as e:
                raise ProcessLockError(f"Failed to acquire lock '{self.lock_name}': {e}")

    def release(self) -> None:
        """Release the lock."""
        if self.lock_file.exists():
            try:
                # Verify we own this lock
                with open(self.lock_file, 'r') as f:
                    pid = int(f.read().strip())

                if pid == os.getpid():
                    self.lock_file.unlink()
                    logger.info(f"Released lock: {self.lock_name}")
                else:
                    logger.warning(
                        f"Lock file {self.lock_file} is owned by another process (PID {pid}), "
                        f"not removing"
                    )
            except Exception as e:
                logger.error(f"Failed to release lock '{self.lock_name}': {e}")

    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running.

        Args:
            pid: Process ID to check

        Returns:
            True if process is running, False otherwise
        """
        if sys.platform == "win32":
            # Windows: use tasklist command
            import subprocess
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return str(pid) in result.stdout
            except Exception:
                return False
        else:
            # Unix: send signal 0 (doesn't actually send a signal, just checks if process exists)
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False

    def __enter__(self):
        """Context manager entry."""
        self.acquire(blocking=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
        return False
