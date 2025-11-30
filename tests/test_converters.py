#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for type conversion functions."""

import unittest
from datetime import date, time
from decimal import Decimal

from src.parser.converters import (
    to_date,
    to_time,
    to_int,
    to_decimal,
    to_race_time,
    to_lap_time,
    to_weight,
    to_odds,
    to_prize_money,
    to_month_day,
    convert_value,
    ConversionError,
)


class TestDateConversion(unittest.TestCase):
    """Test date conversion functions."""

    def test_to_date_valid(self):
        """Test valid date conversion."""
        self.assertEqual(to_date("20231115"), date(2023, 11, 15))
        self.assertEqual(to_date("20240101"), date(2024, 1, 1))
        self.assertEqual(to_date("19991231"), date(1999, 12, 31))

    def test_to_date_boundary(self):
        """Test boundary date values."""
        # Test leap year
        self.assertEqual(to_date("20240229"), date(2024, 2, 29))
        # Test first day of month
        self.assertEqual(to_date("20230101"), date(2023, 1, 1))
        # Test last day of month
        self.assertEqual(to_date("20231231"), date(2023, 12, 31))

    def test_to_date_empty(self):
        """Test empty date values."""
        self.assertIsNone(to_date(""))
        self.assertIsNone(to_date("   "))
        self.assertIsNone(to_date("00000000"))

    def test_to_date_invalid(self):
        """Test invalid date values."""
        with self.assertRaises(ConversionError):
            to_date("202311")  # Too short

        with self.assertRaises(ConversionError):
            to_date("20231301")  # Invalid month

        with self.assertRaises(ConversionError):
            to_date("20231132")  # Invalid day

        with self.assertRaises(ConversionError):
            to_date("20230229")  # Invalid leap year date


class TestTimeConversion(unittest.TestCase):
    """Test time conversion functions."""

    def test_to_time_valid(self):
        """Test valid time conversion."""
        self.assertEqual(to_time("1530"), time(15, 30))
        self.assertEqual(to_time("0000"), time(0, 0))
        self.assertEqual(to_time("2359"), time(23, 59))

    def test_to_time_empty(self):
        """Test empty time values."""
        self.assertIsNone(to_time(""))
        self.assertIsNone(to_time("   "))

    def test_to_time_invalid(self):
        """Test invalid time values."""
        with self.assertRaises(ConversionError):
            to_time("25:00")  # Invalid hour

        with self.assertRaises(ConversionError):
            to_time("1560")  # Invalid minute


class TestIntConversion(unittest.TestCase):
    """Test integer conversion functions."""

    def test_to_int_valid(self):
        """Test valid integer conversion."""
        self.assertEqual(to_int("123"), 123)
        self.assertEqual(to_int("  45  "), 45)
        self.assertEqual(to_int("0"), 0)

    def test_to_int_empty(self):
        """Test empty integer values."""
        self.assertIsNone(to_int(""))
        self.assertIsNone(to_int("   "))

    def test_to_int_zeros(self):
        """Test all zeros."""
        self.assertEqual(to_int("000"), 0)
        self.assertEqual(to_int("0000"), 0)

    def test_to_int_negative(self):
        """Test negative integers."""
        self.assertEqual(to_int("-123"), -123)
        self.assertEqual(to_int("  -45  "), -45)

    def test_to_int_invalid(self):
        """Test invalid integer values."""
        with self.assertRaises(ConversionError):
            to_int("abc")


class TestDecimalConversion(unittest.TestCase):
    """Test decimal conversion functions."""

    def test_to_decimal_valid(self):
        """Test valid decimal conversion."""
        self.assertEqual(to_decimal("1234", 1), Decimal("123.4"))
        self.assertEqual(to_decimal("550", 1), Decimal("55.0"))
        self.assertEqual(to_decimal("123", 1), Decimal("12.3"))

    def test_to_decimal_empty(self):
        """Test empty decimal values."""
        self.assertIsNone(to_decimal("", 1))
        self.assertIsNone(to_decimal("   ", 1))

    def test_to_decimal_with_different_places(self):
        """Test decimal conversion with different decimal places."""
        self.assertEqual(to_decimal("12345", 2), Decimal("123.45"))
        self.assertEqual(to_decimal("12345", 3), Decimal("12.345"))

    def test_to_decimal_zero(self):
        """Test decimal conversion of zero."""
        self.assertEqual(to_decimal("0", 1), Decimal("0.0"))
        self.assertEqual(to_decimal("000", 1), Decimal("0.0"))

    def test_to_decimal_invalid(self):
        """Test invalid decimal values."""
        with self.assertRaises(ConversionError):
            to_decimal("abc", 1)


class TestRaceTimeConversion(unittest.TestCase):
    """Test race time conversion."""

    def test_to_race_time_valid(self):
        """Test valid race time conversion."""
        self.assertEqual(to_race_time("1234"), Decimal("123.4"))
        self.assertEqual(to_race_time("0593"), Decimal("59.3"))
        self.assertEqual(to_race_time("1500"), Decimal("150.0"))

    def test_to_race_time_empty(self):
        """Test empty race time."""
        self.assertIsNone(to_race_time(""))
        self.assertIsNone(to_race_time("    "))


class TestLapTimeConversion(unittest.TestCase):
    """Test lap time conversion."""

    def test_to_lap_time_valid(self):
        """Test valid lap time conversion."""
        self.assertEqual(to_lap_time("123"), Decimal("12.3"))
        self.assertEqual(to_lap_time("115"), Decimal("11.5"))
        self.assertEqual(to_lap_time("100"), Decimal("10.0"))

    def test_to_lap_time_empty(self):
        """Test empty lap time."""
        self.assertIsNone(to_lap_time(""))


class TestWeightConversion(unittest.TestCase):
    """Test weight conversion."""

    def test_to_weight_valid(self):
        """Test valid weight conversion."""
        self.assertEqual(to_weight("550"), Decimal("55.0"))
        self.assertEqual(to_weight("580"), Decimal("58.0"))
        self.assertEqual(to_weight("510"), Decimal("51.0"))

    def test_to_weight_empty(self):
        """Test empty weight."""
        self.assertIsNone(to_weight(""))


class TestOddsConversion(unittest.TestCase):
    """Test odds conversion."""

    def test_to_odds_valid(self):
        """Test valid odds conversion."""
        self.assertEqual(to_odds("0123"), Decimal("12.3"))
        self.assertEqual(to_odds("9999"), Decimal("999.9"))
        self.assertEqual(to_odds("0010"), Decimal("1.0"))

    def test_to_odds_empty(self):
        """Test empty odds."""
        self.assertIsNone(to_odds(""))


class TestPrizeMoneyConversion(unittest.TestCase):
    """Test prize money conversion."""

    def test_to_prize_money_valid(self):
        """Test valid prize money conversion."""
        self.assertEqual(to_prize_money("00050000"), 50000)
        self.assertEqual(to_prize_money("00000100"), 100)
        self.assertEqual(to_prize_money("10000000"), 10000000)

    def test_to_prize_money_empty(self):
        """Test empty prize money."""
        self.assertIsNone(to_prize_money(""))


class TestMonthDayConversion(unittest.TestCase):
    """Test month-day conversion."""

    def test_to_month_day_valid(self):
        """Test valid month-day conversion."""
        self.assertEqual(to_month_day("1115"), 1115)
        self.assertEqual(to_month_day("0101"), 101)
        self.assertEqual(to_month_day("1231"), 1231)

    def test_to_month_day_boundary(self):
        """Test boundary month-day values."""
        self.assertEqual(to_month_day("0131"), 131)  # Jan 31
        self.assertEqual(to_month_day("1201"), 1201)  # Dec 1

    def test_to_month_day_empty(self):
        """Test empty month-day."""
        self.assertIsNone(to_month_day(""))
        self.assertIsNone(to_month_day("0000"))

    def test_to_month_day_invalid(self):
        """Test invalid month-day."""
        with self.assertRaises(ConversionError):
            to_month_day("1332")  # Invalid day

        with self.assertRaises(ConversionError):
            to_month_day("1301")  # Invalid month

        with self.assertRaises(ConversionError):
            to_month_day("0001")  # Invalid month (0)


class TestConvertValue(unittest.TestCase):
    """Test generic convert_value function."""

    def test_convert_value_date(self):
        """Test convert_value with DATE type."""
        result = convert_value("20231115", "DATE")
        self.assertEqual(result, date(2023, 11, 15))

    def test_convert_value_time(self):
        """Test convert_value with TIME type."""
        result = convert_value("1530", "TIME")
        self.assertEqual(result, time(15, 30))

    def test_convert_value_int(self):
        """Test convert_value with INT type."""
        result = convert_value("123", "INT")
        self.assertEqual(result, 123)

    def test_convert_value_smallint(self):
        """Test convert_value with SMALLINT type."""
        result = convert_value("42", "SMALLINT")
        self.assertEqual(result, 42)

    def test_convert_value_integer(self):
        """Test convert_value with INTEGER type."""
        result = convert_value("999", "INTEGER")
        self.assertEqual(result, 999)

    def test_convert_value_decimal(self):
        """Test convert_value with DECIMAL type."""
        result = convert_value("1234", "DECIMAL", decimal_places=2)
        self.assertEqual(result, Decimal("12.34"))

    def test_convert_value_race_time(self):
        """Test convert_value with RACE_TIME type."""
        result = convert_value("1234", "RACE_TIME")
        self.assertEqual(result, Decimal("123.4"))

    def test_convert_value_lap_time(self):
        """Test convert_value with LAP_TIME type."""
        result = convert_value("123", "LAP_TIME")
        self.assertEqual(result, Decimal("12.3"))

    def test_convert_value_weight(self):
        """Test convert_value with WEIGHT type."""
        result = convert_value("550", "WEIGHT")
        self.assertEqual(result, Decimal("55.0"))

    def test_convert_value_odds(self):
        """Test convert_value with ODDS type."""
        result = convert_value("0123", "ODDS")
        self.assertEqual(result, Decimal("12.3"))

    def test_convert_value_prize_money(self):
        """Test convert_value with PRIZE_MONEY type."""
        result = convert_value("00050000", "PRIZE_MONEY")
        self.assertEqual(result, 50000)

    def test_convert_value_month_day(self):
        """Test convert_value with MONTH_DAY type."""
        result = convert_value("1115", "MONTH_DAY")
        self.assertEqual(result, 1115)

    def test_convert_value_unknown_type(self):
        """Test convert_value with unknown type."""
        with self.assertRaises(ConversionError):
            convert_value("123", "UNKNOWN_TYPE")

    def test_convert_value_case_insensitive(self):
        """Test convert_value with lowercase type name."""
        result = convert_value("123", "int")
        self.assertEqual(result, 123)

    def test_convert_value_empty_string(self):
        """Test convert_value with empty string."""
        result = convert_value("", "INT")
        self.assertIsNone(result)

    def test_convert_value_conversion_error(self):
        """Test convert_value with value that causes conversion error."""
        with self.assertRaises(ConversionError):
            convert_value("invalid", "INT")

        with self.assertRaises(ConversionError):
            convert_value("20231301", "DATE")  # Invalid date


if __name__ == '__main__':
    unittest.main()
