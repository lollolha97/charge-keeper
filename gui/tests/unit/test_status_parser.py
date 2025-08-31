"""Tests for CLI output status parser."""

import pytest
from src.core.status_parser import StatusParser, BatteryStatus


class TestStatusParser:
    """Test CLI output parsing functionality."""

    def test_parse_basic_battery_status(self, sample_battery_status):
        """Test parsing basic ASUS battery status output."""
        result = StatusParser.parse_status(sample_battery_status)
        
        assert result.device == "BAT0"
        assert result.end_threshold == 80
        assert result.backup_count == 3
        assert result.start_threshold is None

    def test_parse_thinkpad_with_start_threshold(self, sample_thinkpad_status):
        """Test parsing ThinkPad status with start threshold."""
        result = StatusParser.parse_status(sample_thinkpad_status)
        
        assert result.device == "BAT0"
        assert result.end_threshold == 80
        assert result.start_threshold == 60
        assert result.backup_count == 2

    def test_parse_empty_output(self):
        """Test parsing empty output raises appropriate error."""
        with pytest.raises(ValueError, match="Empty or invalid status output"):
            StatusParser.parse_status("")

    def test_parse_invalid_format(self):
        """Test parsing malformed output raises appropriate error."""
        invalid_output = "Some random text without proper format"
        
        with pytest.raises(ValueError, match="Unable to parse device information"):
            StatusParser.parse_status(invalid_output)

    def test_parse_missing_threshold(self):
        """Test parsing output without threshold information."""
        incomplete_output = "Device : BAT0"
        
        with pytest.raises(ValueError, match="Unable to parse threshold information"):
            StatusParser.parse_status(incomplete_output)


class TestBatteryStatus:
    """Test BatteryStatus data class."""

    def test_battery_status_creation(self):
        """Test creating BatteryStatus instance."""
        status = BatteryStatus(
            device="BAT0",
            end_threshold=80,
            start_threshold=60,
            backup_count=3
        )
        
        assert status.device == "BAT0"
        assert status.end_threshold == 80
        assert status.start_threshold == 60
        assert status.backup_count == 3

    def test_battery_status_defaults(self):
        """Test BatteryStatus with default values."""
        status = BatteryStatus(device="BAT0", end_threshold=80)
        
        assert status.device == "BAT0"
        assert status.end_threshold == 80
        assert status.start_threshold is None
        assert status.backup_count == 0

    def test_battery_status_string_representation(self):
        """Test string representation of BatteryStatus."""
        status = BatteryStatus(device="BAT0", end_threshold=80)
        
        str_repr = str(status)
        assert "BAT0" in str_repr
        assert "80" in str_repr