#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for real-time monitoring."""

import unittest
from unittest.mock import MagicMock, patch, call

from src.realtime.monitor import RealtimeMonitor
from src.realtime.updater import RealtimeUpdater


class TestRealtimeUpdater(unittest.TestCase):
    """Test cases for RealtimeUpdater."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = MagicMock()
        self.updater = RealtimeUpdater(self.mock_db)

    def test_init(self):
        """Test RealtimeUpdater initialization."""
        self.assertEqual(self.updater.database, self.mock_db)
        self.assertIsNotNone(self.updater.parser_factory)

    def test_process_record_new(self):
        """Test processing new record (headDataKubun=1)."""
        # Mock parsed data with headDataKubun=1 (new)
        test_record = "RA11202406010603"

        with patch.object(self.updater.parser_factory, 'parse') as mock_parse:
            mock_parse.return_value = {
                "RecordSpec": "RA",
                "headDataKubun": "1",
                "idYear": "2024",
                "idJyoCD": "06",
                "idRaceNum": "01",
                "RaceName": "Test Race",
            }

            result = self.updater.process_record(test_record)

            self.assertIsNotNone(result)
            self.assertEqual(result["operation"], "insert")
            self.assertEqual(result["table"], "NL_RA_RACE")
            self.assertTrue(result["success"])
            self.mock_db.insert.assert_called_once()

    def test_process_record_update(self):
        """Test processing update record (headDataKubun=2)."""
        test_record = "RA21202406010603"

        with patch.object(self.updater.parser_factory, 'parse') as mock_parse:
            mock_parse.return_value = {
                "RecordSpec": "RA",
                "headDataKubun": "2",
                "idYear": "2024",
                "idJyoCD": "06",
                "idRaceNum": "01",
                "RaceName": "Updated Race",
            }

            result = self.updater.process_record(test_record)

            self.assertIsNotNone(result)
            self.assertEqual(result["operation"], "update")
            self.assertEqual(result["table"], "NL_RA_RACE")

    def test_process_record_delete(self):
        """Test processing delete record (headDataKubun=3)."""
        test_record = "RA31202406010603"

        with patch.object(self.updater.parser_factory, 'parse') as mock_parse:
            mock_parse.return_value = {
                "RecordSpec": "RA",
                "headDataKubun": "3",
                "idYear": "2024",
                "idJyoCD": "06",
                "idRaceNum": "01",
            }

            result = self.updater.process_record(test_record)

            self.assertIsNotNone(result)
            self.assertEqual(result["operation"], "delete")
            self.assertEqual(result["table"], "NL_RA_RACE")

    def test_process_record_invalid(self):
        """Test processing invalid record."""
        test_record = "INVALID"

        with patch.object(self.updater.parser_factory, 'parse') as mock_parse:
            mock_parse.return_value = None

            result = self.updater.process_record(test_record)

            self.assertIsNone(result)

    def test_handle_new_record_se(self):
        """Test handling new SE (horse race) record."""
        test_record = "SE11202406010603"

        with patch.object(self.updater.parser_factory, 'parse') as mock_parse:
            mock_parse.return_value = {
                "RecordSpec": "SE",
                "headDataKubun": "1",
                "idYear": "2024",
                "idBangou": "1",
                "UmaName": "Test Horse",
                "Kishu": "Test Jockey",
            }

            result = self.updater.process_record(test_record)

            self.assertEqual(result["table"], "NL_SE_RACE_UMA")

    def test_handle_new_record_hr(self):
        """Test handling new HR (payout) record."""
        test_record = "HR11202406010603"

        with patch.object(self.updater.parser_factory, 'parse') as mock_parse:
            mock_parse.return_value = {
                "RecordSpec": "HR",
                "headDataKubun": "1",
                "idYear": "2024",
                "TansyoPay1": "500",
                "FukusyoPay1": "200",
            }

            result = self.updater.process_record(test_record)

            self.assertEqual(result["table"], "NL_HR_PAY")


class TestRealtimeMonitor(unittest.TestCase):
    """Test cases for RealtimeMonitor."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = MagicMock()

    @patch('src.realtime.monitor.JVLinkWrapper')
    @patch('src.realtime.monitor.RealtimeUpdater')
    def test_init(self, mock_updater_class, mock_jvlink_class):
        """Test RealtimeMonitor initialization."""
        monitor = RealtimeMonitor(
            database=self.mock_db,
            data_spec="RACE",
            polling_interval=30
        )

        self.assertEqual(monitor.database, self.mock_db)
        self.assertEqual(monitor.data_spec, "RACE")
        self.assertEqual(monitor.polling_interval, 30)
        self.assertFalse(monitor._running)

    @patch('src.realtime.monitor.JVLinkWrapper')
    @patch('src.realtime.monitor.RealtimeUpdater')
    @patch('src.realtime.monitor.signal.signal')
    def test_start_and_stop(self, mock_signal, mock_updater_class, mock_jvlink_class):
        """Test monitor start and stop."""
        mock_jvlink = MagicMock()
        mock_jvlink.jv_init.return_value = 0
        mock_jvlink.jv_rt_open.return_value = 0
        mock_jvlink.jv_read.return_value = (0, "", "")  # Complete immediately
        mock_jvlink_class.return_value = mock_jvlink

        monitor = RealtimeMonitor(
            database=self.mock_db,
            data_spec="RACE",
            polling_interval=1
        )

        # Start monitor in daemon mode
        monitor.start(daemon=True)
        self.assertTrue(monitor._running)

        # Stop monitor
        monitor.stop()
        self.assertFalse(monitor._running)
        mock_jvlink.jv_close.assert_called_once()

    @patch('src.realtime.monitor.JVLinkWrapper')
    @patch('src.realtime.monitor.RealtimeUpdater')
    def test_get_status(self, mock_updater_class, mock_jvlink_class):
        """Test get_status method."""
        monitor = RealtimeMonitor(
            database=self.mock_db,
            data_spec="RACE"
        )

        status = monitor.get_status()

        self.assertFalse(status["running"])
        self.assertEqual(status["data_spec"], "RACE")
        self.assertEqual(status["records_processed"], 0)

    @patch('src.realtime.monitor.JVLinkWrapper')
    @patch('src.realtime.monitor.RealtimeUpdater')
    def test_context_manager(self, mock_updater_class, mock_jvlink_class):
        """Test context manager protocol."""
        mock_jvlink = MagicMock()
        mock_jvlink_class.return_value = mock_jvlink

        with RealtimeMonitor(database=self.mock_db) as monitor:
            self.assertIsNotNone(monitor)

        # Monitor should be stopped after exiting context
        # (if it was started)


if __name__ == "__main__":
    unittest.main()
