#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for RA Parser with JRA-VAN standard type conversion."""

import unittest
from datetime import date, time
from decimal import Decimal

from src.parser.ra_parser_jravan import RAParserJRAVAN


class TestRAParserJRAVAN(unittest.TestCase):
    """Test RA parser with type conversions."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = RAParserJRAVAN()

    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        self.assertEqual(self.parser.record_type, "RA")
        self.assertGreater(len(self.parser._fields), 0)

    def test_field_names(self):
        """Test field names match JRA-VAN standard."""
        field_names = self.parser.get_field_names()

        # Check key fields exist with standard names
        self.assertIn("RecordSpec", field_names)
        self.assertIn("MakeDate", field_names)
        self.assertIn("Year", field_names)
        self.assertIn("MonthDay", field_names)
        self.assertIn("JyoCD", field_names)
        self.assertIn("Kaiji", field_names)
        self.assertIn("RaceNum", field_names)
        self.assertIn("Kyori", field_names)
        self.assertIn("HassoTime", field_names)
        self.assertIn("TorokuTosu", field_names)
        self.assertIn("Honsyokin1", field_names)
        self.assertIn("LapTime1", field_names)

    def test_parse_sample_record(self):
        """Test parsing a sample RA record with type conversions."""
        # Create a sample RA record (simplified, focusing on key fields)
        # Format: RA + DataKubun(1) + MakeDate(8) + Year(4) + MonthDay(4) + ...
        sample_data = (
            b"RA"                          # RecordSpec (2)
            b"1"                           # DataKubun (1)
            b"20231115"                    # MakeDate (8) - should convert to date(2023, 11, 15)
            b"2023"                        # Year (4) - should convert to 2023
            b"1115"                        # MonthDay (4) - should convert to 1115
            b"06"                          # JyoCD (2) - Tokyo
            b"03"                          # Kaiji (2) - should convert to 3
            b"08"                          # Nichiji (2) - should convert to 8
            b"11"                          # RaceNum (2) - should convert to 11
            b"0"                           # YoubiCD (1)
            b"0001"                        # TokuNum (4)
            + b" " * 60                    # Hondai (60)
            + b" " * 60                    # Fukudai (60)
            + b" " * 60                    # Kakko (60)
            + b" " * 120                   # HondaiEng (120)
            + b" " * 120                   # FukudaiEng (120)
            + b" " * 120                   # KakkoEng (120)
            + b" " * 20                    # Ryakusyo10 (20)
            + b" " * 12                    # Ryakusyo6 (12)
            + b" " * 6                     # Ryakusyo3 (6)
            + b"0"                         # Kubun (1)
            + b"001"                       # Nkai (3)
            + b"1"                         # GradeCD (1)
            + b"0"                         # GradeCDBefore (1)
            + b"11"                        # SyubetuCD (2)
            + b"000"                       # KigoCD (3)
            + b"0"                         # JyuryoCD (1)
            + b" " * 15                    # JyokenCD1-5 (15)
            + b" " * 60                    # JyokenName (60)
            + b"2000"                      # Kyori (4) - should convert to 2000
            + b"    "                      # KyoriBefore (4)
            + b"11"                        # TrackCD (2)
            + b"  "                        # TrackCDBefore (2)
            + b"01"                        # CourseKubunCD (2)
            + b"  "                        # CourseKubunCDBefore (2)
            + b"00050000"                  # Honsyokin1 (8) - should convert to 50000
            + b"00030000"                  # Honsyokin2 (8)
            + b"00020000"                  # Honsyokin3 (8)
            + b"00010000"                  # Honsyokin4 (8)
            + b"00005000"                  # Honsyokin5 (8)
            + b"        "                  # Honsyokin6 (8)
            + b"        "                  # Honsyokin7 (8)
            + b" " * 40                    # HonsyokinBefore1-5 (40)
            + b"00005000"                  # Fukasyokin1 (8)
            + b"00003000"                  # Fukasyokin2 (8)
            + b"00002000"                  # Fukasyokin3 (8)
            + b"        "                  # Fukasyokin4 (8)
            + b"        "                  # Fukasyokin5 (8)
            + b" " * 24                    # FukasyokinBefore1-3 (24)
            + b"1530"                      # HassoTime (4) - should convert to time(15, 30)
            + b"    "                      # HassoTimeBefore (4)
            + b"18"                        # TorokuTosu (2) - should convert to 18
            + b"16"                        # SyussoTosu (2) - should convert to 16
            + b"16"                        # NyusenTosu (2) - should convert to 16
            + b"1"                         # TenkoCD (1)
            + b"2"                         # SibaBabaCD (1)
            + b"3"                         # DirtBabaCD (1)
            + b"123"                       # LapTime1 (3) - should convert to Decimal("12.3")
            + b"125"                       # LapTime2 (3)
            + b"120"                       # LapTime3 (3)
            + b"118"                       # LapTime4 (3)
            + b"115"                       # LapTime5 (3)
            + b"112"                       # LapTime6 (3)
            + b"110"                       # LapTime7 (3)
            + b"108"                       # LapTime8 (3)
            + b" " * (3 * 17)              # LapTime9-25 (51)
            + b"    "                      # SyogaiMileTime (4)
            + b"361"                       # HaronTimeS3 (3) - should convert to Decimal("36.1")
            + b"482"                       # HaronTimeS4 (3)
            + b"350"                       # HaronTimeL3 (3)
            + b"465"                       # HaronTimeL4 (3)
            + b" " * (72 * 4)              # Corner positions (288)
            + b"0"                         # RecordUpKubun (1)
        )

        result = self.parser.parse(sample_data)

        # Verify type conversions
        self.assertEqual(result["RecordSpec"], "RA")
        self.assertEqual(result["DataKubun"], "1")

        # Date conversion
        self.assertIsInstance(result["MakeDate"], date)
        self.assertEqual(result["MakeDate"], date(2023, 11, 15))

        # Integer conversions
        self.assertIsInstance(result["Year"], int)
        self.assertEqual(result["Year"], 2023)

        self.assertIsInstance(result["MonthDay"], int)
        self.assertEqual(result["MonthDay"], 1115)

        self.assertIsInstance(result["Kaiji"], int)
        self.assertEqual(result["Kaiji"], 3)

        self.assertIsInstance(result["RaceNum"], int)
        self.assertEqual(result["RaceNum"], 11)

        self.assertIsInstance(result["Kyori"], int)
        self.assertEqual(result["Kyori"], 2000)

        self.assertIsInstance(result["TorokuTosu"], int)
        self.assertEqual(result["TorokuTosu"], 18)

        # Prize money conversion
        self.assertIsInstance(result["Honsyokin1"], int)
        self.assertEqual(result["Honsyokin1"], 50000)

        # Time conversion
        self.assertIsInstance(result["HassoTime"], time)
        self.assertEqual(result["HassoTime"], time(15, 30))

        # Lap time conversions (DECIMAL)
        self.assertIsInstance(result["LapTime1"], Decimal)
        self.assertEqual(result["LapTime1"], Decimal("12.3"))

        self.assertIsInstance(result["LapTime2"], Decimal)
        self.assertEqual(result["LapTime2"], Decimal("12.5"))

        # Haron time conversions
        self.assertIsInstance(result["HaronTimeS3"], Decimal)
        self.assertEqual(result["HaronTimeS3"], Decimal("36.1"))

        self.assertIsInstance(result["HaronTimeL3"], Decimal)
        self.assertEqual(result["HaronTimeL3"], Decimal("35.0"))

    def test_empty_values_convert_to_none(self):
        """Test that empty/whitespace values convert to None."""
        # Create record with empty values
        sample_data = (
            b"RA1"
            + b"        "  # MakeDate (8) - empty
            + b"    "      # Year (4) - empty
            + b"    "      # MonthDay (4) - empty
            + b"  "        # JyoCD (2)
            + b"  "        # Kaiji (2) - empty
            + b"  "        # Nichiji (2)
            + b"  "        # RaceNum (2)
            + b" " * 1252  # Padding to complete record
        )

        result = self.parser.parse(sample_data)

        # Empty values should be None
        self.assertIsNone(result["MakeDate"])
        self.assertIsNone(result["Year"])
        self.assertIsNone(result["MonthDay"])
        self.assertIsNone(result["Kaiji"])


if __name__ == '__main__':
    unittest.main()
