"""Tests for battery manager business logic."""

import pytest
from unittest.mock import Mock, MagicMock
from src.core.battery_manager import BatteryManager, BatteryInfo, BatteryEvent
from src.core.status_parser import BatteryStatus
from src.core.cli_interface import CliResult
from tests.fixtures.cli_outputs import (
    FULL_STATUS_OUTPUT, 
    CHARGING_STATUS_OUTPUT, 
    THINKPAD_STATUS_OUTPUT,
    MINIMAL_STATUS_OUTPUT
)


class TestBatteryManager:
    """Test battery manager business logic."""

    def test_initialization_success(self, mock_cli_interface):
        """Test successful battery manager initialization."""
        mock_cli_interface.get_status.return_value = CliResult.success(
            BatteryStatus(device="BAT0", end_threshold=80)
        )
        
        manager = BatteryManager(cli_interface=mock_cli_interface)
        result = manager.initialize()
        
        assert result.success is True
        assert manager.is_initialized is True
        assert manager.current_info.device == "BAT0"
        assert manager.current_info.end_threshold == 80

    def test_initialization_failure(self, mock_cli_interface):
        """Test battery manager initialization failure."""
        mock_cli_interface.get_status.return_value = CliResult.error("CLI not found")
        
        manager = BatteryManager(cli_interface=mock_cli_interface)
        result = manager.initialize()
        
        assert result.success is False
        assert manager.is_initialized is False
        assert "CLI not found" in result.error_message

    def test_refresh_status_success(self, mock_cli_interface):
        """Test successful status refresh."""
        # Setup initial state
        initial_status = BatteryStatus(device="BAT0", end_threshold=70)
        mock_cli_interface.get_status.return_value = CliResult.success(initial_status)
        
        manager = BatteryManager(cli_interface=mock_cli_interface)
        manager.initialize()
        
        # Change status
        updated_status = BatteryStatus(device="BAT0", end_threshold=80)
        mock_cli_interface.get_status.return_value = CliResult.success(updated_status)
        
        result = manager.refresh_status()
        
        assert result.success is True
        assert manager.current_info.end_threshold == 80

    def test_set_threshold_with_validation(self, mock_cli_interface):
        """Test threshold setting with validation."""
        mock_cli_interface.get_status.return_value = CliResult.success(
            BatteryStatus(device="BAT0", end_threshold=100)
        )
        mock_cli_interface.set_threshold.return_value = CliResult.success()
        
        manager = BatteryManager(cli_interface=mock_cli_interface)
        manager.initialize()
        
        # Valid threshold
        result = manager.set_threshold(80)
        assert result.success is True
        
        # Invalid thresholds
        result = manager.set_threshold(19)
        assert result.success is False
        assert "between 20 and 100" in result.error_message
        
        result = manager.set_threshold(101)
        assert result.success is False

    def test_persist_threshold_success(self, mock_cli_interface):
        """Test persistent threshold setting."""
        mock_cli_interface.get_status.return_value = CliResult.success(
            BatteryStatus(device="BAT0", end_threshold=100)
        )
        mock_cli_interface.persist_threshold.return_value = CliResult.success()
        
        manager = BatteryManager(cli_interface=mock_cli_interface)
        manager.initialize()
        
        result = manager.persist_threshold(70)
        
        assert result.success is True
        mock_cli_interface.persist_threshold.assert_called_once_with(70)

    def test_event_callback_registration(self, mock_cli_interface):
        """Test event callback registration and triggering."""
        mock_cli_interface.get_status.return_value = CliResult.success(
            BatteryStatus(device="BAT0", end_threshold=80)
        )
        
        manager = BatteryManager(cli_interface=mock_cli_interface)
        manager.initialize()
        
        # Register callback
        callback_called = False
        received_event = None
        
        def test_callback(event: BatteryEvent):
            nonlocal callback_called, received_event
            callback_called = True
            received_event = event
        
        manager.register_event_callback(test_callback)
        
        # Trigger status change
        new_status = BatteryStatus(device="BAT0", end_threshold=70)
        mock_cli_interface.get_status.return_value = CliResult.success(new_status)
        
        manager.refresh_status()
        
        assert callback_called is True
        assert received_event.event_type == "threshold_changed"
        assert received_event.data["old_threshold"] == 80
        assert received_event.data["new_threshold"] == 70

    def test_auto_refresh_control(self, mock_cli_interface):
        """Test auto-refresh functionality control."""
        mock_cli_interface.get_status.return_value = CliResult.success(
            BatteryStatus(device="BAT0", end_threshold=80)
        )
        
        manager = BatteryManager(cli_interface=mock_cli_interface)
        manager.initialize()
        
        # Test auto-refresh control
        assert manager.auto_refresh_enabled is False  # Default off
        
        manager.enable_auto_refresh(interval_seconds=5)
        assert manager.auto_refresh_enabled is True
        
        manager.disable_auto_refresh()
        assert manager.auto_refresh_enabled is False


class TestBatteryInfo:
    """Test extended battery information parsing."""

    def test_parse_full_battery_info(self):
        """Test parsing comprehensive battery information."""
        info = BatteryInfo.from_cli_output(FULL_STATUS_OUTPUT)
        
        # Basic info
        assert info.device == "BAT0"
        assert info.end_threshold == 70
        assert info.backup_count == 2
        
        # Hardware info
        assert info.vendor == "AS3GYRE3KC"
        assert info.model == "GA40347"
        assert info.serial == "06D2"
        
        # Power info
        assert info.state == "discharging"
        assert info.percentage == 66
        assert info.energy_current == 45.088
        assert info.energy_full == 68.314
        assert info.energy_full_design == 73
        assert info.energy_rate == 15.126
        assert info.voltage == 15.858
        assert info.capacity == 93.5808
        assert info.time_to_empty == "3.0 hours"
        assert info.time_to_full is None

    def test_parse_charging_battery_info(self):
        """Test parsing charging battery information."""
        info = BatteryInfo.from_cli_output(CHARGING_STATUS_OUTPUT)
        
        assert info.state == "charging"
        assert info.percentage == 81
        assert info.time_to_full == "17.5 minutes"
        assert info.time_to_empty is None

    def test_parse_thinkpad_battery_info(self):
        """Test parsing ThinkPad battery with start threshold."""
        info = BatteryInfo.from_cli_output(THINKPAD_STATUS_OUTPUT)
        
        assert info.end_threshold == 80
        assert info.start_threshold == 75
        assert info.state == "not charging"
        assert info.charge_cycles == 125
        assert info.energy_rate == 0  # Not charging

    def test_parse_minimal_battery_info(self):
        """Test parsing minimal battery information."""
        info = BatteryInfo.from_cli_output(MINIMAL_STATUS_OUTPUT)
        
        assert info.device == "BAT1"
        assert info.end_threshold == 100
        assert info.vendor is None
        assert info.percentage is None

    def test_battery_info_health_calculation(self):
        """Test battery health calculation."""
        info = BatteryInfo.from_cli_output(FULL_STATUS_OUTPUT)
        
        # Health = (energy_full / energy_full_design) * 100
        expected_health = (68.314 / 73) * 100
        assert abs(info.health_percentage - expected_health) < 0.01

    def test_battery_info_string_representation(self):
        """Test string representation of battery info."""
        info = BatteryInfo.from_cli_output(FULL_STATUS_OUTPUT)
        
        str_repr = str(info)
        assert "BAT0" in str_repr
        assert "70%" in str_repr
        assert "discharging" in str_repr


class TestBatteryEvent:
    """Test battery event system."""

    def test_event_creation(self):
        """Test battery event creation."""
        event = BatteryEvent(
            event_type="threshold_changed",
            data={"old": 80, "new": 70},
            timestamp=1234567890
        )
        
        assert event.event_type == "threshold_changed"
        assert event.data["old"] == 80
        assert event.data["new"] == 70
        assert event.timestamp == 1234567890

    def test_event_string_representation(self):
        """Test event string representation."""
        event = BatteryEvent("status_changed", {"state": "charging"})
        
        str_repr = str(event)
        assert "status_changed" in str_repr
        assert "charging" in str_repr


@pytest.fixture
def mock_cli_interface():
    """Mock CLI interface for testing."""
    return Mock()