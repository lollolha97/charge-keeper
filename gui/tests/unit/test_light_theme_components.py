"""Test light theme application across all GUI components."""

import pytest
import sys
import tempfile
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication

from src.core.config_manager import ConfigManager
from src.core.battery_manager import BatteryManager
from src.gui.battery_popup import BatteryPopup
from src.gui.battery_detail_dialog import BatteryDetailDialog
from src.gui.settings_dialog import SettingsDialog
from src.gui.system_tray import SystemTrayApp


class TestLightThemeComponents:
    """Test cases for light theme application across all components."""
    
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
    def config_manager_light(self, temp_config_dir):
        """Create config manager with light theme."""
        config = ConfigManager(config_dir=temp_config_dir)
        config.set('theme', 'light')
        config.set('default_threshold', 80)
        config.save()
        return config
    
    def test_battery_popup_light_theme(self, app):
        """Test that battery popup applies light theme correctly."""
        battery_manager = BatteryManager()
        popup = BatteryPopup(battery_manager)
        
        # Apply light theme
        popup.apply_theme('light')
        
        # Check that theme was stored
        assert hasattr(popup, '_current_theme')
        assert popup._current_theme == 'light'
        
        # Check that stylesheet contains light theme colors
        stylesheet = popup.styleSheet()
        assert '#ffffff' in stylesheet  # White background
        assert '#000000' in stylesheet  # Black text
    
    def test_battery_detail_dialog_light_theme(self, app):
        """Test that battery detail dialog applies light theme correctly."""
        battery_manager = BatteryManager()
        dialog = BatteryDetailDialog(battery_manager)
        
        # Apply light theme
        dialog.apply_theme('light')
        
        # Check that stylesheet contains light theme colors
        stylesheet = dialog.styleSheet()
        assert '#ffffff' in stylesheet  # White background
        assert '#000000' in stylesheet  # Black text
        assert '#f8f8f8' in stylesheet  # Light frame background
    
    def test_settings_dialog_light_theme(self, app, config_manager_light):
        """Test that settings dialog applies light theme correctly."""
        dialog = SettingsDialog(config_manager_light)
        
        # Simulate theme change to light
        dialog.theme_combo.setCurrentText('Light')
        dialog.on_theme_changed('Light')
        
        # Check that stylesheet contains light theme colors
        stylesheet = dialog.styleSheet()
        assert '#ffffff' in stylesheet  # White background
        assert '#000000' in stylesheet  # Black text
    
    def test_system_tray_applies_theme_to_all_components(self, app, config_manager_light):
        """Test that system tray applies theme to all its components."""
        battery_manager = BatteryManager()
        tray_app = SystemTrayApp(battery_manager)
        tray_app.config_manager = config_manager_light
        
        # Apply theme changes
        tray_app._apply_theme_changes()
        
        # Check battery popup theme
        assert hasattr(tray_app.battery_popup, '_current_theme')
        assert tray_app.battery_popup._current_theme == 'light'
        
        # Create detail dialog and check it gets theme applied
        tray_app._show_status()
        assert tray_app.detail_dialog is not None
        
        # Check detail dialog stylesheet
        stylesheet = tray_app.detail_dialog.styleSheet()
        assert '#ffffff' in stylesheet  # Should have light theme applied
    
    def test_battery_popup_progress_bar_theme_aware(self, app):
        """Test that battery popup progress bar adapts to theme."""
        from src.core.battery_manager import BatteryInfo
        
        battery_manager = BatteryManager()
        popup = BatteryPopup(battery_manager)
        
        # Test with light theme
        popup.apply_theme('light')
        
        # Create mock battery info
        battery_info = BatteryInfo(
            device="BAT0",
            end_threshold=80,
            percentage=75,
            state="charging"
        )
        
        # Update battery info (should update progress bar colors)
        popup.update_battery_info(battery_info)
        
        # Check that progress bar background is light
        progress_stylesheet = popup.battery_progress.styleSheet()
        assert '#f0f0f0' in progress_stylesheet  # Light background
    
    def test_theme_persistence_on_startup(self, app, config_manager_light):
        """Test that saved light theme is applied on system tray startup."""
        battery_manager = BatteryManager()
        tray_app = SystemTrayApp(battery_manager)
        tray_app.config_manager = config_manager_light
        
        # Simulate startup theme application
        tray_app._apply_theme_changes()
        
        # Battery popup should have light theme
        assert tray_app.battery_popup._current_theme == 'light'
        
        # Check popup stylesheet
        stylesheet = tray_app.battery_popup.styleSheet()
        assert '#ffffff' in stylesheet
        assert '#000000' in stylesheet
    
    def test_all_components_have_apply_theme_method(self, app):
        """Test that all theme-aware components implement apply_theme method."""
        battery_manager = BatteryManager()
        
        # Test battery popup
        popup = BatteryPopup(battery_manager)
        assert hasattr(popup, 'apply_theme')
        assert callable(popup.apply_theme)
        
        # Test battery detail dialog
        dialog = BatteryDetailDialog(battery_manager)
        assert hasattr(dialog, 'apply_theme')
        assert callable(dialog.apply_theme)
        
        # Settings dialog doesn't need apply_theme as it handles theme internally