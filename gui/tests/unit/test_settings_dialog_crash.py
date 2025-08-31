"""Test for settings dialog segmentation fault - TDD approach."""

import pytest
import tempfile
import sys
from unittest.mock import MagicMock, patch

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from src.core.config_manager import ConfigManager
from src.gui.settings_dialog import SettingsDialog


class TestSettingsDialogCrash:
    """Test cases to reproduce and fix settings dialog crash."""
    
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
    
    @pytest.fixture
    def settings_dialog(self, app, config_manager):
        """Create settings dialog."""
        return SettingsDialog(config_manager)
    
    def test_settings_dialog_ok_button_click_should_not_crash(self, settings_dialog):
        """Test that clicking OK button doesn't cause segmentation fault."""
        # This test should initially fail due to the crash
        
        # Mock the signal connection to detect if signal is emitted properly
        signal_emitted = False
        
        def on_settings_changed():
            nonlocal signal_emitted
            signal_emitted = True
        
        settings_dialog.settings_changed.connect(on_settings_changed)
        
        # Change a setting
        settings_dialog.auto_start_checkbox.setChecked(True)
        settings_dialog.threshold_spinbox.setValue(75)
        
        # This should not crash - but currently does
        try:
            # Simulate OK button click
            settings_dialog.ok_clicked()
            
            # If we reach here, the dialog didn't crash
            assert True, "Settings dialog should not crash on OK click"
            assert signal_emitted, "settings_changed signal should be emitted"
            
        except Exception as e:
            pytest.fail(f"Settings dialog crashed with: {e}")
    
    def test_settings_save_without_signal_emission_crash(self, settings_dialog):
        """Test that settings can be saved without signal emission causing crash."""
        # Change settings
        settings_dialog.auto_start_checkbox.setChecked(True)
        settings_dialog.threshold_spinbox.setValue(70)
        
        # Save settings directly without UI interaction
        try:
            settings_dialog.save_settings()
            # Should not crash
            assert True
        except Exception as e:
            pytest.fail(f"save_settings crashed with: {e}")
    
    def test_settings_dialog_accept_without_crash(self, settings_dialog):
        """Test that dialog.accept() doesn't cause threading issues."""
        # This should not cause segmentation fault
        try:
            settings_dialog.accept()
            assert True
        except Exception as e:
            pytest.fail(f"dialog.accept() crashed with: {e}")
    
    def test_settings_dialog_with_system_tray_integration(self, app, config_manager):
        """Test settings dialog crash in context of system tray integration."""
        from src.core.battery_manager import BatteryManager
        from src.gui.system_tray import SystemTrayApp
        
        # Create system tray app (but don't start it to avoid UI)
        battery_manager = BatteryManager()
        tray_app = SystemTrayApp(battery_manager)
        
        # Create settings dialog connected to system tray
        settings_dialog = SettingsDialog(config_manager)
        settings_dialog.settings_changed.connect(tray_app._on_settings_changed)
        
        # This should reproduce the actual crash scenario
        try:
            # Change settings
            settings_dialog.auto_start_checkbox.setChecked(True)
            
            # Simulate OK click which triggers signal chain
            settings_dialog.ok_clicked()
            
            # Should not crash
            assert True, "Settings dialog with system tray integration should not crash"
            
        except Exception as e:
            pytest.fail(f"Settings dialog with system tray integration crashed: {e}")
    
    def test_settings_dialog_safe_signal_emission(self, app, config_manager):
        """Test that signal emission happens after dialog closure to prevent crashes."""
        from src.core.battery_manager import BatteryManager
        from src.gui.system_tray import SystemTrayApp
        
        # Create system tray app
        battery_manager = BatteryManager()
        tray_app = SystemTrayApp(battery_manager)
        
        # Create settings dialog
        settings_dialog = SettingsDialog(config_manager)
        
        # Track signal emission
        signal_emitted = False
        def on_settings_changed():
            nonlocal signal_emitted
            signal_emitted = True
        
        settings_dialog.settings_changed.connect(on_settings_changed)
        settings_dialog.settings_changed.connect(tray_app._on_settings_changed)
        
        # Test the new safe approach
        try:
            # Change settings
            settings_dialog.auto_start_checkbox.setChecked(True)
            settings_dialog.threshold_spinbox.setValue(75)
            
            # Test _save_settings_without_signal
            settings_dialog._save_settings_without_signal()
            
            # Signal should not be emitted yet
            assert not signal_emitted, "Signal should not be emitted during save_without_signal"
            
            # Manually emit signal (simulating ok_clicked behavior)
            settings_dialog.settings_changed.emit()
            
            # Now signal should be emitted
            assert signal_emitted, "Signal should be emitted after manual emit"
            
            # Verify settings were saved
            assert config_manager.get('auto_start') == True
            assert config_manager.get('default_threshold') == 75
            
        except Exception as e:
            pytest.fail(f"Safe signal emission test failed: {e}")