"""Battery detail information dialog."""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGridLayout, QPushButton, QGraphicsDropShadowEffect, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPainter, QIcon, QPixmap

from src.core.battery_manager import BatteryManager, BatteryInfo


class BatteryDetailDialog(QDialog):
    """Dialog showing detailed battery information."""
    
    def __init__(self, battery_manager: BatteryManager, parent=None):
        """Initialize battery detail dialog.
        
        Args:
            battery_manager: Battery manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.battery_manager = battery_manager
        self._setup_window_properties()
        self._setup_ui()
        self.refresh_battery_info()
    
    def _setup_window_properties(self):
        """Setup window properties."""
        self.setWindowTitle("A14 Charge Keeper")
        self.setFixedSize(580, 620)  # Adjusted for sectioned layout
        self.setModal(True)
        
        # Set window icon
        try:
            icon_path = "/home/sang/Developments/tuf-charge-keeper/icon-Photoroom.png"
            self.setWindowIcon(QIcon(icon_path))
        except:
            pass  # If icon file not found, continue without it
        
        # Center on screen
        screen = self.screen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        # Apply default dark theme
        self.apply_theme('dark')
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)
    
    def apply_theme(self, theme='dark'):
        """Apply theme to battery detail dialog."""
        if theme == 'light':
            self.setStyleSheet("""
                QDialog {
                    background-color: #ffffff;
                    border-radius: 12px;
                }
                QLabel {
                    color: #000000;
                    background: transparent;
                    border: none;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }
                QFrame {
                    background-color: #f8f8f8;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                }
                QPushButton {
                    background-color: #007aff;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #0051d5;
                }
                QPushButton:pressed {
                    background-color: #003d82;
                }
                QTableWidget {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    gridline-color: #e0e0e0;
                }
                QTableWidget::item {
                    background-color: #ffffff;
                    color: #000000;
                    border: none;
                    padding: 8px;
                }
                QTableWidget::item:selected {
                    background-color: #007aff;
                    color: #ffffff;
                }
                QHeaderView::section {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #e0e0e0;
                    padding: 8px;
                    font-weight: bold;
                }
            """)
        else:
            # Dark theme
            self.setStyleSheet("""
                QDialog {
                    background-color: #1c1c1e;
                    border-radius: 12px;
                }
                QLabel {
                    color: #ffffff;
                    background: transparent;
                    border: none;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }
                QFrame {
                    background-color: #2c2c2e;
                    border-radius: 8px;
                    border: none;
                }
                QPushButton {
                    background-color: #007aff;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #0051d5;
                }
                QPushButton:pressed {
                    background-color: #003d82;
                }
                QTableWidget {
                    background-color: #2c2c2e;
                    color: #ffffff;
                    border: 1px solid #3a3a3c;
                    border-radius: 6px;
                    gridline-color: #3a3a3c;
                }
                QTableWidget::item {
                    background-color: #2c2c2e;
                    color: #ffffff;
                    border: none;
                    padding: 8px;
                }
                QTableWidget::item:selected {
                    background-color: #007aff;
                    color: #ffffff;
                }
                QHeaderView::section {
                    background-color: #3a3a3c;
                    color: #ffffff;
                    border: 1px solid #48484a;
                    padding: 8px;
                    font-weight: bold;
                }
            """)
    
    def _setup_ui(self):
        """Setup the UI layout with categorized sections."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Battery Details")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ffffff; padding: 0px 0px 8px 0px;")
        main_layout.addWidget(title_label)
        
        # Use QTableWidget with sectioned layout
        self.info_table = QTableWidget()
        self.info_table.setColumnCount(2)
        self.info_table.setRowCount(18)  # More rows for section headers
        self.info_table.setHorizontalHeaderLabels(["Property", "Value"])
        
        # Define sections with headers and data
        self.table_sections = [
            # Battery Status Section
            ("BATTERY STATUS", None, "header"),
            ("Battery Level", "percentage", "data"),
            ("Charging State", "state", "data"),
            ("Time to Empty", "time_to_empty", "data"),
            ("", None, "spacer"),
            
            # Power Information Section  
            ("POWER INFORMATION", None, "header"),
            ("Power Consumption", "power", "data"),
            ("Voltage", "voltage", "data"),
            ("Current Energy", "energy_current", "data"),
            ("Full Energy", "energy_full", "data"),
            ("", None, "spacer"),
            
            # Battery Health Section
            ("BATTERY HEALTH", None, "header"),
            ("Design Energy", "energy_full_design", "data"),
            ("Battery Health", "capacity", "data"),
            ("Charge Limit", "end_threshold", "data"),
            ("", None, "spacer"),
            
            # Hardware Section
            ("HARDWARE INFORMATION", None, "header"),
            ("Manufacturer", "manufacturer", "data"),
            ("Model", "model", "data")
        ]
        
        # Populate table with sectioned data
        for row, (label, key, row_type) in enumerate(self.table_sections):
            if row_type == "header":
                # Section header
                header_item = QTableWidgetItem(label)
                header_item.setFlags(Qt.ItemIsEnabled)
                header_item.setFont(QFont("SF Pro", 11, QFont.Bold))
                header_item.setForeground(QColor("#007aff"))
                header_item.setBackground(QColor("#2c2c2e"))
                self.info_table.setItem(row, 0, header_item)
                
                # Empty value cell for header
                empty_item = QTableWidgetItem("")
                empty_item.setFlags(Qt.ItemIsEnabled)
                empty_item.setBackground(QColor("#2c2c2e"))
                self.info_table.setItem(row, 1, empty_item)
                
            elif row_type == "data":
                # Data row
                label_item = QTableWidgetItem(label)
                label_item.setFlags(Qt.ItemIsEnabled)
                label_item.setFont(QFont("SF Pro", 10))
                label_item.setForeground(QColor("#ffffff"))
                self.info_table.setItem(row, 0, label_item)
                
                # Value item
                value_item = QTableWidgetItem("Unknown")
                value_item.setFlags(Qt.ItemIsEnabled)
                value_item.setFont(QFont("SF Pro", 10))
                value_item.setForeground(QColor("#8e8e93"))
                self.info_table.setItem(row, 1, value_item)
                
            elif row_type == "spacer":
                # Spacer row
                spacer_item = QTableWidgetItem("")
                spacer_item.setFlags(Qt.ItemIsEnabled)
                spacer_item.setBackground(QColor("#1c1c1e"))
                self.info_table.setItem(row, 0, spacer_item)
                
                spacer_item2 = QTableWidgetItem("")
                spacer_item2.setFlags(Qt.ItemIsEnabled) 
                spacer_item2.setBackground(QColor("#1c1c1e"))
                self.info_table.setItem(row, 1, spacer_item2)
        
        # Enhanced table styling
        self.info_table.setStyleSheet("""
            QTableWidget {
                background-color: #1c1c1e;
                color: #ffffff;
                border: none;
                selection-background-color: transparent;
                gridline-color: #3a3a3c;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 10px 12px;
                border: none;
                border-bottom: 1px solid #2c2c2e;
            }
            QHeaderView::section {
                background-color: #2c2c2e;
                color: #ffffff;
                border: none;
                padding: 12px;
                font-weight: 600;
                font-size: 12px;
                border-radius: 4px;
            }
            QTableWidget::item:selected {
                background-color: transparent;
            }
        """)
        
        # Set column widths for better proportions
        self.info_table.setColumnWidth(0, 280)
        self.info_table.setColumnWidth(1, 220)
        
        # Hide row numbers
        self.info_table.verticalHeader().setVisible(False)
        
        # Set row heights for different types
        for row, (label, key, row_type) in enumerate(self.table_sections):
            if row_type == "header":
                self.info_table.setRowHeight(row, 35)
            elif row_type == "data":
                self.info_table.setRowHeight(row, 32)
            elif row_type == "spacer":
                self.info_table.setRowHeight(row, 12)
        
        # Disable editing and selection
        self.info_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.info_table.setSelectionMode(QTableWidget.NoSelection)
        
        # Remove focus outline
        self.info_table.setFocusPolicy(Qt.NoFocus)
        
        main_layout.addWidget(self.info_table)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_battery_info)
        button_layout.addWidget(refresh_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)  # Hide instead of accept
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def _create_section_header(self, title: str) -> QLabel:
        """Create a styled section header."""
        header = QLabel(title)
        header_font = QFont()
        header_font.setPointSize(13)
        header_font.setWeight(QFont.Bold)
        header.setFont(header_font)
        header.setStyleSheet("color: #007aff; padding: 8px 0px 4px 0px;")
        return header
    
    def _create_info_row(self, label_text: str, key: str, parent_layout) -> QLabel:
        """Create an information row with label and value."""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(16)
        
        # Label
        label = QLabel(label_text)
        label.setMinimumWidth(140)
        label.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: 500;")
        
        # Value
        value_label = QLabel("Unknown")
        value_label.setStyleSheet("color: #8e8e93; font-size: 11px;")
        value_label.setAlignment(Qt.AlignRight)
        
        row_layout.addWidget(label)
        row_layout.addStretch()
        row_layout.addWidget(value_label)
        
        parent_layout.addLayout(row_layout)
        
        # Store reference for updates
        self.value_labels[key] = value_label
        return value_label
    
    def _create_status_section(self, main_layout):
        """Create battery status section."""
        main_layout.addWidget(self._create_section_header("Battery Status"))
        
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background-color: #2c2c2e;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(8)
        section_layout.setContentsMargins(12, 12, 12, 12)
        
        self._create_info_row("Battery Level", "percentage", section_layout)
        self._create_info_row("Charging State", "state", section_layout)
        self._create_info_row("Time to Empty", "time_to_empty", section_layout)
        
        main_layout.addWidget(section_frame)
    
    def _create_power_section(self, main_layout):
        """Create power information section."""
        main_layout.addWidget(self._create_section_header("Power Information"))
        
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background-color: #2c2c2e;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(8)
        section_layout.setContentsMargins(12, 12, 12, 12)
        
        self._create_info_row("Power Consumption", "power", section_layout)
        self._create_info_row("Voltage", "voltage", section_layout)
        self._create_info_row("Current Energy", "energy_current", section_layout)
        self._create_info_row("Full Energy", "energy_full", section_layout)
        
        main_layout.addWidget(section_frame)
    
    def _create_health_section(self, main_layout):
        """Create battery health section."""
        main_layout.addWidget(self._create_section_header("Battery Health"))
        
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background-color: #2c2c2e;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(8)
        section_layout.setContentsMargins(12, 12, 12, 12)
        
        self._create_info_row("Design Energy", "energy_full_design", section_layout)
        self._create_info_row("Battery Health", "capacity", section_layout)
        self._create_info_row("Charge Limit", "end_threshold", section_layout)
        
        main_layout.addWidget(section_frame)
    
    def _create_hardware_section(self, main_layout):
        """Create hardware information section."""
        main_layout.addWidget(self._create_section_header("Hardware Information"))
        
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background-color: #2c2c2e;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(8)
        section_layout.setContentsMargins(12, 12, 12, 12)
        
        self._create_info_row("Manufacturer", "manufacturer", section_layout)
        self._create_info_row("Model", "model", section_layout)
        
        main_layout.addWidget(section_frame)
    
    def refresh_battery_info(self):
        """Refresh battery information display."""
        if not self.battery_manager.is_initialized:
            init_result = self.battery_manager.initialize()
            if not init_result.success:
                return
        
        result = self.battery_manager.refresh_status()
        if result.success and self.battery_manager.current_info:
            self.update_battery_info(self.battery_manager.current_info)
    
    def update_battery_info(self, battery_info: BatteryInfo):
        """Update displayed battery information.
        
        Args:
            battery_info: Current battery information
        """
        # Create mapping of keys to formatted values
        data_values = {
            "percentage": f"{battery_info.percentage}%" if battery_info.percentage is not None else "Unknown",
            "state": self._translate_state_english(battery_info.state) if battery_info.state else "Unknown",
            "time_to_empty": str(battery_info.time_to_empty) if battery_info.time_to_empty else "Unknown",
            "power": f"{battery_info.energy_rate:.3f}W" if battery_info.energy_rate else "Unknown",
            "voltage": f"{battery_info.voltage:.3f}V" if battery_info.voltage else "Unknown",
            "energy_current": f"{battery_info.energy_current:.2f}Wh" if battery_info.energy_current else "Unknown",
            "energy_full": f"{battery_info.energy_full:.2f}Wh" if battery_info.energy_full else "Unknown",
            "energy_full_design": f"{battery_info.energy_full_design:.1f}Wh" if battery_info.energy_full_design else "Unknown",
            "capacity": f"{battery_info.capacity:.1f}%" if battery_info.capacity else "Unknown",
            "end_threshold": f"{battery_info.end_threshold}%",
            "manufacturer": str(battery_info.vendor) if battery_info.vendor else "Unknown",
            "model": str(battery_info.model) if battery_info.model else "Unknown"
        }
        
        # Update table items using new sectioned structure
        for row, (label, key, row_type) in enumerate(self.table_sections):
            if row_type == "data" and key and key in data_values:
                value_item = self.info_table.item(row, 1)
                if value_item:
                    value_item.setText(data_values[key])
                    
                    # Apply colors for specific items
                    if key == "percentage" and battery_info.percentage is not None:
                        if battery_info.percentage <= 20:
                            value_item.setForeground(QColor("#ff453a"))  # Red
                        elif battery_info.percentage <= 50:
                            value_item.setForeground(QColor("#ff9f0a"))  # Orange
                        else:
                            value_item.setForeground(QColor("#30d158"))  # Green
                    elif key == "state" and battery_info.state and "charging" in battery_info.state.lower():
                        value_item.setForeground(QColor("#007aff"))  # Blue for charging
                    else:
                        value_item.setForeground(QColor("#d1d1d6"))  # Light gray for data
    
    
    @staticmethod
    def _translate_state_english(state: str) -> str:
        """Translate battery state to clean English.
        
        Args:
            state: Raw battery state
            
        Returns:
            Clean English translation of state
        """
        translations = {
            "charging": "Charging",
            "discharging": "Not Charging", 
            "not charging": "Not Charging",
            "full": "Full",
            "unknown": "Unknown"
        }
        return translations.get(state.lower(), state.title())
    
    @staticmethod
    def _translate_state_korean(state: str) -> str:
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
    
    @staticmethod
    def _translate_technology_korean(tech: str) -> str:
        """Translate battery technology to Korean."""
        translations = {
            "li-ion": "리튬 이온",
            "lithium-ion": "리튬 이온",
            "li-poly": "리튬 폴리머",
            "lithium-polymer": "리튬 폴리머",
            "nimh": "니켈 수소",
            "nickel-metal hydride": "니켈 수소",
            "unknown": "알 수 없음"
        }
        return translations.get(tech.lower(), tech)
    
    @staticmethod
    def _translate_manufacturer_korean(mfg: str) -> str:
        """Translate manufacturer to Korean if needed."""
        translations = {
            "asus": "에이수스",
            "lenovo": "레노버",
            "dell": "델",
            "hp": "HP",
            "acer": "에이서",
            "msi": "MSI",
            "samsung": "삼성",
            "lg": "LG",
            "unknown": "알 수 없음"
        }
        return translations.get(mfg.lower(), mfg)
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.hide()  # Just hide the dialog, don't close app
            event.accept()
            return
        super().keyPressEvent(event)
    
    def showEvent(self, event):
        """Handle show event - refresh data when dialog becomes visible."""
        super().showEvent(event)
        # Force refresh when dialog is shown
        self.refresh_battery_info()
    
    def closeEvent(self, event):
        """Handle close event - hide dialog instead of closing."""
        event.ignore()  # Don't close the dialog
        self.hide()     # Just hide it