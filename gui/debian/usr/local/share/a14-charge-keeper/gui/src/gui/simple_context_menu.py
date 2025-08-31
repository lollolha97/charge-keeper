"""Simple context menu for tray icon right-click."""

from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import pyqtSignal

from src.core.battery_manager import BatteryManager


class SimpleContextMenu(QMenu):
    """Simple context menu with basic options."""
    
    # Signals
    settings_requested = pyqtSignal()
    status_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self, battery_manager: BatteryManager, parent=None):
        """Initialize simple context menu.
        
        Args:
            battery_manager: Battery manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.battery_manager = battery_manager
        self._setup_menu()
    
    def _setup_menu(self):
        """Setup the context menu."""
        # Battery details action
        details_action = QAction("📊 Battery Details", self)
        details_action.triggered.connect(self.status_requested.emit)
        self.addAction(details_action)
        
        # Settings action
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.settings_requested.emit)
        self.addAction(settings_action)
        
        self.addSeparator()
        
        # Quit action
        quit_action = QAction("🚪 Quit", self)
        quit_action.triggered.connect(self.quit_requested.emit)
        self.addAction(quit_action)
        
        # Don't apply hardcoded style - will be set by theme
        self.apply_theme('dark')  # Default theme
    
    def apply_theme(self, theme='dark'):
        """Apply theme to context menu."""
        print(f"SimpleContextMenu: Applying {theme} theme")
        
        if theme == 'light':
            self.setStyleSheet("""
                QMenu {
                    background-color: #f8f9fa;
                    color: #212529;
                    border: 1px solid #dee2e6;
                    border-radius: 12px;
                    padding: 8px;
                    font-size: 13px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    font-weight: 500;
                }
                QMenu::item {
                    padding: 10px 16px;
                    border-radius: 8px;
                    min-width: 140px;
                    margin: 2px;
                }
                QMenu::item:selected {
                    background-color: #007aff;
                    color: #ffffff;
                }
                QMenu::item:pressed {
                    background-color: #0051d5;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #ced4da;
                    margin: 6px 12px;
                    border: none;
                }
            """)
        else:
            # Dark theme
            self.setStyleSheet("""
                QMenu {
                    background-color: #1c1c1e;
                    color: #ffffff;
                    border: 1px solid #38383a;
                    border-radius: 12px;
                    padding: 8px;
                    font-size: 13px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    font-weight: 500;
                }
                QMenu::item {
                    padding: 10px 16px;
                    border-radius: 8px;
                    min-width: 140px;
                    margin: 2px;
                }
                QMenu::item:selected {
                    background-color: #007aff;
                    color: #ffffff;
                }
                QMenu::item:pressed {
                    background-color: #0051d5;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #3a3a3c;
                    margin: 6px 12px;
                    border: none;
                }
            """)
        
        print(f"SimpleContextMenu: {theme} theme stylesheet applied")