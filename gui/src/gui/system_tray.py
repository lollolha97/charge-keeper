"""System tray application for battery management."""

import sys
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, 
    QWidget, QVBoxLayout, QLabel, QSlider, QPushButton
)
from PyQt5.QtCore import QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QBrush, QPen, QColor

from src.core.battery_manager import BatteryManager, BatteryInfo
from src.gui.simple_battery_menu import SimpleBatteryMenu
from src.gui.battery_popup import BatteryPopup
from src.gui.simple_context_menu import SimpleContextMenu
from src.gui.battery_detail_dialog import BatteryDetailDialog
from src.gui.settings_dialog import SettingsDialog
from src.core.cli_interface import CliResult
from src.core.config_manager import ConfigManager


class TrayIcon(QSystemTrayIcon):
    """System tray icon for battery management."""
    
    def __init__(self, parent=None):
        """Initialize tray icon.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set icon from file or fallback to default
        self._setup_icon_from_file()
        
        # Set default tooltip
        self.setToolTip("A14 Charge Keeper")
        
        # This will be set by SystemTrayApp - don't create default menu
        
        # Connect click handler for popup
        self.activated.connect(self._on_tray_activated)
    
    def _setup_icon_from_file(self):
        """Setup icon from file or create default battery icon."""
        try:
            import os
            # Try multiple possible icon paths
            possible_paths = [
                "/home/sang/Developments/tuf-charge-keeper/charge-keeper.png",
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "charge-keeper.png"),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "charge-keeper.png"))
            ]
            
            for icon_path in possible_paths:
                if os.path.exists(icon_path):
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        self.setIcon(icon)
                        print(f"System tray icon loaded from: {icon_path}")
                        return
        except Exception as e:
            print(f"Warning: Could not set system tray icon: {e}")
            pass
        
        # Fallback to default battery icon
        print("Using fallback battery icon")
        self._setup_default_icon()
    
    def _setup_default_icon(self):
        """Setup default battery icon."""
        # Create battery-shaped icon
        icon = self._create_battery_icon(percentage=100, is_charging=False)
        self.setIcon(icon)
    
    def _create_battery_icon(self, percentage: int = 100, is_charging: bool = False) -> QIcon:
        """Create battery-shaped icon with charge level.
        
        Args:
            percentage: Battery percentage (0-100)
            is_charging: Whether battery is charging
            
        Returns:
            QIcon with battery shape
        """
        size = 22
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Battery body dimensions
        body_width = 14
        body_height = 8
        body_x = 2
        body_y = (size - body_height) // 2
        
        # Terminal dimensions  
        terminal_width = 2
        terminal_height = 4
        terminal_x = body_x + body_width
        terminal_y = body_y + 2
        
        # Draw battery body outline
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush(QColor(240, 240, 240)))
        painter.drawRect(body_x, body_y, body_width, body_height)
        
        # Draw battery terminal
        painter.setBrush(QBrush(QColor(120, 120, 120)))
        painter.drawRect(terminal_x, terminal_y, terminal_width, terminal_height)
        
        # Draw charge level
        if percentage > 0:
            charge_width = int((body_width - 2) * percentage / 100)
            if percentage <= 20:
                charge_color = QColor(231, 76, 60)  # Red for low
            elif percentage <= 50:
                charge_color = QColor(241, 196, 15)  # Yellow for medium
            else:
                charge_color = QColor(39, 174, 96)  # Green for good
                
            painter.setBrush(QBrush(charge_color))
            painter.setPen(QPen(charge_color))
            painter.drawRect(body_x + 1, body_y + 1, charge_width, body_height - 2)
        
        # Draw charging indicator (lightning bolt)
        if is_charging:
            painter.setPen(QPen(QColor(52, 152, 219), 2))
            # Simple lightning bolt path
            painter.drawLine(body_x + 4, body_y + 2, body_x + 7, body_y + 4)
            painter.drawLine(body_x + 7, body_y + 4, body_x + 10, body_y + 2)
            painter.drawLine(body_x + 7, body_y + 4, body_x + 10, body_y + 6)
        
        painter.end()
        return QIcon(pixmap)
    
    def update_battery_icon(self, battery_info: BatteryInfo):
        """Update tray icon based on battery info.
        
        Args:
            battery_info: Current battery information
        """
        # Keep using the fixed charge-keeper.png icon
        # Don't change icon dynamically to maintain consistent branding
        pass
    
    
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
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        # This will be handled by SystemTrayApp
        pass


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
        self.config_manager = ConfigManager()
        self.config_manager.load()
        
        # Use config for refresh interval if available
        self.refresh_interval = self.config_manager.get('refresh_interval', refresh_interval // 1000) * 1000
        
        # Create tray icon
        self.tray_icon = TrayIcon()
        
        # Setup simple context menu for right-click
        self.context_menu = SimpleContextMenu(self.battery_manager)
        self.context_menu.settings_requested.connect(self._show_settings)
        self.context_menu.status_requested.connect(self._show_status)
        self.context_menu.quit_requested.connect(self._quit_application)
        
        # Apply saved theme to context menu
        saved_theme = self.config_manager.get('theme', 'dark')
        print(f"Applying initial theme {saved_theme} to context menu during creation")
        self.context_menu.apply_theme(saved_theme)
        
        # Don't set context menu - we'll handle clicks manually
        # self.tray_icon.setContextMenu(self.context_menu)
        
        # Create popup for left-click
        self.battery_popup = BatteryPopup(self.battery_manager)
        
        # Apply saved theme to popup immediately after creation
        saved_theme = self.config_manager.get('theme', 'dark')
        print(f"Applying initial theme {saved_theme} to battery popup during creation")
        self.battery_popup.apply_theme(saved_theme)
        self.battery_popup.closed.connect(self._on_popup_closed)
        
        # Force immediate style refresh of popup
        print(f"Force refreshing popup style for theme: {saved_theme}")
        self.battery_popup.style().unpolish(self.battery_popup)
        self.battery_popup.style().polish(self.battery_popup)
        self.battery_popup.update()
        
        # Create detail dialog for additional info
        self.detail_dialog = None
        
        # Create settings dialog
        self.settings_dialog = None
        
        # Connect tray activation to show popup
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        # Setup refresh timer (will be started in start() method)
        self.refresh_timer = None
    
    
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
        
        # Create and start refresh timer ensuring it's in main thread
        if self.refresh_interval > 0:
            # Ensure we're in the main thread before creating QTimer
            if QThread.currentThread() == QApplication.instance().thread():
                self.refresh_timer = QTimer()
                self.refresh_timer.timeout.connect(self.refresh_battery_status)
                # Move timer to main thread explicitly
                self.refresh_timer.moveToThread(QApplication.instance().thread())
                self.refresh_timer.start(self.refresh_interval)
            else:
                print("Warning: Not in main thread, timer creation skipped")
        
        # Initial status update
        self.refresh_battery_status()
        
        # Debug: Check config manager state
        print(f"Config manager loaded theme: {self.config_manager.get('theme', 'NOT_FOUND')}")
        
        return CliResult.success()
    
    def stop(self):
        """Stop the system tray application."""
        # Stop timer
        if self.refresh_timer:
            self.refresh_timer.stop()
        
        # Hide tray icon
        self.tray_icon.hide()
    
    def refresh_battery_status(self):
        """Refresh battery status and update tray icon."""
        if not self.battery_manager.is_initialized:
            return
        
        result = self.battery_manager.refresh_status()
        
        if result.success and self.battery_manager.current_info:
            # Update tray icon appearance
            self.tray_icon.update_battery_icon(self.battery_manager.current_info)
            
            # Update tooltip
            battery_info = self.battery_manager.current_info
            tooltip = f"A14 Charge Keeper - {battery_info.percentage or '?'}%"
            if battery_info.state:
                state_map = {"charging": "충전 중", "discharging": "방전 중", "full": "완충"}
                state = state_map.get(battery_info.state.lower(), battery_info.state)
                tooltip += f" ({state})"
            if battery_info.end_threshold != 100:
                tooltip += f" | 제한: {battery_info.end_threshold}%"
            self.tray_icon.setToolTip(tooltip)
            
            # Update popup if it's visible
            if self.battery_popup.isVisible():
                self.battery_popup.refresh_battery_info()
    
    def _show_status(self):
        """Show battery detail dialog."""
        if self.detail_dialog is None:
            self.detail_dialog = BatteryDetailDialog(self.battery_manager)
            # Apply current theme to detail dialog
            current_theme = self.config_manager.get('theme', 'dark')
            self.detail_dialog.apply_theme(current_theme)
        
        # If dialog is already visible, just bring it to front
        if self.detail_dialog.isVisible():
            self.detail_dialog.raise_()
            self.detail_dialog.activateWindow()
            return
        
        # Show dialog first, then refresh data
        self.detail_dialog.show()
        self.detail_dialog.refresh_battery_info()
        self.detail_dialog.raise_()
        self.detail_dialog.activateWindow()
    
    def _show_settings(self):
        """Show settings dialog."""
        if self.settings_dialog is None:
            # Create dialog with main window as parent if available
            parent = None
            if hasattr(QApplication.instance(), 'activeWindow'):
                parent = QApplication.instance().activeWindow()
            self.settings_dialog = SettingsDialog(self.config_manager, parent)
            self.settings_dialog.settings_changed.connect(self._on_settings_changed)
        
        # If dialog is already visible, just bring it to front
        if self.settings_dialog.isVisible():
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()
            return
        
        # Show dialog
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
    
    def _on_settings_changed(self):
        """Handle settings changes."""
        try:
            # Update refresh interval
            self._update_refresh_interval()
            
            # Apply new battery threshold
            self._apply_battery_threshold()
            
            # Apply theme changes to all components
            self._apply_theme_changes()
            
        except Exception as e:
            print(f"Error updating settings: {e}")
    
    def _update_refresh_interval(self):
        """Update refresh interval in a safe Qt context."""
        try:
            new_interval = self.config_manager.get('refresh_interval', 30) * 1000
            if new_interval != self.refresh_interval:
                self.refresh_interval = new_interval
                self._restart_timer()
        except Exception as e:
            print(f"Error updating refresh interval: {e}")
    
    def _restart_timer(self):
        """Restart the refresh timer in main thread context."""
        try:
            # Stop existing timer
            if self.refresh_timer and self.refresh_timer.isActive():
                self.refresh_timer.stop()
            
            if self.refresh_interval > 0:
                # Ensure we're in main thread
                if QThread.currentThread() == QApplication.instance().thread():
                    if not self.refresh_timer:
                        self.refresh_timer = QTimer()
                        self.refresh_timer.timeout.connect(self.refresh_battery_status)
                        # Ensure timer is bound to main thread
                        self.refresh_timer.moveToThread(QApplication.instance().thread())
                    self.refresh_timer.start(self.refresh_interval)
                else:
                    print("Warning: Cannot restart timer - not in main thread")
        except Exception as e:
            print(f"Error restarting timer: {e}")
    
    def _apply_battery_threshold(self):
        """Apply new battery threshold from settings."""
        try:
            new_threshold = self.config_manager.get('default_threshold', 80)
            print(f"Applying battery threshold: {new_threshold}%")
            
            # Use battery manager to set the threshold
            result = self.battery_manager.set_threshold(new_threshold)
            if result.success:
                print(f"Battery threshold successfully set to {new_threshold}%")
                # Refresh status to show updated info
                self.refresh_battery_status()
            else:
                print(f"Failed to set battery threshold: {result.error_message}")
                
        except Exception as e:
            print(f"Error applying battery threshold: {e}")
    
    def _apply_theme_changes(self):
        """Apply theme changes to all GUI components."""
        try:
            theme = self.config_manager.get('theme', 'dark')
            print(f"Applying theme: {theme}")
            
            # Apply theme to battery popup
            if self.battery_popup:
                print(f"Applying theme {theme} to battery popup")
                self.battery_popup.apply_theme(theme)
            else:
                print("Battery popup not available for theme application")
            
            # Apply theme to detail dialog if it exists
            if self.detail_dialog:
                print(f"Applying theme {theme} to detail dialog")
                self.detail_dialog.apply_theme(theme)
            
            # Apply theme to context menu
            if self.context_menu:
                print(f"Applying theme {theme} to context menu")
                self.context_menu.apply_theme(theme)
                
            # Settings dialog will apply theme when opened next time
            
        except Exception as e:
            print(f"Error applying theme changes: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.DoubleClick:  # Left click or double click
            self._show_popup()
        elif reason == QSystemTrayIcon.Context:  # Right click
            self._show_context_menu()
    
    def _show_popup(self):
        """Show battery popup near cursor."""
        # Refresh popup data
        self.battery_popup.refresh_battery_info()
        
        # Show popup near cursor
        self.battery_popup.show_near_cursor()
    
    def _show_context_menu(self):
        """Show context menu at cursor position."""
        from PyQt5.QtGui import QCursor
        self.context_menu.popup(QCursor.pos())
    
    def _on_popup_closed(self):
        """Handle popup closed."""
        pass  # Nothing special needed when popup closes
    
    def _quit_application(self):
        """Quit the application with proper cleanup."""
        try:
            # Close popup if open
            if self.battery_popup and self.battery_popup.isVisible():
                self.battery_popup.close()
            
            # Close settings dialog if open
            if self.settings_dialog and self.settings_dialog.isVisible():
                self.settings_dialog.close()
                
            # Close detail dialog if open
            if self.detail_dialog and self.detail_dialog.isVisible():
                self.detail_dialog.close()
            
            # Stop the tray app
            self.stop()
            
            # Process pending events before quitting
            app = QApplication.instance()
            if app:
                app.processEvents()
                app.quit()
        except Exception as e:
            print(f"Error during quit: {e}")
            # Force quit if there's an error
            if QApplication.instance():
                QApplication.instance().quit()


def main():
    """Main entry point for the system tray application."""
    # Use existing QApplication instance to prevent QBasicTimer issues
    app = QApplication.instance()
    if app is None:
        print("Error: No QApplication instance found. Create QApplication before calling main().")
        return 1
    
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
    
    # Run application using existing instance
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())