"""Stylish progress display for JLTSQL using rich library.

This module provides beautiful, informative progress bars for data fetching operations.
"""

import threading
import time
from contextlib import contextmanager
from typing import Optional

from rich.console import Console, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text


class StatsDisplay:
    """Dynamic stats display that updates without recreating the object."""

    def __init__(self):
        self._lock = threading.Lock()
        self.fetched = 0
        self.parsed = 0
        self.failed = 0
        self.inserted = 0
        self.speed: Optional[float] = None

    def update(self, fetched: int = 0, parsed: int = 0, failed: int = 0,
               inserted: int = 0, speed: Optional[float] = None):
        with self._lock:
            self.fetched = fetched
            self.parsed = parsed
            self.failed = failed
            self.inserted = inserted
            self.speed = speed

    def __rich__(self) -> RenderableType:
        """Generate table dynamically when rendered."""
        with self._lock:
            table = Table.grid(padding=(0, 2))
            table.add_column(style="cyan", justify="right")
            table.add_column(style="green")
            table.add_row("取得レコード:", f"[bold green]{self.fetched:,}[/] 件")
            table.add_row("パース成功:", f"[bold green]{self.parsed:,}[/] 件")
            if self.failed > 0:
                table.add_row("パース失敗:", f"[bold red]{self.failed:,}[/] 件")
            if self.inserted > 0:
                table.add_row("DB挿入:", f"[bold cyan]{self.inserted:,}[/] 件")
            if self.speed is not None:
                table.add_row("処理速度:", f"[bold yellow]{self.speed:.1f}[/] レコード/秒")
            return table


class JVLinkProgressDisplay:
    """Stylish progress display for JV-Link data operations.

    Features:
    - Multiple concurrent progress bars
    - Download progress with percentage
    - Record fetching with speed metrics
    - Database insertion progress
    - Beautiful styling with colors
    - ETA and elapsed time
    """

    def __init__(self, console: Optional[Console] = None):
        """Initialize progress display.

        Args:
            console: Rich console instance (creates new if None)
        """
        # Force UTF-8 encoding for Windows console compatibility
        self.console = console or Console(force_terminal=True, legacy_windows=True)

        # Thread safety lock for shared state
        self._lock = threading.Lock()

        # Rate limiting for updates (avoid screen flickering)
        self._last_update_time = 0.0
        self._min_update_interval = 0.2  # 200ms minimum between updates (reduced flickering)

        # Cache layout to avoid recreation
        self._cached_layout = None

        # Create main progress bar for overall operations
        self.progress = Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[bold blue]{task.description}", justify="right"),
            BarColumn(bar_width=40, complete_style="green", finished_style="bright_green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("|"),
            TextColumn("[cyan]{task.fields[status]}"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            expand=False,
        )

        # Create simple progress for downloads
        self.download_progress = Progress(
            TextColumn("[bold magenta]{task.description}", justify="right"),
            BarColumn(bar_width=40, complete_style="magenta", finished_style="bright_magenta"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("[cyan]{task.fields[status]}"),
            console=self.console,
            expand=False,
        )

        # Use StatsDisplay for dynamic updates without recreating layout
        self.stats_display = StatsDisplay()

        # Create layout once and cache it
        self._layout: Optional[Table] = None

        self.live: Optional[Live] = None
        self.tasks = {}

    def _create_layout(self) -> Table:
        """Create the display layout once and cache it.

        The layout is created only once. Internal components (Progress, StatsDisplay)
        update their own content dynamically via __rich__() method.

        Uses simple section headers instead of Panel borders to reduce flickering
        during screen refresh.
        """
        if self._layout is not None:
            return self._layout

        layout = Table.grid(expand=False, padding=(0, 0))
        # セクション1: ダウンロード
        layout.add_row(Text(""))  # 空行
        layout.add_row(Text("  データダウンロード", style="bold cyan"))
        layout.add_row(self.download_progress)
        # セクション2: 処理
        layout.add_row(Text(""))  # 空行
        layout.add_row(Text("  データ取得・処理", style="bold blue"))
        layout.add_row(self.progress)
        # セクション3: 統計
        layout.add_row(Text(""))  # 空行
        layout.add_row(Text("  統計情報", style="bold green"))
        layout.add_row(self.stats_display)
        layout.add_row(Text(""))  # 空行
        self._layout = layout
        return layout

    def _should_update(self) -> bool:
        """Check if enough time has passed for an update."""
        with self._lock:
            current_time = time.time()
            if current_time - self._last_update_time >= self._min_update_interval:
                self._last_update_time = current_time
                return True
            return False

    def start(self):
        """Start the live display."""
        with self._lock:
            if self.live is None:
                self.live = Live(
                    self._create_layout(),
                    console=self.console,
                    refresh_per_second=2,  # Reduced refresh rate to minimize flickering
                    transient=False,
                    vertical_overflow="visible",  # Don't crop content
                )
                self.live.start()

    def stop(self):
        """Stop the live display."""
        with self._lock:
            if self.live:
                self.live.stop()
                self.live = None

    def add_download_task(
        self,
        description: str,
        total: Optional[float] = None,
    ) -> TaskID:
        """Add a download progress task.

        Args:
            description: Task description
            total: Total download count (None for indeterminate)

        Returns:
            Task ID
        """
        task_id = self.download_progress.add_task(
            description,
            total=total or 100,
            status="待機中...",
        )
        return task_id

    def add_task(
        self,
        description: str,
        total: Optional[float] = None,
    ) -> TaskID:
        """Add a progress task.

        Args:
            description: Task description
            total: Total items to process (None for indeterminate)

        Returns:
            Task ID
        """
        task_id = self.progress.add_task(
            description,
            total=total or 100,
            status="初期化中...",
        )
        self.tasks[description] = task_id
        return task_id

    def update_download(
        self,
        task_id: TaskID,
        advance: Optional[float] = None,
        completed: Optional[float] = None,
        status: Optional[str] = None,
    ):
        """Update download progress.

        Args:
            task_id: Task ID
            advance: Amount to advance
            completed: Set completed amount
            status: Status message
        """
        update_dict = {}
        if advance is not None:
            update_dict["advance"] = advance
        if completed is not None:
            update_dict["completed"] = completed
        if status is not None:
            update_dict["status"] = status

        self.download_progress.update(task_id, **update_dict)
        # Note: Don't call live.update() - Progress auto-updates within Live context
        # This prevents frame flickering

    def update(
        self,
        task_id: TaskID,
        advance: Optional[float] = None,
        completed: Optional[float] = None,
        total: Optional[float] = None,
        status: Optional[str] = None,
    ):
        """Update progress.

        Args:
            task_id: Task ID
            advance: Amount to advance
            completed: Set completed amount
            total: Set total amount
            status: Status message
        """
        update_dict = {}
        if advance is not None:
            update_dict["advance"] = advance
        if completed is not None:
            update_dict["completed"] = completed
        if total is not None:
            update_dict["total"] = total
        if status is not None:
            update_dict["status"] = status

        self.progress.update(task_id, **update_dict)
        # Note: Don't call live.update() - Progress auto-updates within Live context
        # This prevents frame flickering

    def update_stats(
        self,
        fetched: int = 0,
        parsed: int = 0,
        failed: int = 0,
        inserted: int = 0,
        speed: Optional[float] = None,
    ):
        """Update statistics display.

        Args:
            fetched: Number of records fetched
            parsed: Number of records parsed
            failed: Number of failed records
            inserted: Number of records inserted to database
            speed: Processing speed (records/sec)
        """
        # Update StatsDisplay - it will generate new table on next render
        self.stats_display.update(
            fetched=fetched,
            parsed=parsed,
            failed=failed,
            inserted=inserted,
            speed=speed,
        )
        # Note: Don't call live.update() - Live auto-refreshes and StatsDisplay
        # generates fresh content via __rich__() on each render

    def print_success(self, message: str):
        """Print success message.

        Args:
            message: Success message
        """
        self.console.print(f"[bold green][OK][/] {message}")

    def print_error(self, message: str):
        """Print error message.

        Args:
            message: Error message
        """
        self.console.print(f"[bold red][ERROR][/] {message}")

    def print_warning(self, message: str):
        """Print warning message.

        Args:
            message: Warning message
        """
        self.console.print(f"[bold yellow][WARNING][/] {message}")

    def print_info(self, message: str):
        """Print info message.

        Args:
            message: Info message
        """
        self.console.print(f"[bold cyan][INFO][/] {message}")

    @contextmanager
    def task_context(self, description: str, total: Optional[float] = None):
        """Context manager for a progress task.

        Args:
            description: Task description
            total: Total items

        Yields:
            Task ID
        """
        task_id = self.add_task(description, total)
        try:
            yield task_id
        finally:
            self.update(task_id, status="完了")

    def __enter__(self):
        """Enter context manager."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.stop()
        return False
