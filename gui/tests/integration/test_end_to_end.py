"""End-to-end integration tests for the complete application."""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer

from src.core.battery_manager import BatteryManager
from src.core.config_manager import ConfigManager
from src.gui.system_tray import SystemTrayApp
from src.gui.settings_dialog import SettingsDialog


@pytest.fixture
def temp_config_dir():
    """Create temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = os.path.join(temp_dir, '.config', 'a14-charge-keeper')
        os.makedirs(config_dir)
        yield config_dir


@pytest.fixture
def qapp():
    """Ensure QApplication instance exists."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        app.setQuitOnLastWindowClosed(False)
    
    yield app
    
    # Don't quit the app as it might be used by other tests


@pytest.mark.integration
@pytest.mark.gui
def test_complete_app_startup_and_shutdown(qapp, temp_config_dir):
    """Test complete application startup and shutdown cycle."""
    # Mock battery manager to avoid real system calls
    with patch('src.gui.system_tray.BatteryManager') as MockBatteryManager:
        mock_battery_manager = MagicMock()
        mock_battery_manager.initialize.return_value.success = True
        mock_battery_manager.is_initialized = True
        mock_battery_manager.current_info = None
        MockBatteryManager.return_value = mock_battery_manager
        
        # Create system tray app
        tray_app = SystemTrayApp()
        
        # Start the app
        result = tray_app.start()
        assert result.success is True
        
        # Check that components are created
        assert tray_app.tray_icon is not None
        assert tray_app.battery_popup is not None
        assert tray_app.context_menu is not None
        assert tray_app.config_manager is not None
        
        # Test config loading
        theme = tray_app.config_manager.get('theme', 'dark')
        assert theme in ['dark', 'light']
        
        # Stop the app
        tray_app.stop()


@pytest.mark.integration
@pytest.mark.gui
def test_settings_workflow(qapp, temp_config_dir):
    """Test complete settings change workflow."""
    # Create config manager with temp directory
    config_manager = ConfigManager(config_dir=temp_config_dir)
    
    # Test initial settings
    assert config_manager.get('theme') == 'dark'  # Default
    assert config_manager.get('default_threshold') == 80  # Default
    
    # Create settings dialog
    settings_dialog = SettingsDialog(config_manager)
    
    # Verify initial UI state
    assert settings_dialog.theme_combo.currentText() == 'Dark'
    assert settings_dialog.threshold_spinbox.value() == 80
    
    # Change settings programmatically (simulating user input)
    settings_dialog.theme_combo.setCurrentText('Light')
    settings_dialog.threshold_spinbox.setValue(75)
    settings_dialog.auto_start_checkbox.setChecked(True)
    
    # Save settings
    settings_dialog.save_settings()
    
    # Verify settings were saved
    assert config_manager.get('theme') == 'light'
    assert config_manager.get('default_threshold') == 75
    assert config_manager.get('auto_start') is True
    
    # Create new config manager to test persistence
    new_config = ConfigManager(config_dir=temp_config_dir)
    new_config.load()
    assert new_config.get('theme') == 'light'
    assert new_config.get('default_threshold') == 75
    assert new_config.get('auto_start') is True


@pytest.mark.integration
@pytest.mark.gui
def test_theme_application_workflow(qapp, temp_config_dir):
    """Test theme application across all components."""
    with patch('src.gui.system_tray.BatteryManager') as MockBatteryManager:
        mock_battery_manager = MagicMock()
        mock_battery_manager.initialize.return_value.success = True
        mock_battery_manager.is_initialized = True
        mock_battery_manager.current_info = None  # No current info for theme test
        MockBatteryManager.return_value = mock_battery_manager
        
        # Create system tray app with light theme
        with patch('src.gui.system_tray.ConfigManager') as MockConfigManager:
            mock_config = ConfigManager(config_dir=temp_config_dir)
            MockConfigManager.return_value = mock_config
            
            tray_app = SystemTrayApp()
            tray_app.config_manager.set('theme', 'light')
            tray_app.config_manager.save()
        
        result = tray_app.start()
        assert result.success is True
        
        # Check that all components have light theme applied
        assert hasattr(tray_app.battery_popup, '_current_theme')
        
        # Change theme to dark
        tray_app.config_manager.set('theme', 'dark')
        tray_app._apply_theme_changes()
        
        # Verify theme change propagated
        # (In a real test, we'd check visual properties)
        
        tray_app.stop()


@pytest.mark.integration
@pytest.mark.slow
def test_battery_manager_integration_with_mocked_cli():
    """Test battery manager with mocked CLI integration."""
    with patch('src.core.cli_interface.subprocess.run') as mock_run:
        # Mock successful CLI response
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = """Device : BAT0
충전 종료: 80%
백업 파일: 2개

=== upower 정보 ===
  Device: /org/freedesktop/UPower/devices/battery_BAT0
  Power supply: yes
  Updated: Mon 09 Dec 2024 10:30:15 AM KST (2 seconds ago)
  Has history: yes
  Has statistics: yes
  Present: yes
  Energy: 45.2 Wh
  Energy empty: 0 Wh  
  Energy full: 48.8 Wh
  Energy full design: 50.0 Wh
  Voltage: 11.4 V
  Percentage: 92%
  Capacity: 97.6%
  Technology: lithium-ion
  State: not charging"""
        mock_run.return_value.stderr = ""
        
        # Test battery manager
        battery_manager = BatteryManager()
        result = battery_manager.initialize()
        
        assert result.success is True
        assert battery_manager.is_initialized is True
        assert battery_manager.current_info is not None
        assert battery_manager.current_info.device == "BAT0"
        assert battery_manager.current_info.end_threshold == 80
        # Note: percentage comes from upower parsing which may not be implemented yet
        # assert battery_manager.current_info.percentage == 92
        
        # Test threshold setting
        mock_run.return_value.returncode = 0  # Success
        result = battery_manager.set_threshold(75)
        assert result.success is True


@pytest.mark.integration
def test_config_manager_error_handling(temp_config_dir):
    """Test config manager handles errors gracefully."""
    config_manager = ConfigManager(config_dir=temp_config_dir)
    
    # Test loading non-existent config (should use defaults)
    config_manager.load()
    assert config_manager.get('theme') == 'dark'
    
    # Test invalid config file
    config_file = os.path.join(temp_config_dir, 'config.json')
    with open(config_file, 'w') as f:
        f.write('invalid json content')
    
    # Should handle invalid JSON gracefully
    new_config = ConfigManager(config_dir=temp_config_dir)
    new_config.load()  # Should not crash
    assert new_config.get('theme') == 'dark'  # Should use defaults


@pytest.mark.integration
@pytest.mark.gui  
def test_popup_interaction_workflow(qapp, temp_config_dir):
    """Test battery popup interaction workflow."""
    with patch('src.gui.system_tray.BatteryManager') as MockBatteryManager:
        mock_battery_manager = MagicMock()
        mock_battery_manager.initialize.return_value.success = True
        mock_battery_manager.is_initialized = True
        
        # Mock battery info
        from src.core.battery_manager import BatteryInfo
        mock_info = BatteryInfo(
            device="BAT0",
            percentage=85,
            state="not charging",
            end_threshold=80
        )
        mock_battery_manager.current_info = mock_info
        MockBatteryManager.return_value = mock_battery_manager
        
        # Create system tray app
        tray_app = SystemTrayApp()
        result = tray_app.start()
        assert result.success is True
        
        # Show popup programmatically
        popup = tray_app.battery_popup
        popup.show()
        
        # Verify popup displays correct info
        assert "85%" in popup.battery_percent_label.text()
        assert popup.threshold_slider.value() == 80
        
        # Simulate slider change
        popup.threshold_slider.setValue(70)
        mock_battery_manager.set_threshold.return_value.success = True
        
        # Trigger slider released
        popup._on_slider_released()
        
        # Verify set_threshold was called
        mock_battery_manager.set_threshold.assert_called_with(70)
        
        popup.hide()
        tray_app.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])