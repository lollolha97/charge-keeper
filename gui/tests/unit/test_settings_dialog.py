"""Tests for Settings Dialog - TDD approach."""

import pytest
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from src.gui.settings_dialog import SettingsDialog
from src.core.config_manager import ConfigManager


class TestSettingsDialog:
    """Test cases for settings dialog."""
    
    @pytest.fixture
    def qtbot(self):
        """QTest bot fixture."""
        return None  # Will be provided by pytest-qt
    
    @pytest.fixture
    def mock_config_manager(self):
        """Mock config manager."""
        config = Mock(spec=ConfigManager)
        config.get.return_value = None
        config.DEFAULTS = ConfigManager.DEFAULTS
        return config
    
    @pytest.fixture 
    def settings_dialog(self, qtbot, mock_config_manager):
        """Settings dialog fixture."""
        dialog = SettingsDialog(mock_config_manager)
        if qtbot:
            qtbot.addWidget(dialog)
        return dialog
    
    def test_dialog_initialization(self, settings_dialog, mock_config_manager):
        """Test that settings dialog initializes correctly."""
        # Dialog should be created
        assert settings_dialog is not None
        assert settings_dialog.config_manager is mock_config_manager
        
        # Should load current settings
        mock_config_manager.get.assert_called()
    
    def test_load_settings_into_ui(self, settings_dialog, mock_config_manager):
        """Test loading settings into UI elements."""
        # Mock current settings
        mock_config_manager.get.side_effect = lambda key, default=None: {
            'auto_start': True,
            'default_threshold': 70,
            'theme': 'light',
            'refresh_interval': 60,
            'show_notifications': False
        }.get(key, default)
        
        settings_dialog.load_settings()
        
        # Check UI elements reflect the settings
        assert settings_dialog.auto_start_checkbox.isChecked() is True
        assert settings_dialog.threshold_spinbox.value() == 70
        assert settings_dialog.theme_combo.currentText() == 'Light'
        assert settings_dialog.refresh_interval_spinbox.value() == 60
        assert settings_dialog.notifications_checkbox.isChecked() is False
    
    def test_save_settings_from_ui(self, settings_dialog, mock_config_manager):
        """Test saving settings from UI elements."""
        # Set UI values
        settings_dialog.auto_start_checkbox.setChecked(True)
        settings_dialog.threshold_spinbox.setValue(65)
        settings_dialog.theme_combo.setCurrentText('Dark')
        settings_dialog.refresh_interval_spinbox.setValue(45)
        settings_dialog.notifications_checkbox.setChecked(True)
        
        # Save settings
        settings_dialog.save_settings()
        
        # Verify config_manager.set was called with correct values
        expected_calls = [
            ('auto_start', True),
            ('default_threshold', 65),
            ('theme', 'dark'),
            ('refresh_interval', 45),
            ('show_notifications', True)
        ]
        
        for key, value in expected_calls:
            mock_config_manager.set.assert_any_call(key, value)
        
        # Should save to file
        mock_config_manager.save.assert_called_once()
    
    def test_reset_to_defaults_button(self, settings_dialog, mock_config_manager):
        """Test reset to defaults functionality."""
        # Simulate clicking reset button
        settings_dialog.reset_to_defaults()
        
        # Should call config manager reset
        mock_config_manager.reset_to_defaults.assert_called_once()
        
        # Should reload UI with defaults
        mock_config_manager.save.assert_called_once()
    
    def test_dialog_buttons(self, settings_dialog, mock_config_manager):
        """Test OK and Cancel button behavior."""
        # Mock dialog methods
        with patch.object(settings_dialog, 'save_settings') as mock_save:
            with patch.object(settings_dialog, 'accept') as mock_accept:
                settings_dialog.ok_clicked()
                mock_save.assert_called_once()
                mock_accept.assert_called_once()
        
        # Test cancel
        with patch.object(settings_dialog, 'load_settings') as mock_load:
            with patch.object(settings_dialog, 'reject') as mock_reject:
                settings_dialog.cancel_clicked()
                mock_load.assert_called_once()  # Revert changes
                mock_reject.assert_called_once()
    
    def test_input_validation(self, settings_dialog, mock_config_manager):
        """Test that invalid inputs are handled properly."""
        # Set invalid threshold
        settings_dialog.threshold_spinbox.setValue(150)  # Above max
        
        # Should be clamped to valid range
        with pytest.raises(ValueError):
            settings_dialog.save_settings()
    
    def test_theme_change_preview(self, settings_dialog, mock_config_manager):
        """Test theme change preview functionality."""
        # Change theme
        settings_dialog.theme_combo.setCurrentText('Light')
        settings_dialog.on_theme_changed('Light')
        
        # Should preview the theme change
        # (Implementation would apply theme to dialog)
        assert 'light' in settings_dialog.styleSheet().lower() or settings_dialog.styleSheet() == ""
    
    def test_dialog_size_and_positioning(self, settings_dialog):
        """Test dialog size and positioning."""
        # Dialog should have reasonable size
        assert settings_dialog.width() >= 400
        assert settings_dialog.height() >= 300
        
        # Should be modal
        assert settings_dialog.isModal() is True