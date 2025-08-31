"""Simple battery menu for debugging."""

from PyQt5.QtWidgets import QMenu, QAction, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton, QWidgetAction
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

from src.core.battery_manager import BatteryManager



class SimpleBatteryMenu(QMenu):
    """Simple battery menu for testing."""
    
    # Signals
    status_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self, battery_manager: BatteryManager, parent=None):
        """Initialize simple battery menu."""
        super().__init__(parent)
        
        self.battery_manager = battery_manager
        self._setup_menu()
    
    def _setup_menu(self):
        """Setup the simple menu."""
        # Try to refresh battery info first
        if not self.battery_manager.is_initialized:
            init_result = self.battery_manager.initialize()
            if init_result.success:
                self.battery_manager.refresh_status()
        
        # Battery info header
        battery_info = "🔋 배터리 상태"
        if self.battery_manager.current_info and self.battery_manager.current_info.percentage:
            percentage = self.battery_manager.current_info.percentage
            state = self.battery_manager.current_info.state or ""
            state_korean_map = {
                "charging": "충전 중",
                "discharging": "방전 중", 
                "not charging": "충전 안함",
                "full": "완충",
                "unknown": "알 수 없음"
            }
            state_korean = state_korean_map.get(state.lower(), state) if state else ""
            if state_korean:
                battery_info = f"🔋 {percentage}% • {state_korean}"
            else:
                battery_info = f"🔋 {percentage}%"
        else:
            battery_info = "🔋 ??%"
        
        info_action = QAction(battery_info, self)
        info_action.setEnabled(False)  # Just for display
        self.addAction(info_action)
        
        self.addSeparator()
        
        # Current threshold value
        current_threshold = 70  # Default, will be updated
        if self.battery_manager.current_info:
            current_threshold = self.battery_manager.current_info.end_threshold
        
        # Threshold control section
        threshold_title = QAction(f"⚡ 충전 제한: {current_threshold}%", self)
        threshold_title.setEnabled(False)
        self.addAction(threshold_title)
        
        # Quick threshold options
        for threshold in [60, 70, 80, 90, 100]:
            action = QAction(f"  {threshold}%", self)
            if threshold == current_threshold:
                action.setText(f"● {threshold}%")
            action.triggered.connect(lambda checked, t=threshold: self._set_threshold(t))
            self.addAction(action)
        
        self.addSeparator()
        
        # Status and quit
        status_action = QAction("📊 배터리 상태", self)
        status_action.triggered.connect(self.status_requested.emit)
        self.addAction(status_action)
        
        self.addSeparator()
        
        quit_action = QAction("🚪 종료", self)
        quit_action.triggered.connect(self.quit_requested.emit)
        self.addAction(quit_action)
        
        # Set wider menu width
        self.setMinimumWidth(350)
        
        # Add some styling for better appearance
        self.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 4px;
                font-size: 13px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
                min-width: 280px;
            }
            QMenu::item:selected {
                background-color: #404040;
            }
            QMenu::item:disabled {
                color: #cccccc;
                background-color: transparent;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555555;
                margin: 4px 8px;
            }
        """)
    
    
    def _set_threshold(self, threshold: int):
        """Set battery threshold and close menu."""
        result = self.battery_manager.set_threshold(threshold)
        if result.success:
            print(f"Threshold set to {threshold}%")
        else:
            print(f"Failed to set threshold: {result.error_message}")
        self.hide()
    
    def set_threshold(self, threshold: int):
        """Set battery threshold."""
        result = self.battery_manager.set_threshold(threshold)
        if result.success:
            print(f"Threshold set to {threshold}%")
        else:
            print(f"Failed to set threshold: {result.error_message}")
    
    def refresh_battery_info(self):
        """Refresh battery information."""
        # Simple refresh - just update the first action text
        if self.battery_manager.current_info:
            percentage = self.battery_manager.current_info.percentage or "?"
            state = self.battery_manager.current_info.state or ""
            state_korean_map = {
                "charging": "충전 중",
                "discharging": "방전 중", 
                "not charging": "충전 안함",
                "full": "완충",
                "unknown": "알 수 없음"
            }
            state_korean = state_korean_map.get(state.lower(), state) if state else ""
            if state_korean:
                battery_info = f"🔋 {percentage}% • {state_korean}"
            else:
                battery_info = f"🔋 {percentage}%"
            if self.actions():
                self.actions()[0].setText(battery_info)