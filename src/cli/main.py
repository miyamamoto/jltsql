"""JLTSQL Command Line Interface."""

import sys
from pathlib import Path

import click
from rich.console import Console

from src.utils.config import ConfigError, load_config
from src.utils.logger import get_logger, setup_logging_from_config

# Version
__version__ = "0.1.0-alpha"

# Console for rich output
console = Console()
logger = get_logger(__name__)


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    default=None,
    help="Path to configuration file (default: config/config.yaml)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
@click.version_option(version=__version__, prog_name="jltsql")
@click.pass_context
def cli(ctx, config, verbose):
    """JLTSQL - JRA-VAN Link To SQL

    JRA-VAN DataLabの競馬データをSQLite/DuckDB/PostgreSQLに
    リアルタイムインポートするツール

    \b
    使用例:
      jltsql init                     # プロジェクト初期化
      jltsql fetch --from 2024-01-01  # データ取得
      jltsql monitor --daemon         # リアルタイム監視開始

    詳細: https://github.com/yourusername/jltsql
    """
    # Store context
    ctx.ensure_object(dict)

    # Load configuration
    if config:
        config_path = config
    else:
        # Try default path
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

        if not config_path.exists():
            # Config not found, use default for init command
            if ctx.invoked_subcommand != "init":
                console.print(
                    "[red]Error:[/red] Configuration file not found. "
                    "Run 'jltsql init' first.",
                    style="bold",
                )
                sys.exit(1)
            else:
                config_path = None

    if config_path:
        try:
            cfg = load_config(str(config_path))
            ctx.obj["config"] = cfg

            # Setup logging from config
            setup_logging_from_config(cfg.to_dict())

            # Override log level if verbose
            if verbose:
                from src.utils.logger import setup_logging

                setup_logging(level="DEBUG")

            logger.info("Configuration loaded", config_path=str(config_path))

        except ConfigError as e:
            console.print(f"[red]Configuration Error:[/red] {e}", style="bold")
            sys.exit(1)
    else:
        ctx.obj["config"] = None


@cli.command()
@click.option(
    "--force",
    is_flag=True,
    help="Force overwrite existing configuration",
)
@click.pass_context
def init(ctx, force):
    """Initialize JLTSQL project.

    Creates configuration files and database directories.
    """
    console.print("[bold cyan]Initializing JLTSQL project...[/bold cyan]")

    project_root = Path(__file__).parent.parent.parent
    config_dir = project_root / "config"
    data_dir = project_root / "data"
    logs_dir = project_root / "logs"

    # Create directories
    for directory in [config_dir, data_dir, logs_dir]:
        if not directory.exists():
            directory.mkdir(parents=True)
            console.print(f"[green]+[/green] Created directory: {directory}")
        else:
            console.print(f"  Directory exists: {directory}")

    # Create config.yaml from example
    config_example = config_dir / "config.yaml.example"
    config_yaml = config_dir / "config.yaml"

    if config_yaml.exists() and not force:
        console.print(
            f"[yellow]Warning:[/yellow] {config_yaml} already exists. "
            "Use --force to overwrite."
        )
    else:
        if config_example.exists():
            import shutil

            shutil.copy(config_example, config_yaml)
            console.print(f"[green]+[/green] Created configuration file: {config_yaml}")
        else:
            console.print(
                f"[red]Error:[/red] {config_example} not found.",
                style="bold",
            )
            sys.exit(1)

    console.print("\n[bold green]Initialization complete![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Edit config/config.yaml and set your JV-Link service key")
    console.print("  2. Run: jltsql fetch --help")


@cli.command()
def status():
    """Show JLTSQL status."""
    console.print("[bold cyan]JLTSQL Status[/bold cyan]")
    console.print(f"Version: {__version__}")
    console.print("Status: [green]Ready[/green]")


@cli.command()
def version():
    """Show version information."""
    console.print(f"JLTSQL version {__version__}")
    console.print("Python version: " + sys.version.split()[0])


@cli.command()
@click.option("--from", "date_from", required=True, help="Start date (YYYYMMDD)")
@click.option("--to", "date_to", required=True, help="End date (YYYYMMDD)")
@click.option("--spec", "data_spec", required=True, help="Data specification (RACE, DIFF, etc.)")
@click.option("--db", type=click.Choice(["sqlite", "duckdb", "postgresql"]), default=None, help="Database type (default: from config)")
@click.option("--batch-size", default=1000, help="Batch size for imports (default: 1000)")
@click.pass_context
def fetch(ctx, date_from, date_to, data_spec, db, batch_size):
    """Fetch historical data from JRA-VAN DataLab.

    \b
    Examples:
      jltsql fetch --from 20240101 --to 20241231 --spec RACE
      jltsql fetch --from 20240101 --to 20241231 --spec DIFF
    """
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    from src.database.sqlite_handler import SQLiteDatabase
    from src.database.duckdb_handler import DuckDBDatabase
    from src.database.postgresql_handler import PostgreSQLDatabase
    from src.database.schema import SchemaManager
    from src.importer.batch import BatchProcessor

    config = ctx.obj.get("config")
    if not config and not db:
        console.print("[red]Error:[/red] No configuration found. Run 'jltsql init' first or use --db option.")
        sys.exit(1)

    # Determine database type
    if db:
        db_type = db
    else:
        db_type = config.database.get("type", "sqlite")

    console.print(f"[bold cyan]Fetching historical data from JRA-VAN...[/bold cyan]\n")
    console.print(f"  Date range: {date_from} → {date_to}")
    console.print(f"  Data spec:  {data_spec}")
    console.print(f"  Database:   {db_type}")
    console.print()

    try:
        # Initialize database
        if db_type == "sqlite":
            db_config = config.database if config else {"path": "data/keiba.db"}
            database = SQLiteDatabase(db_config)
        elif db_type == "duckdb":
            db_config = config.database if config else {"path": "data/keiba.duckdb"}
            database = DuckDBDatabase(db_config)
        elif db_type == "postgresql":
            if not config:
                console.print("[red]Error:[/red] PostgreSQL requires configuration file.")
                sys.exit(1)
            database = PostgreSQLDatabase(config.database)
        else:
            console.print(f"[red]Error:[/red] Unsupported database type: {db_type}")
            sys.exit(1)

        # Connect to database
        with database:
            # Ensure tables exist
            schema_manager = SchemaManager(database)
            missing_tables = schema_manager.get_missing_tables()

            if missing_tables:
                console.print(f"[yellow]Warning:[/yellow] {len(missing_tables)} tables are missing.")
                console.print("Creating tables...")

                for table_name in missing_tables:
                    schema_manager.create_table(table_name)

                console.print(f"[green]✓[/green] Created {len(missing_tables)} tables\n")

            # Process data
            processor = BatchProcessor(
                database=database,
                sid=config.jvlink.get("sid", "JLTSQL") if config else "JLTSQL",
                batch_size=batch_size
            )

            console.print("[bold]Processing data...[/bold]")

            result = processor.process_date_range(
                data_spec=data_spec,
                from_date=date_from,
                to_date=date_to
            )

            # Show results
            console.print()
            console.print("[bold green]✓ Fetch complete![/bold green]")
            console.print()
            console.print("[bold]Statistics:[/bold]")
            console.print(f"  Fetched:  {result['fetched']}")
            console.print(f"  Parsed:   {result['parsed']}")
            console.print(f"  Imported: {result['imported']}")
            console.print(f"  Failed:   {result['failed']}")
            console.print(f"  Batches:  {result.get('batches', 0)}")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}", style="bold")
        logger.error("Failed to fetch data", error=str(e), exc_info=True)
        sys.exit(1)


@cli.command()
@click.option("--daemon", is_flag=True, help="Run in background")
@click.option("--spec", "data_spec", default="RACE", help="Data specification (default: RACE)")
@click.option("--interval", default=60, help="Polling interval in seconds (default: 60)")
@click.option("--db", type=click.Choice(["sqlite", "duckdb", "postgresql"]), default=None, help="Database type (default: from config)")
@click.pass_context
def monitor(ctx, daemon, data_spec, interval, db):
    """Start real-time monitoring.

    \b
    Examples:
      jltsql monitor                        # Run in foreground
      jltsql monitor --daemon               # Run in background
      jltsql monitor --spec RACE --interval 30
    """
    from src.database.sqlite_handler import SQLiteDatabase
    from src.database.duckdb_handler import DuckDBDatabase
    from src.database.postgresql_handler import PostgreSQLDatabase
    from src.database.schema import SchemaManager
    from src.realtime.monitor import RealtimeMonitor

    config = ctx.obj.get("config")
    if not config and not db:
        console.print("[red]Error:[/red] No configuration found. Run 'jltsql init' first or use --db option.")
        sys.exit(1)

    # Determine database type
    if db:
        db_type = db
    else:
        db_type = config.database.get("type", "sqlite")

    console.print(f"[bold cyan]Starting real-time monitoring...[/bold cyan]\n")
    console.print(f"  Data spec:  {data_spec}")
    console.print(f"  Interval:   {interval}s")
    console.print(f"  Database:   {db_type}")
    console.print(f"  Mode:       {'daemon' if daemon else 'foreground'}")
    console.print()

    try:
        # Initialize database
        if db_type == "sqlite":
            db_config = config.database if config else {"path": "data/keiba.db"}
            database = SQLiteDatabase(db_config)
        elif db_type == "duckdb":
            db_config = config.database if config else {"path": "data/keiba.duckdb"}
            database = DuckDBDatabase(db_config)
        elif db_type == "postgresql":
            if not config:
                console.print("[red]Error:[/red] PostgreSQL requires configuration file.")
                sys.exit(1)
            database = PostgreSQLDatabase(config.database)
        else:
            console.print(f"[red]Error:[/red] Unsupported database type: {db_type}")
            sys.exit(1)

        # Connect to database
        with database:
            # Ensure tables exist
            schema_manager = SchemaManager(database)
            missing_tables = schema_manager.get_missing_tables()

            if missing_tables:
                console.print(f"[yellow]Warning:[/yellow] {len(missing_tables)} tables are missing.")
                console.print("Creating tables...")

                for table_name in missing_tables:
                    schema_manager.create_table(table_name)

                console.print(f"[green]✓[/green] Created {len(missing_tables)} tables\n")

            # Start monitoring
            monitor_obj = RealtimeMonitor(
                database=database,
                data_spec=data_spec,
                polling_interval=interval,
                sid=config.jvlink.get("sid", "JLTSQL") if config else "JLTSQL"
            )

            console.print("[bold green]Monitoring started![/bold green]")
            console.print("Press Ctrl+C to stop.\n")

            # Start in daemon or foreground mode
            monitor_obj.start(daemon=daemon)

            if daemon:
                console.print("\n[bold green]Monitoring running in background[/bold green]")
                status = monitor_obj.get_status()
                console.print(f"Started at: {status['started_at']}")
            else:
                # Foreground mode - wait for Ctrl+C
                try:
                    import time
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Stopping monitor...[/yellow]")
                    monitor_obj.stop()
                    console.print("[green]Monitor stopped.[/green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}", style="bold")
        logger.error("Failed to start monitoring", error=str(e), exc_info=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def stop(ctx):
    """Stop real-time monitoring."""
    console.print("[yellow]Note: This command is not yet implemented.[/yellow]")
    console.print("Would stop monitoring")


@cli.command()
@click.option("--db", type=click.Choice(["sqlite", "duckdb", "postgresql"]), default=None, help="Database type (default: from config)")
@click.option("--all", "create_all", is_flag=True, help="Create both NL_ and RT_ tables")
@click.option("--nl-only", is_flag=True, help="Create only NL_ (Normal Load) tables")
@click.option("--rt-only", is_flag=True, help="Create only RT_ (Real-Time) tables")
@click.pass_context
def create_tables(ctx, db, create_all, nl_only, rt_only):
    """Create database tables.

    \b
    Examples:
      jltsql create-tables                # Create all tables (from config)
      jltsql create-tables --db sqlite    # Create all tables in SQLite
      jltsql create-tables --nl-only      # Create only NL_* tables
      jltsql create-tables --rt-only      # Create only RT_* tables
    """
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from src.database.schema import SchemaManager
    from src.database.sqlite_handler import SQLiteDatabase
    from src.database.duckdb_handler import DuckDBDatabase
    from src.database.postgresql_handler import PostgreSQLDatabase

    config = ctx.obj.get("config")
    if not config and not db:
        console.print("[red]Error:[/red] No configuration found. Run 'jltsql init' first or use --db option.")
        sys.exit(1)

    # Determine database type
    if db:
        db_type = db
    else:
        db_type = config.database.get("type", "sqlite")

    console.print(f"[bold cyan]Creating database tables ({db_type})...[/bold cyan]\n")

    try:
        # Initialize database
        if db_type == "sqlite":
            db_config = config.database if config else {"path": "data/keiba.db"}
            database = SQLiteDatabase(db_config)
        elif db_type == "duckdb":
            db_config = config.database if config else {"path": "data/keiba.duckdb"}
            database = DuckDBDatabase(db_config)
        elif db_type == "postgresql":
            if not config:
                console.print("[red]Error:[/red] PostgreSQL requires configuration file.")
                sys.exit(1)
            database = PostgreSQLDatabase(config.database)
        else:
            console.print(f"[red]Error:[/red] Unsupported database type: {db_type}")
            sys.exit(1)

        # Connect to database
        with database:
            schema_manager = SchemaManager(database)

            # Determine which tables to create
            from src.database.schema import SCHEMAS

            if nl_only:
                tables_to_create = [name for name in SCHEMAS.keys() if name.startswith("NL_")]
            elif rt_only:
                tables_to_create = [name for name in SCHEMAS.keys() if name.startswith("RT_")]
            else:
                tables_to_create = list(SCHEMAS.keys())

            # Create tables with progress bar
            created_count = 0
            failed_count = 0

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"[cyan]Creating {len(tables_to_create)} tables...", total=len(tables_to_create))

                for table_name in tables_to_create:
                    progress.update(task, description=f"[cyan]Creating {table_name}...")

                    if schema_manager.create_table(table_name):
                        created_count += 1
                    else:
                        failed_count += 1

                    progress.advance(task)

            # Show results
            console.print()
            console.print(f"[green]✓[/green] Created {created_count} tables")
            if failed_count > 0:
                console.print(f"[yellow]⚠[/yellow] Failed to create {failed_count} tables")

            # Show table statistics
            nl_tables = len([n for n in tables_to_create if n.startswith("NL_")])
            rt_tables = len([n for n in tables_to_create if n.startswith("RT_")])

            console.print()
            console.print("[bold]Table Statistics:[/bold]")
            console.print(f"  NL_* tables (Normal Load): {nl_tables}")
            console.print(f"  RT_* tables (Real-Time):   {rt_tables}")
            console.print(f"  Total:                     {len(tables_to_create)}")

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}", style="bold")
        logger.error("Failed to create tables", error=str(e), exc_info=True)
        sys.exit(1)


@cli.command()
@click.option("--db", type=click.Choice(["sqlite", "duckdb", "postgresql"]), default=None, help="Database type (default: from config)")
@click.option("--table", help="Create indexes for specific table only")
@click.pass_context
def create_indexes(ctx, db, table):
    """Create database indexes for improved query performance.

    \b
    Creates optimized indexes on frequently queried columns:
    - Date fields (開催年月日, データ作成年月日)
    - Venue/Race fields (競馬場コード, レース番号)
    - Real-time fields (発表月日時分)
    - Composite indexes for JOIN optimization

    \b
    Examples:
      jltsql create-indexes                    # Create all indexes
      jltsql create-indexes --db sqlite        # Create indexes in SQLite
      jltsql create-indexes --table NL_RA      # Create indexes for NL_RA only
    """
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from src.database.indexes import IndexManager
    from src.database.sqlite_handler import SQLiteDatabase
    from src.database.duckdb_handler import DuckDBDatabase
    from src.database.postgresql_handler import PostgreSQLDatabase

    config = ctx.obj.get("config")
    if not config and not db:
        console.print("[red]Error:[/red] No configuration found. Run 'jltsql init' first or use --db option.")
        sys.exit(1)

    # Determine database type
    if db:
        db_type = db
    else:
        db_type = config.database.get("type", "sqlite")

    console.print(f"[bold cyan]Creating database indexes ({db_type})...[/bold cyan]\n")

    try:
        # Initialize database
        if db_type == "sqlite":
            db_config = config.database if config else {"path": "data/keiba.db"}
            database = SQLiteDatabase(db_config)
        elif db_type == "duckdb":
            db_config = config.database if config else {"path": "data/keiba.duckdb"}
            database = DuckDBDatabase(db_config)
        elif db_type == "postgresql":
            if not config:
                console.print("[red]Error:[/red] PostgreSQL requires configuration file.")
                sys.exit(1)
            database = PostgreSQLDatabase(config.database)
        else:
            console.print(f"[red]Error:[/red] Unsupported database type: {db_type}")
            sys.exit(1)

        # Connect to database
        with database:
            index_manager = IndexManager(database)

            # Create indexes for specific table or all tables
            if table:
                console.print(f"Creating indexes for table: {table}")
                result = index_manager.create_indexes(table)

                if result:
                    index_count = index_manager.get_index_count(table)
                    console.print(f"[green]✓[/green] Created {index_count} indexes for {table}")
                else:
                    console.print(f"[red]✗[/red] Failed to create indexes for {table}")
                    sys.exit(1)
            else:
                console.print("Creating indexes for all tables...")

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("[cyan]Creating indexes...", total=None)

                    results = index_manager.create_all_indexes()

                    progress.update(task, description="[green]Indexes created!")

                # Show results
                total_indexes = sum(results.values())
                total_tables = len(results)

                console.print()
                console.print(f"[green]✓[/green] Created {total_indexes} indexes across {total_tables} tables")

                # Show breakdown
                console.print()
                console.print("[bold]Index Statistics:[/bold]")
                nl_indexes = sum(count for table, count in results.items() if table.startswith("NL_"))
                rt_indexes = sum(count for table, count in results.items() if table.startswith("RT_"))

                console.print(f"  NL_* tables: {nl_indexes} indexes")
                console.print(f"  RT_* tables: {rt_indexes} indexes")
                console.print(f"  Total:       {total_indexes} indexes")

                console.print()
                console.print("[dim]Note: Indexes improve query performance for date ranges,")
                console.print("      venue/race searches, and real-time data queries.[/dim]")

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}", style="bold")
        logger.error("Failed to create indexes", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    cli(obj={})
