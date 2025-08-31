"""Battery control popup window that appears near tray icon."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, 
    QPushButton, QProgressBar, QFrame, QGraphicsDropShadowEffect, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QColor, QPainterPath, QRegion, QPainter

from src.core.battery_manager import BatteryManager, BatteryInfo


class BatteryPopup(QWidget):
    """Popup window for battery control with slider."""
    
    # Signals
    closed = pyqtSignal()
    
    def __init__(self, battery_manager: BatteryManager, parent=None):
        """Initialize battery popup.
        
        Args:
            battery_manager: Battery manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.battery_manager = battery_manager
        self.min_threshold = 20
        self.max_threshold = 100
        self.current_threshold = 100
        
        # Initialize with current battery info if available
        if battery_manager.current_info:
            self.current_threshold = battery_manager.current_info.end_threshold
        
        self._setup_ui()
        self._setup_window_properties()
        self.refresh_battery_info()
    
    def _setup_window_properties(self):
        """Setup window properties for popup behavior."""
        # Use Window instead of ToolTip for better key handling
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        
        # Enable focus so it can receive key events  
        self.setFocusPolicy(Qt.StrongFocus)
        # Don't use WA_TranslucentBackground - it makes everything transparent
        
        # Improve rendering performance - disable double buffering issues
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)  # Allow proper transparency
        self.setAttribute(Qt.WA_NoSystemBackground, True)  # Prevent system background interference
        
        # Auto-close when losing focus
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        
        # Make sure popup gets proper focus immediately
        self.setFocus(Qt.OtherFocusReason)
        
        # Install event filter for global mouse clicks
        QApplication.instance().installEventFilter(self)
        
        # Set compact size - slightly wider for better proportions
        self.setFixedSize(260, 145)
        
        # Modern macOS-style dark theme
        self.setStyleSheet("""
            BatteryPopup {
                background-color: #1c1c1e;
                border: 1px solid #38383a;
                border-radius: 12px;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
                border: none;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 0px;
                margin: 0px;
            }
            QSlider:horizontal {
                background: transparent;
                min-height: 20px;
                max-height: 20px;
            }
            QSlider::groove:horizontal {
                background: #3a3a3c;
                height: 2px;
                border-radius: 1px;
                border: none;
                margin: 9px 0;
            }
            QSlider::handle:horizontal {
                background: #007aff;
                border: none;
                width: 14px;
                height: 14px;
                border-radius: 7px;
                margin: -6px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #0051d5;
            }
            QSlider::handle:horizontal:pressed {
                background: #003d82;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #2c2c2e;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #30d158;
                border-radius: 4px;
                margin: 0px;
            }
        """)
    
    def _setup_ui(self):
        """Setup clean card-style UI."""
        # Main layout - optimized spacing
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(10)
        
        # Top section: Battery status
        status_layout = QVBoxLayout()
        status_layout.setSpacing(4)
        
        # Battery percentage and label in one line
        status_row = QHBoxLayout()
        self.battery_title_label = QLabel("Battery")
        self.battery_title_label.setAlignment(Qt.AlignLeft)
        font = QFont()
        font.setPointSize(11)
        font.setWeight(QFont.Medium)
        self.battery_title_label.setFont(font)
        
        self.battery_percent_label = QLabel("100%")
        self.battery_percent_label.setAlignment(Qt.AlignRight)
        self.battery_percent_label.setFixedWidth(35)  # Fixed width for percentage
        font2 = QFont()
        font2.setPointSize(11)
        self.battery_percent_label.setFont(font2)
        
        status_row.addWidget(self.battery_title_label)
        status_row.addWidget(self.battery_percent_label)
        status_layout.addLayout(status_row)
        
        # Battery state on separate line (smaller text, dimmed)
        self.battery_state_label = QLabel("Not Charging")
        self.battery_state_label.setAlignment(Qt.AlignLeft)
        font3 = QFont()
        font3.setPointSize(9)  # Even smaller font
        self.battery_state_label.setFont(font3)
        self.battery_state_label.setStyleSheet("color: #8e8e93;")  # Dimmed text
        status_layout.addWidget(self.battery_state_label)
        
        # Small spacing before progress bar
        status_layout.addSpacing(2)
        
        # Progress bar
        self.battery_progress = QProgressBar()
        self.battery_progress.setMinimum(0)
        self.battery_progress.setMaximum(100)
        self.battery_progress.setFixedHeight(8)
        self.battery_progress.setTextVisible(False)
        # Force style refresh
        self.battery_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #2c2c2e;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #30d158;
                border-radius: 4px;
                margin: 0px;
                border: none;
            }
        """)
        status_layout.addWidget(self.battery_progress)
        
        main_layout.addLayout(status_layout)
        
        # Bottom section: Charge limit
        limit_layout = QVBoxLayout()
        limit_layout.setSpacing(6)
        
        # Limit title and value in one line
        self.limit_row = QHBoxLayout()
        limit_title = QLabel("Charge Limit")
        limit_title.setAlignment(Qt.AlignLeft)
        font3 = QFont()
        font3.setPointSize(11)
        font3.setWeight(QFont.Medium)
        limit_title.setFont(font3)
        
        self.threshold_label = QLabel(f"{self.current_threshold}%")
        self.threshold_label.setAlignment(Qt.AlignRight)
        self.threshold_label.setFixedWidth(30)  # Fixed width to prevent layout shifts
        font4 = QFont()
        font4.setPointSize(11)
        self.threshold_label.setFont(font4)
        
        self.limit_row.addWidget(limit_title)
        self.limit_row.addWidget(self.threshold_label)
        limit_layout.addLayout(self.limit_row)
        
        # Slider
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(self.min_threshold)
        self.threshold_slider.setMaximum(self.max_threshold)
        self.threshold_slider.setValue(self.current_threshold)
        self.threshold_slider.valueChanged.connect(self._on_slider_changed)
        self.threshold_slider.sliderReleased.connect(self._on_slider_released)  # Apply on release
        limit_layout.addWidget(self.threshold_slider)
        
        main_layout.addLayout(limit_layout)
        
        self.setLayout(main_layout)
        
        # Add subtle drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 180))  # Deeper shadow for better depth
        self.setGraphicsEffect(shadow)
        
        # Rounded corners will be applied in showEvent when widget is properly sized
    
    def _create_rounded_mask(self):
        """Create rounded corner mask for the popup."""
        # Create mask with proper integer coordinates
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        
        # Convert to polygon with higher precision
        polygon = path.toFillPolygon().toPolygon()
        region = QRegion(polygon)
        self.setMask(region)
    
    def _on_slider_changed(self, value: int):
        """Handle slider value change."""
        # Remove old label and create new one to prevent overlapping
        self.limit_row.removeWidget(self.threshold_label)
        self.threshold_label.deleteLater()
        
        # Create new label
        self.threshold_label = QLabel(f"{value}%")
        self.threshold_label.setAlignment(Qt.AlignRight)
        self.threshold_label.setFixedWidth(30)
        font4 = QFont()
        font4.setPointSize(11)
        self.threshold_label.setFont(font4)
        
        # Add back to layout
        self.limit_row.addWidget(self.threshold_label)
        
        # Just trigger a single clean update
        self.update()
    
    def _on_slider_released(self):
        """Handle slider release - apply the threshold."""
        threshold = self.threshold_slider.value()
        result = self.battery_manager.set_threshold(threshold)
        if result.success:
            print(f"Threshold set to {threshold}%")
            # Don't close popup immediately, let user see the result
            self.hide()  # Hide immediately to avoid QTimer issues
        else:
            print(f"Failed to set threshold: {result.error_message}")
            # Show error briefly then hide
            self.hide()  # Hide immediately to avoid QTimer issues
    
    
    def _close_popup(self):
        """Hide popup immediately."""
        self.hide()  # Hide immediately to avoid QTimer issues
    
    def refresh_battery_info(self):
        """Refresh battery information."""
        if self.battery_manager.is_initialized:
            result = self.battery_manager.refresh_status()
            if result.success and self.battery_manager.current_info:
                self.update_battery_info(self.battery_manager.current_info)
    
    def update_battery_info(self, battery_info: BatteryInfo):
        """Update displayed battery information."""
        self.current_threshold = battery_info.end_threshold
        
        # Update battery percentage
        if battery_info.percentage is not None:
            self.battery_percent_label.setText(f"{battery_info.percentage}%")
            self.battery_progress.setValue(battery_info.percentage)
            # Update progress bar color based on battery state and level
            self._update_progress_bar_color(battery_info)
        else:
            self.battery_percent_label.setText("?%")
            self.battery_progress.setValue(0)
        
        # Update battery state
        if battery_info.state:
            state_english = self._translate_state_english(battery_info.state)
            self.battery_state_label.setText(state_english)
        else:
            self.battery_state_label.setText("Unknown")
        
        # Update threshold slider and label
        if battery_info.end_threshold != self.threshold_slider.value():
            self.threshold_slider.setValue(battery_info.end_threshold)
            self.threshold_label.setText(f"{battery_info.end_threshold}%")
    
    def _update_progress_bar_color(self, battery_info: BatteryInfo):
        """Update progress bar color based on battery state and level."""
        percentage = battery_info.percentage or 0
        state = battery_info.state.lower() if battery_info.state else ""
        
        # Removed debug prints for production
        
        # Determine color based on state and percentage
        if state == "charging":
            # Charging: Blue/cyan colors
            if percentage >= 80:
                color = "#007aff"  # Blue
            elif percentage >= 50:
                color = "#5ac8fa"  # Light blue
            else:
                color = "#64d2ff"  # Cyan
        elif percentage <= 20:
            # Low battery: Red
            color = "#ff453a"
        elif percentage <= 50:
            # Medium battery: Orange/Yellow
            color = "#ff9f0a"
        else:
            # Good battery: Green
            color = "#30d158"
        
        # Apply the color to progress bar
        self.battery_progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: #2c2c2e;
                height: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
                margin: 0px;
                border: none;
            }}
        """)
    
    def paintEvent(self, event):
        """Custom paint event to prevent text overlapping."""
        # Clear the widget completely before repainting
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(28, 28, 30))  # Fill with background color
        painter.end()
        super().paintEvent(event)
    
    def showEvent(self, event):
        """Handle show event - create rounded mask when widget has proper size."""
        super().showEvent(event)
        # Create rounded mask now that widget is properly sized
        self._create_rounded_mask()
        # Ensure focus is set properly for click-outside detection
        self.setFocus(Qt.OtherFocusReason)
        self.activateWindow()
    
    def mousePressEvent(self, event):
        """Handle mouse press - prevent focus issues that cause text overlapping."""
        # Allow click-outside detection to work by calling super()
        super().mousePressEvent(event)
    
    def show_near_cursor(self):
        """Show popup near cursor position."""
        from PyQt5.QtGui import QCursor
        
        cursor_pos = QCursor.pos()
        screen = self.screen().availableGeometry()
        
        # Position popup above and to the left of cursor
        popup_x = cursor_pos.x() - self.width() - 10
        popup_y = cursor_pos.y() - self.height() - 10
        
        # Make sure popup stays on screen
        if popup_x < screen.x():
            popup_x = cursor_pos.x() + 10
        
        if popup_y < screen.y():
            popup_y = cursor_pos.y() + 10
            
        if popup_x + self.width() > screen.right():
            popup_x = screen.right() - self.width() - 10
            
        if popup_y + self.height() > screen.bottom():
            popup_y = screen.bottom() - self.height() - 10
        
        self.move(popup_x, popup_y)
        self.show()
        self.raise_()
        self.activateWindow()
        # Force focus for immediate click-outside detection
        QApplication.processEvents()  # Process pending events first
        self.setFocus(Qt.OtherFocusReason)
    
    @staticmethod
    def _translate_state(state: str) -> str:
        """Translate battery state to Korean."""
        translations = {
            "charging": "충전 중",
            "discharging": "방전 중", 
            "not charging": "충전 안함",
            "full": "완충",
            "unknown": "알 수 없음"
        }
        return translations.get(state.lower(), state)
    
    @staticmethod
    def _translate_state_english(state: str) -> str:
        """Translate battery state to clean English."""
        translations = {
            "charging": "Charging",
            "discharging": "Not Charging", 
            "not charging": "Not Charging",
            "full": "Full",
            "unknown": "Unknown"
        }
        return translations.get(state.lower(), state.title())
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.hide()  # Hide popup, don't close
            event.accept()  # Stop event propagation
            return
        super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        """Handle focus lost - hide popup."""
        self.hide()
        super().focusOutEvent(event)
    
    def eventFilter(self, obj, event):
        """Event filter to detect clicks outside popup."""
        if event.type() == QEvent.MouseButtonPress and self.isVisible():
            # Check if click is outside this popup
            global_pos = event.globalPos()
            popup_rect = self.geometry()
            
            if not popup_rect.contains(global_pos):
                self.hide()
                return True  # Event handled
        
        return super().eventFilter(obj, event)
    
    def closeEvent(self, event):
        """Handle close event."""
        self.closed.emit()
        super().closeEvent(event)