# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-12-06

### Added
- DuckDB database support for analytical workloads (OLAP optimized)
- DuckDB configuration options: `memory_limit`, `threads`, `read_only`
- `--db duckdb` option for CLI commands (`fetch`, `monitor`, `realtime start`, `realtime timeseries`)
- NL_HR schema: HenkanDoWaku5-8 columns for complete refund slot coverage

### Fixed
- DuckDB UPSERT syntax: Use `ON CONFLICT (pk_cols) DO UPDATE SET` instead of `INSERT OR REPLACE`
- DuckDB identifier quoting: Use double quotes (SQL standard) with proper escaping
- Primary key detection via `PRAGMA table_info()` for proper conflict resolution
- Rollback error handling: Log warnings instead of silent failures

### Changed
- Updated project metadata to include DuckDB in description and keywords

## [2.0.10] - 2025-12-06

### Added
- Time-series odds: Custom period selection for historical odds data
- Performance improvements for time-series data fetching

## [2.0.4] - 2025-12-05

### Added
- Initial public release
- SQLite and PostgreSQL database support
- JV-Link integration for real-time data fetching
- Quickstart wizard for easy setup
- CLI commands for data management

[2.1.0]: https://github.com/miyamamoto/jrvltsql/compare/v2.0.10...v2.1.0
[2.0.10]: https://github.com/miyamamoto/jrvltsql/compare/v2.0.4...v2.0.10
[2.0.4]: https://github.com/miyamamoto/jrvltsql/releases/tag/v2.0.4
