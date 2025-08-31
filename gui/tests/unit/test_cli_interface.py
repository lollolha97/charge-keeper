"""Tests for CLI interface communication layer."""

import pytest
import subprocess
from unittest.mock import Mock
from src.core.cli_interface import CliInterface, CliResult
from src.core.status_parser import BatteryStatus


class TestCliInterface:
    """Test CLI communication functionality."""

    def test_get_status_success(self, mock_subprocess, mock_completed_process, sample_battery_status):
        """Test successful status retrieval."""
        mock_subprocess.return_value = mock_completed_process(
            stdout=sample_battery_status,
            returncode=0
        )
        
        cli = CliInterface()
        result = cli.get_status()
        
        assert result.success is True
        assert result.data.device == "BAT0"
        assert result.data.end_threshold == 80
        assert result.error_message is None
        
        mock_subprocess.assert_called_once_with(
            ['a14-charge-keeper', 'status'],
            capture_output=True,
            text=True,
            timeout=30
        )

    def test_get_status_cli_not_found(self, mock_subprocess):
        """Test handling when CLI tool is not found."""
        mock_subprocess.side_effect = FileNotFoundError()
        
        cli = CliInterface()
        result = cli.get_status()
        
        assert result.success is False
        assert result.data is None
        assert "a14-charge-keeper not found" in result.error_message

    def test_get_status_cli_error(self, mock_subprocess, mock_completed_process):
        """Test handling CLI command errors."""
        mock_subprocess.return_value = mock_completed_process(
            stdout="",
            stderr="Error: BAT0 not supported",
            returncode=2
        )
        
        cli = CliInterface()
        result = cli.get_status()
        
        assert result.success is False
        assert result.data is None
        assert "Error: BAT0 not supported" in result.error_message

    def test_get_status_timeout(self, mock_subprocess):
        """Test handling command timeout."""
        mock_subprocess.side_effect = subprocess.TimeoutExpired(
            cmd=['a14-charge-keeper', 'status'], 
            timeout=30
        )
        
        cli = CliInterface()
        result = cli.get_status()
        
        assert result.success is False
        assert "Command timed out" in result.error_message

    def test_set_threshold_success(self, mock_subprocess, mock_completed_process):
        """Test successful threshold setting."""
        mock_subprocess.return_value = mock_completed_process(
            stdout="[✅] charge_control_end_threshold = 70 적용 완료",
            returncode=0
        )
        
        cli = CliInterface()
        result = cli.set_threshold(70)
        
        assert result.success is True
        assert result.data is None  # set operations don't return data
        
        mock_subprocess.assert_called_once_with(
            ['sudo', 'a14-charge-keeper', 'set', '70'],
            capture_output=True,
            text=True,
            timeout=30
        )

    def test_set_threshold_invalid_value(self):
        """Test validation of threshold values."""
        cli = CliInterface()
        
        # Test below minimum
        result = cli.set_threshold(19)
        assert result.success is False
        assert "must be between 20 and 100" in result.error_message
        
        # Test above maximum
        result = cli.set_threshold(101)
        assert result.success is False
        assert "must be between 20 and 100" in result.error_message

    def test_set_threshold_sudo_required(self, mock_subprocess, mock_completed_process):
        """Test handling when sudo is required but fails."""
        mock_subprocess.return_value = mock_completed_process(
            stdout="",
            stderr="루트 권한이 필요합니다",
            returncode=1
        )
        
        cli = CliInterface()
        result = cli.set_threshold(80)
        
        assert result.success is False
        assert "루트 권한이 필요합니다" in result.error_message

    def test_persist_threshold_success(self, mock_subprocess, mock_completed_process):
        """Test successful persistent threshold setting."""
        mock_subprocess.return_value = mock_completed_process(
            stdout="[✅] 부팅/절전 후 자동 재적용 구성 완료 (현재 값: 80%)",
            returncode=0
        )
        
        cli = CliInterface()
        result = cli.persist_threshold(80)
        
        assert result.success is True
        
        mock_subprocess.assert_called_once_with(
            ['sudo', 'a14-charge-keeper', 'persist', '80'],
            capture_output=True,
            text=True,
            timeout=30
        )

    def test_clear_threshold_success(self, mock_subprocess, mock_completed_process):
        """Test successful threshold clearing."""
        mock_subprocess.return_value = mock_completed_process(
            stdout="[✅] 임계값을 100%로 복원하고 자동 적용을 해제했습니다.",
            returncode=0
        )
        
        cli = CliInterface()
        result = cli.clear_threshold()
        
        assert result.success is True
        
        mock_subprocess.assert_called_once_with(
            ['sudo', 'a14-charge-keeper', 'clear'],
            capture_output=True,
            text=True,
            timeout=30
        )


class TestCliResult:
    """Test CliResult data structure."""

    def test_success_result_creation(self):
        """Test creating successful result."""
        battery_status = BatteryStatus(device="BAT0", end_threshold=80)
        result = CliResult.success(battery_status)
        
        assert result.success is True
        assert result.data == battery_status
        assert result.error_message is None

    def test_error_result_creation(self):
        """Test creating error result."""
        result = CliResult.error("Command failed")
        
        assert result.success is False
        assert result.data is None
        assert result.error_message == "Command failed"

    def test_result_string_representation(self):
        """Test string representation of results."""
        success_result = CliResult.success(None)
        error_result = CliResult.error("Test error")
        
        assert "SUCCESS" in str(success_result)
        assert "ERROR" in str(error_result)
        assert "Test error" in str(error_result)