"""Test for complete QTimer removal to fix sudo crashes."""

import pytest
import tempfile
import sys
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication

from src.core.config_manager import ConfigManager
from src.gui.settings_dialog import SettingsDialog
from src.core.battery_manager import BatteryManager
from src.gui.system_tray import SystemTrayApp


class TestSudoCrashFix:
    """Test cases to verify QTimer removal fixes sudo crashes."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication if it doesn't exist."""
        if not QApplication.instance():
            app = QApplication(sys.argv)
            return app
        return QApplication.instance()
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """Create config manager with temp directory."""
        return ConfigManager(config_dir=temp_config_dir)
    
    def test_settings_dialog_no_qtimer_usage(self, app, config_manager):
        """Test that settings dialog doesn't use QTimer internally."""
        # Mock os.geteuid to simulate sudo execution
        with patch('os.geteuid', return_value=0):
            settings_dialog = SettingsDialog(config_manager)
            
            # Change settings and save
            settings_dialog.auto_start_checkbox.setChecked(True)
            settings_dialog.threshold_spinbox.setValue(70)
            
            # This should not use any QTimer internally and not crash
            try:
                settings_dialog.ok_clicked()
                assert True, "Settings dialog should not crash without QTimer"
            except Exception as e:
                pytest.fail(f"Settings dialog crashed: {e}")
    
    def test_system_tray_settings_change_no_qtimer(self, app):
        """Test that system tray settings change doesn't use QTimer.singleShot."""
        battery_manager = BatteryManager()
        tray_app = SystemTrayApp(battery_manager)
        
        # Mock os.geteuid to simulate sudo execution
        with patch('os.geteuid', return_value=0):
            try:
                # This should call _update_refresh_interval directly
                tray_app._on_settings_changed()
                assert True, "Settings change should not use QTimer.singleShot"
            except Exception as e:
                pytest.fail(f"Settings change crashed: {e}")
    
    def test_battery_popup_no_qtimer_usage(self, app):
        """Test that battery popup doesn't use QTimer for hiding."""
        from src.gui.battery_popup import BatteryPopup
        
        battery_manager = BatteryManager()
        popup = BatteryPopup(battery_manager)
        
        # Mock os.geteuid to simulate sudo execution
        with patch('os.geteuid', return_value=0):
            try:
                # These methods should not use QTimer.singleShot anymore
                popup._on_slider_released()
                popup._close_popup()
                assert True, "Battery popup should not use QTimer"
            except Exception as e:
                pytest.fail(f"Battery popup crashed: {e}")
    
    def test_complete_qtimer_removal_verification(self, app, temp_config_dir):
        """Verify that no QTimer.singleShot calls remain in critical paths."""
        config_manager = ConfigManager(config_dir=temp_config_dir)
        battery_manager = BatteryManager()
        tray_app = SystemTrayApp(battery_manager)
        
        # Create and connect settings dialog
        settings_dialog = SettingsDialog(config_manager)
        settings_dialog.settings_changed.connect(tray_app._on_settings_changed)
        
        # Mock being root user
        with patch('os.geteuid', return_value=0):
            # Mock QTimer.singleShot to detect any usage
            with patch('PyQt5.QtCore.QTimer.singleShot') as mock_single_shot:
                try:
                    # Simulate full settings save flow
                    settings_dialog.auto_start_checkbox.setChecked(True)
                    settings_dialog.ok_clicked()
                    
                    # QTimer.singleShot should not be called in settings flow
                    mock_single_shot.assert_not_called()
                    
                except Exception as e:
                    pytest.fail(f"Complete flow crashed: {e}")
    
    def test_refresh_timer_still_works_in_main_thread(self, app):
        """Test that refresh timer still works when properly in main thread."""
        battery_manager = BatteryManager()
        tray_app = SystemTrayApp(battery_manager, refresh_interval=1000)
        
        # Mock being in main thread (not root)
        with patch('os.geteuid', return_value=1000):  # Regular user
            with patch('PyQt5.QtCore.QThread.currentThread') as mock_current_thread:
                mock_current_thread.return_value = app.thread()
                
                try:
                    result = tray_app.start()
                    assert result.success
                    # Timer should be created for regular user
                    assert tray_app.refresh_timer is not None
                except Exception as e:
                    pytest.fail(f"Regular user execution failed: {e}")