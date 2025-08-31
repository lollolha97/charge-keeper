"""System tray application for battery management."""

import sys
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, 
    QWidget, QVBoxLayout, QLabel, QSlider, QPushButton
)
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap

from src.core.battery_manager import BatteryManager, BatteryInfo
from src.core.cli_interface import CliResult


class TrayIcon(QSystemTrayIcon):
    """System tray icon for battery management."""
    
    def __init__(self, parent=None):
        """Initialize tray icon.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set default icon (create a simple colored square)
        self._setup_default_icon()
        
        # Set default tooltip
        self.setToolTip("A14 Charge Keeper")
        
        # Setup context menu
        self._setup_context_menu()
    
    def _setup_default_icon(self):
        """Setup default battery icon."""
        # Create a simple 16x16 colored pixmap as placeholder
        pixmap = QPixmap(16, 16)
        pixmap.fill()  # White background
        icon = QIcon(pixmap)
        self.setIcon(icon)
    
    def _setup_context_menu(self):
        """Setup context menu for tray icon."""
        menu = QMenu()
        
        # Battery status action
        status_action = QAction("배터리 상태", self)
        menu.addAction(status_action)
        
        menu.addSeparator()
        
        # Settings action
        settings_action = QAction("설정", self)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # Quit action
        quit_action = QAction("종료", self)
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
    
    def update_battery_status(self, battery_info: BatteryInfo):
        """Update icon and tooltip based on battery status.
        
        Args:
            battery_info: Current battery information
        """
        tooltip = self._generate_tooltip(battery_info)
        self.setToolTip(tooltip)
        
        # TODO: Update icon based on battery state and threshold
        # This would involve creating different icons for:
        # - Charging vs discharging
        # - Battery level (full, medium, low)
        # - Threshold limited vs unlimited
    
    def _generate_tooltip(self, battery_info: BatteryInfo) -> str:
        """Generate tooltip text from battery information.
        
        Args:
            battery_info: Current battery information
            
        Returns:
            Formatted tooltip string
        """
        tooltip_parts = ["A14 Charge Keeper"]
        
        if battery_info.percentage is not None:
            tooltip_parts.append(f"배터리: {battery_info.percentage}%")
        
        if battery_info.state:
            state_text = self._translate_battery_state(battery_info.state)
            tooltip_parts.append(f"상태: {state_text}")
        
        if battery_info.end_threshold != 100:
            tooltip_parts.append(f"제한: {battery_info.end_threshold}%")
        
        return " | ".join(tooltip_parts)
    
    @staticmethod
    def _translate_battery_state(state: str) -> str:
        """Translate battery state to Korean.
        
        Args:
            state: English battery state
            
        Returns:
            Korean translation of state
        """
        translations = {
            "charging": "충전 중",
            "discharging": "방전 중",
            "not charging": "충전 안함",
            "full": "완충",
            "unknown": "알 수 없음"
        }
        return translations.get(state.lower(), state)


class SystemTrayApp:
    """Main system tray application for battery management."""
    
    def __init__(self, battery_manager: Optional[BatteryManager] = None, 
                 refresh_interval: int = 30000):
        """Initialize system tray application.
        
        Args:
            battery_manager: Battery manager instance (creates new if None)
            refresh_interval: Auto-refresh interval in milliseconds
        """
        self.battery_manager = battery_manager or BatteryManager()
        self.refresh_interval = refresh_interval
        
        # Create tray icon
        self.tray_icon = TrayIcon()
        
        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_battery_status)
        
        # Connect menu actions
        self._connect_menu_actions()
    
    def _connect_menu_actions(self):
        """Connect context menu actions to handlers."""
        menu = self.tray_icon.contextMenu()
        actions = menu.actions()
        
        for action in actions:
            if action.text() == "배터리 상태":
                action.triggered.connect(self._show_status)
            elif action.text() == "설정":
                action.triggered.connect(self._show_settings)
            elif action.text() == "종료":
                action.triggered.connect(self._quit_application)
    
    def start(self) -> CliResult:
        """Start the system tray application.
        
        Returns:
            CliResult indicating success or failure
        """
        # Initialize battery manager
        result = self.battery_manager.initialize()
        
        if not result.success:
            return result
        
        # Show tray icon
        self.tray_icon.show()
        
        # Start auto-refresh timer
        if self.refresh_interval > 0:
            self.refresh_timer.start(self.refresh_interval)
        
        # Initial status update
        self.refresh_battery_status()
        
        return CliResult.success()
    
    def stop(self):
        """Stop the system tray application."""
        # Stop timer
        self.refresh_timer.stop()
        
        # Hide tray icon
        self.tray_icon.hide()
    
    def refresh_battery_status(self):
        """Refresh battery status and update tray icon."""
        if not self.battery_manager.is_initialized:
            return
        
        result = self.battery_manager.refresh_status()
        
        if result.success and self.battery_manager.current_info:
            self.tray_icon.update_battery_status(self.battery_manager.current_info)
    
    def _show_status(self):
        """Show battery status dialog."""
        # TODO: Implement status dialog
        print("Show status dialog")
    
    def _show_settings(self):
        """Show settings dialog."""
        # TODO: Implement settings dialog
        print("Show settings dialog")
    
    def _quit_application(self):
        """Quit the application."""
        self.stop()
        if QApplication.instance():
            QApplication.instance().quit()


def main():
    """Main entry point for the system tray application."""
    app = QApplication(sys.argv)
    
    # Check system tray availability
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("System tray is not available on this system.")
        return 1
    
    # Create and start tray app
    tray_app = SystemTrayApp()
    result = tray_app.start()
    
    if not result.success:
        print(f"Failed to start application: {result.error_message}")
        return 1
    
    # Run application
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())