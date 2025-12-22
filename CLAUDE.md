# jrvltsql Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-15

## Active Technologies

- **Python 3.12 (32-bit)** (REQUIRED for UmaConn/NAR support) + pywin32 (COM API), click (CLI), rich (UI), structlog (logging), SQLite/PostgreSQL (database)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.12 (32-bit): Follow standard conventions

## Architecture Constraints

### Database: SQLite / PostgreSQL

- UmaConn (NAR) API requires 32-bit Python
- SQLite provides stable, lightweight database solution (default)
- PostgreSQL supported via pg8000 driver (pure Python, 32-bit compatible)
- DuckDB is NOT supported (requires 64-bit Python)

### Python Version: 32-bit Required

- **Primary Reason**: UmaConn COM API is 32-bit DLL only
- **64-bit Alternative Tested**: DllSurrogate approach causes DAX errors
- **Minimum Version**: Python 3.12 (32-bit)
- **Compatibility**: Works with both JV-Link (JRA) and UmaConn (NAR)

## Recent Changes

- 001-local-racing-support: Migrated to 32-bit Python + SQLite/PostgreSQL for stable UmaConn/NAR support
- SQLite (default) and PostgreSQL supported; DuckDB removed (64-bit only)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
