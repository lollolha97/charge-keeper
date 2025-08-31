"""Test for QApplication lifecycle management to prevent QBasicTimer issues."""

import pytest
import sys
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication

# Import main modules
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from main import main, setup_qt_for_root
from gui.system_tray import main as tray_main


class TestQApplicationLifecycle:
    """Test cases for QApplication lifecycle management."""
    
    def test_setup_qt_for_root_environment(self):
        """Test that Qt environment is properly set up for root execution."""
        with patch('os.geteuid', return_value=0):  # Mock running as root
            with patch.dict(os.environ, {'SUDO_USER': 'testuser'}, clear=False):
                with patch('os.makedirs') as mock_makedirs:
                    setup_qt_for_root()
                    
                    # Should set required environment variables
                    assert 'XDG_RUNTIME_DIR' in os.environ
                    assert 'QT_X11_NO_MITSHM' in os.environ
                    assert 'QT_QUICK_BACKEND' in os.environ
                    
                    # Should create runtime directory
                    mock_makedirs.assert_called()
    
    def test_qapplication_global_creation(self):
        """Test that main() creates global QApplication."""
        with patch('os.geteuid', return_value=0):
            with patch('gui.system_tray.main') as mock_tray_main:
                mock_tray_main.return_value = 0
                
                # Mock QApplication creation
                with patch('PyQt5.QtWidgets.QApplication') as mock_app_class:
                    mock_app_instance = MagicMock()
                    mock_app_class.instance.return_value = None
                    mock_app_class.return_value = mock_app_instance
                    
                    # Call main function
                    result = main()
                    
                    # Should create QApplication
                    mock_app_class.assert_called_once()
                    # Should set quit behavior
                    mock_app_instance.setQuitOnLastWindowClosed.assert_called_with(False)
    
    def test_system_tray_uses_existing_qapplication(self):
        """Test that system tray main uses existing QApplication instance."""
        # Create a mock QApplication instance
        mock_app = MagicMock()
        mock_app.exec_.return_value = 0
        
        with patch('PyQt5.QtWidgets.QApplication.instance') as mock_instance:
            with patch('PyQt5.QtWidgets.QSystemTrayIcon.isSystemTrayAvailable') as mock_tray_available:
                with patch('gui.system_tray.SystemTrayApp') as mock_tray_app_class:
                    mock_instance.return_value = mock_app
                    mock_tray_available.return_value = True
                    
                    mock_tray_app = MagicMock()
                    mock_tray_app.start.return_value = MagicMock(success=True)
                    mock_tray_app_class.return_value = mock_tray_app
                    
                    # Call tray_main
                    result = tray_main()
                    
                    # Should use existing QApplication instance
                    mock_instance.assert_called_once()
                    # Should call exec_ on existing instance
                    mock_app.exec_.assert_called_once()
                    assert result == 0
    
    def test_system_tray_error_when_no_qapplication(self):
        """Test that system tray main fails when no QApplication exists."""
        with patch('PyQt5.QtWidgets.QApplication.instance') as mock_instance:
            mock_instance.return_value = None
            
            # Should return error code
            result = tray_main()
            assert result == 1
    
    def test_settings_dialog_with_parent(self):
        """Test that settings dialog is created with proper parent."""
        from gui.system_tray import SystemTrayApp
        from core.battery_manager import BatteryManager
        
        battery_manager = BatteryManager()
        tray_app = SystemTrayApp(battery_manager)
        
        # Mock QApplication with active window
        mock_app = MagicMock()
        mock_active_window = MagicMock()
        mock_app.activeWindow.return_value = mock_active_window
        
        with patch('PyQt5.QtWidgets.QApplication.instance') as mock_instance:
            with patch('gui.settings_dialog.SettingsDialog') as mock_dialog_class:
                mock_instance.return_value = mock_app
                mock_dialog = MagicMock()
                mock_dialog_class.return_value = mock_dialog
                
                # Call _show_settings
                tray_app._show_settings()
                
                # Should create dialog with parent
                mock_dialog_class.assert_called_once()
                # First call should have config_manager and parent
                args, kwargs = mock_dialog_class.call_args
                assert len(args) >= 2  # config_manager and parent
    
    def test_proper_cleanup_on_quit(self):
        """Test that _quit_application performs proper cleanup."""
        from gui.system_tray import SystemTrayApp
        from core.battery_manager import BatteryManager
        
        battery_manager = BatteryManager()
        tray_app = SystemTrayApp(battery_manager)
        
        # Mock dialogs and popup
        mock_popup = MagicMock()
        mock_popup.isVisible.return_value = True
        mock_settings_dialog = MagicMock()
        mock_settings_dialog.isVisible.return_value = True
        mock_detail_dialog = MagicMock()
        mock_detail_dialog.isVisible.return_value = True
        
        tray_app.battery_popup = mock_popup
        tray_app.settings_dialog = mock_settings_dialog
        tray_app.detail_dialog = mock_detail_dialog
        
        # Mock QApplication
        mock_app = MagicMock()
        
        with patch('PyQt5.QtWidgets.QApplication.instance') as mock_instance:
            with patch.object(tray_app, 'stop') as mock_stop:
                mock_instance.return_value = mock_app
                
                # Call quit
                tray_app._quit_application()
                
                # Should close all dialogs
                mock_popup.close.assert_called_once()
                mock_settings_dialog.close.assert_called_once()
                mock_detail_dialog.close.assert_called_once()
                
                # Should stop tray app
                mock_stop.assert_called_once()
                
                # Should process events and quit
                mock_app.processEvents.assert_called_once()
                mock_app.quit.assert_called_once()