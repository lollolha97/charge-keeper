"""pytest configuration and fixtures for GUI testing."""

import pytest
import sys
from unittest.mock import Mock, MagicMock
from PyQt5.QtWidgets import QApplication


# Ensure QApplication instance exists for GUI tests
@pytest.fixture(scope='session')
def qapp():
    """Create QApplication instance for GUI testing."""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app




@pytest.fixture
def mock_subprocess(mocker):
    """Mock subprocess.run for CLI interface testing."""
    return mocker.patch('subprocess.run')


@pytest.fixture
def mock_completed_process():
    """Factory for creating mock CompletedProcess objects."""
    def _create_mock(stdout="", stderr="", returncode=0):
        mock = Mock()
        mock.stdout = stdout
        mock.stderr = stderr
        mock.returncode = returncode
        return mock
    return _create_mock


@pytest.fixture
def sample_battery_status():
    """Sample battery status output from CLI."""
    return """Device : BAT0
충전 종료: 80%
백업 파일: 3개

  Device: /org/freedesktop/UPower/devices/battery_BAT0
    native-path:          BAT0
    percentage:           75%
    state:                charging"""


@pytest.fixture
def sample_thinkpad_status():
    """Sample ThinkPad battery status with start threshold."""
    return """Device : BAT0
충전 종료: 80%
충전 시작: 60% (ThinkPad/Lenovo 등 지원)
백업 파일: 2개"""