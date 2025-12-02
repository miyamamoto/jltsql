"""Type conversion functions for JV-Data parsing.

This module provides conversion functions to transform JV-Data fixed-length
text fields into appropriate Python/database types.
"""

from datetime import date, time, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Optional, Union


class ConversionError(Exception):
    """Error during data type conversion."""
    pass


def to_date(value: str) -> Optional[date]:
    """Convert YYYYMMDD string to date.

    Args:
        value: Date string in YYYYMMDD format (e.g., "20231115")

    Returns:
        date object or None if value is empty/invalid

    Examples:
        >>> to_date("20231115")
        datetime.date(2023, 11, 15)
        >>> to_date("00000000")
        None
        >>> to_date("")
        None
    """
    if not value or not value.strip() or value.strip() == "0" * 8:
        return None

    value = value.strip()
    if len(value) != 8:
        raise ConversionError(f"Invalid date format: {value} (expected YYYYMMDD)")

    try:
        year = int(value[0:4])
        month = int(value[4:6])
        day = int(value[6:8])

        # Validate date components
        if year < 1900 or year > 2100:
            raise ConversionError(f"Invalid year: {year}")
        if month < 1 or month > 12:
            raise ConversionError(f"Invalid month: {month}")
        if day < 1 or day > 31:
            raise ConversionError(f"Invalid day: {day}")

        return date(year, month, day)
    except (ValueError, IndexError) as e:
        raise ConversionError(f"Failed to convert '{value}' to date: {e}")


def to_time(value: str) -> Optional[time]:
    """Convert HHMM string to time.

    Args:
        value: Time string in HHMM format (e.g., "1530" for 15:30)

    Returns:
        time object or None if value is empty/invalid

    Examples:
        >>> to_time("1530")
        datetime.time(15, 30)
        >>> to_time("0000")
        datetime.time(0, 0)
        >>> to_time("")
        None
    """
    if not value or not value.strip():
        return None

    value = value.strip()

    # 4桁: HHMM形式（時分のみ）
    # 8桁: MMDDHHMM形式（発表月日時分）- 末尾4桁を使用
    if len(value) == 4:
        time_part = value
    elif len(value) == 8:
        # MMDDHHMM形式: 末尾4桁がHHMM
        time_part = value[4:8]
    else:
        raise ConversionError(f"Invalid time format: {value} (expected HHMM or MMDDHHMM)")

    try:
        hour = int(time_part[0:2])
        minute = int(time_part[2:4])

        if hour < 0 or hour > 23:
            raise ConversionError(f"Invalid hour: {hour}")
        if minute < 0 or minute > 59:
            raise ConversionError(f"Invalid minute: {minute}")

        return time(hour, minute, 0)
    except (ValueError, IndexError) as e:
        raise ConversionError(f"Failed to convert '{value}' to time: {e}")


def to_int(value: str) -> Optional[int]:
    """Convert string to integer.

    Args:
        value: Numeric string

    Returns:
        int or None if value is empty/invalid

    Examples:
        >>> to_int("123")
        123
        >>> to_int("  45  ")
        45
        >>> to_int("")
        None
        >>> to_int("   ")
        None
    """
    if not value or not value.strip():
        return None

    try:
        return int(value.strip())
    except ValueError:
        # Check if all zeros
        if value.strip() == "0" * len(value.strip()):
            return 0
        raise ConversionError(f"Failed to convert '{value}' to int")


def to_decimal(value: str, decimal_places: int = 1) -> Optional[Decimal]:
    """Convert string to Decimal.

    For JV-Data, numeric fields are often stored without decimal points.
    For example, "1234" might represent 123.4 seconds.

    Args:
        value: Numeric string
        decimal_places: Number of decimal places (default: 1)

    Returns:
        Decimal or None if value is empty/invalid

    Examples:
        >>> to_decimal("1234", 1)
        Decimal('123.4')
        >>> to_decimal("550", 1)
        Decimal('55.0')
        >>> to_decimal("123", 1)
        Decimal('12.3')
        >>> to_decimal("")
        None
    """
    if not value or not value.strip():
        return None

    try:
        int_value = int(value.strip())

        # Divide by 10^decimal_places
        divisor = 10 ** decimal_places
        return Decimal(int_value) / Decimal(divisor)
    except (ValueError, InvalidOperation):
        raise ConversionError(f"Failed to convert '{value}' to Decimal")


def to_race_time(value: str) -> Optional[Decimal]:
    """Convert race time string to Decimal (seconds).

    Race times are stored as TEXT(4) in format like "1234" = 123.4 seconds.

    Args:
        value: Time string (4 digits, e.g., "1234")

    Returns:
        Decimal representing seconds

    Examples:
        >>> to_race_time("1234")
        Decimal('123.4')
        >>> to_race_time("0593")
        Decimal('59.3')
    """
    return to_decimal(value, decimal_places=1)


def to_lap_time(value: str) -> Optional[Decimal]:
    """Convert lap time string to Decimal (seconds).

    Lap times are stored as TEXT(3) in format like "123" = 12.3 seconds.

    Args:
        value: Lap time string (3 digits, e.g., "123")

    Returns:
        Decimal representing seconds

    Examples:
        >>> to_lap_time("123")
        Decimal('12.3')
        >>> to_lap_time("115")
        Decimal('11.5')
    """
    return to_decimal(value, decimal_places=1)


def to_weight(value: str) -> Optional[Decimal]:
    """Convert weight (斤量) string to Decimal (kg).

    Weight is stored as TEXT(3) in format like "550" = 55.0 kg.

    Args:
        value: Weight string (3 digits, e.g., "550")

    Returns:
        Decimal representing kg

    Examples:
        >>> to_weight("550")
        Decimal('55.0')
        >>> to_weight("580")
        Decimal('58.0')
    """
    return to_decimal(value, decimal_places=1)


def to_odds(value: str) -> Optional[Decimal]:
    """Convert odds string to Decimal.

    Odds are stored as TEXT(4) in format like "0123" = 12.3倍.

    Args:
        value: Odds string (4 digits, e.g., "0123")

    Returns:
        Decimal representing odds multiplier

    Examples:
        >>> to_odds("0123")
        Decimal('12.3')
        >>> to_odds("9999")
        Decimal('999.9')
    """
    return to_decimal(value, decimal_places=1)


def to_prize_money(value: str) -> Optional[int]:
    """Convert prize money string to integer (千円単位).

    Prize money is stored as TEXT(8) in 千円 units.

    Args:
        value: Prize money string (e.g., "00050000" = 50,000千円 = 5000万円)

    Returns:
        int representing prize money in 千円 units

    Examples:
        >>> to_prize_money("00050000")
        50000
        >>> to_prize_money("00000100")
        100
    """
    return to_int(value)


def to_month_day(value: str) -> Optional[int]:
    """Convert MMDD string to integer.

    Args:
        value: Month-day string in MMDD format (e.g., "1115")

    Returns:
        int or None if value is empty/invalid

    Examples:
        >>> to_month_day("1115")
        1115
        >>> to_month_day("0101")
        101
        >>> to_month_day("1231")
        1231
    """
    if not value or not value.strip() or value.strip() == "0" * 4:
        return None

    value = value.strip()
    if len(value) != 4:
        raise ConversionError(f"Invalid month-day format: {value} (expected MMDD)")

    try:
        month = int(value[0:2])
        day = int(value[2:4])

        if month < 1 or month > 12:
            raise ConversionError(f"Invalid month: {month}")
        if day < 1 or day > 31:
            raise ConversionError(f"Invalid day: {day}")

        return int(value)
    except (ValueError, IndexError) as e:
        raise ConversionError(f"Failed to convert '{value}' to month-day: {e}")


# Type converter registry
CONVERTERS = {
    'DATE': to_date,
    'TIME': to_time,
    'INT': to_int,
    'SMALLINT': to_int,
    'INTEGER': to_int,
    'DECIMAL': to_decimal,
    'RACE_TIME': to_race_time,
    'LAP_TIME': to_lap_time,
    'WEIGHT': to_weight,
    'ODDS': to_odds,
    'PRIZE_MONEY': to_prize_money,
    'MONTH_DAY': to_month_day,
}


def convert_value(value: str, target_type: str, **kwargs) -> Any:
    """Convert value to target type using registered converter.

    Args:
        value: String value to convert
        target_type: Target type name (e.g., 'DATE', 'INT', 'DECIMAL')
        **kwargs: Additional arguments for converter

    Returns:
        Converted value

    Raises:
        ConversionError: If conversion fails

    Examples:
        >>> convert_value("20231115", "DATE")
        datetime.date(2023, 11, 15)
        >>> convert_value("1234", "RACE_TIME")
        Decimal('123.4')
        >>> convert_value("550", "WEIGHT")
        Decimal('55.0')
    """
    converter = CONVERTERS.get(target_type.upper())
    if not converter:
        raise ConversionError(f"Unknown converter type: {target_type}")

    try:
        return converter(value, **kwargs)
    except Exception as e:
        raise ConversionError(f"Conversion failed for '{value}' to {target_type}: {e}")
