"""Settings dialog for A14 Charge Keeper GUI application."""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QCheckBox, QSpinBox, QComboBox, QPushButton, QGroupBox,
    QFrame, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from src.core.config_manager import ConfigManager


class SettingsDialog(QDialog):
    """Settings configuration dialog."""
    
    # Signals
    settings_changed = pyqtSignal()
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        """Initialize settings dialog.
        
        Args:
            config_manager: Configuration manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self._setup_ui()
        self._setup_window_properties()
        self.load_settings()
    
    def _setup_window_properties(self):
        """Setup window properties."""
        self.setWindowTitle("A14 Charge Keeper - Settings")
        self.setModal(True)
        self.setFixedSize(450, 400)
        
        # Set window icon
        try:
            icon_path = "/home/sang/Developments/tuf-charge-keeper/icon-Photoroom.png"
            self.setWindowIcon(QIcon(icon_path))
        except:
            pass
        
        # Center on parent or screen
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)
        
        # Apply theme based on current settings
        current_theme = self.config_manager.get('theme', 'dark')
        print(f"SettingsDialog: Applying initial theme {current_theme}")
        if current_theme == 'light':
            self._apply_light_theme()
        else:
            self._apply_dark_theme()
    
    def _apply_dark_theme(self):
        """Apply dark theme based on light theme structure."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1c1c1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QGroupBox {
                color: #ffffff;
                border: 2px solid #3a3a3c;
            }
            QGroupBox::title {
                color: #007aff;
            }
            QCheckBox {
                color: #ffffff;
            }
            QSpinBox, QComboBox {
                background-color: #2c2c2e;
                border: 1px solid #3a3a3c;
                color: #ffffff;
            }
            QPushButton {
                background-color: #007aff;
                color: #ffffff;
            }
            QPushButton[class="secondary"] {
                background-color: #2c2c2e;
                border: 1px solid #3a3a3c;
                color: #ffffff;
            }
        """)
    
    def _apply_light_theme(self):
        """Apply light theme based on dark theme structure."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                color: #212529;
            }
            QLabel {
                color: #212529;
            }
            QGroupBox {
                color: #212529;
                border: 2px solid #dee2e6;
            }
            QGroupBox::title {
                color: #007aff;
            }
            QCheckBox {
                color: #212529;
            }
            QSpinBox, QComboBox {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                color: #212529;
            }
            QPushButton {
                background-color: #007aff;
                color: #ffffff;
            }
            QPushButton[class="secondary"] {
                background-color: #f8f9fa;
                border: 1px solid #ced4da;
                color: #212529;
            }
        """)
    
    def _setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Settings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # General settings group
        general_group = QGroupBox("General")
        general_layout = QGridLayout()
        general_layout.setSpacing(10)
        general_layout.setContentsMargins(10, 15, 10, 10)
        
        # Auto start checkbox
        self.auto_start_checkbox = QCheckBox("Start automatically with system")
        general_layout.addWidget(self.auto_start_checkbox, 0, 0, 1, 2)
        
        # Show notifications checkbox
        self.notifications_checkbox = QCheckBox("Show notifications")
        general_layout.addWidget(self.notifications_checkbox, 1, 0, 1, 2)
        
        # Default threshold
        threshold_label = QLabel("Default Threshold:")
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(20, 100)
        self.threshold_spinbox.setSuffix("%")
        general_layout.addWidget(threshold_label, 2, 0)
        general_layout.addWidget(self.threshold_spinbox, 2, 1)
        
        # Refresh interval
        refresh_label = QLabel("Refresh Interval:")
        self.refresh_interval_spinbox = QSpinBox()
        self.refresh_interval_spinbox.setRange(5, 300)
        self.refresh_interval_spinbox.setSuffix(" sec")
        general_layout.addWidget(refresh_label, 3, 0)
        general_layout.addWidget(self.refresh_interval_spinbox, 3, 1)
        
        general_group.setLayout(general_layout)
        main_layout.addWidget(general_group)
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QGridLayout()
        appearance_layout.setSpacing(10)
        appearance_layout.setContentsMargins(10, 15, 10, 10)
        
        # Theme selection
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        appearance_layout.addWidget(theme_label, 0, 0)
        appearance_layout.addWidget(self.theme_combo, 0, 1)
        
        appearance_group.setLayout(appearance_layout)
        main_layout.addWidget(appearance_group)
        
        # Reset button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.setProperty("class", "secondary")
        reset_button.clicked.connect(self.reset_to_defaults)
        main_layout.addWidget(reset_button)
        
        # Spacer
        main_layout.addStretch()
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.ok_clicked)
        button_box.rejected.connect(self.cancel_clicked)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
    
    def load_settings(self):
        """Load settings from config manager into UI."""
        # Load values with defaults
        auto_start = self.config_manager.get('auto_start', False)
        default_threshold = self.config_manager.get('default_threshold', 80)
        theme = self.config_manager.get('theme', 'dark')
        refresh_interval = self.config_manager.get('refresh_interval', 30)
        show_notifications = self.config_manager.get('show_notifications', True)
        
        # Update UI elements
        self.auto_start_checkbox.setChecked(auto_start)
        self.threshold_spinbox.setValue(default_threshold)
        self.theme_combo.setCurrentText(theme.title())
        self.refresh_interval_spinbox.setValue(refresh_interval)
        self.notifications_checkbox.setChecked(show_notifications)
    
    def save_settings(self):
        """Save settings from UI to config manager."""
        # Get values from UI
        auto_start = self.auto_start_checkbox.isChecked()
        default_threshold = self.threshold_spinbox.value()
        theme = self.theme_combo.currentText().lower()
        refresh_interval = self.refresh_interval_spinbox.value()
        show_notifications = self.notifications_checkbox.isChecked()
        
        # Validate threshold
        if not 20 <= default_threshold <= 100:
            raise ValueError("Threshold must be between 20 and 100")
        
        # Save to config manager
        self.config_manager.set('auto_start', auto_start)
        self.config_manager.set('default_threshold', default_threshold)
        self.config_manager.set('theme', theme)
        self.config_manager.set('refresh_interval', refresh_interval)
        self.config_manager.set('show_notifications', show_notifications)
        
        # Persist to file
        self.config_manager.save()
        
        # Emit settings changed signal directly
        self.settings_changed.emit()
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.config_manager.reset_to_defaults()
        self.config_manager.save()
        self.load_settings()
    
    def ok_clicked(self):
        """Handle OK button click."""
        try:
            # Save settings without emitting signal yet
            self._save_settings_without_signal()
            
            # Close dialog first
            self.accept()
            
            # Emit signal after dialog is closed to prevent Qt conflicts
            self.settings_changed.emit()
            
        except ValueError as e:
            # TODO: Show error message dialog
            print(f"Settings error: {e}")
    
    def _save_settings_without_signal(self):
        """Save settings to config manager without emitting signal."""
        # Get values from UI
        auto_start = self.auto_start_checkbox.isChecked()
        default_threshold = self.threshold_spinbox.value()
        theme = self.theme_combo.currentText().lower()
        refresh_interval = self.refresh_interval_spinbox.value()
        show_notifications = self.notifications_checkbox.isChecked()
        
        # Validate threshold
        if not 20 <= default_threshold <= 100:
            raise ValueError("Threshold must be between 20 and 100")
        
        # Save to config manager
        self.config_manager.set('auto_start', auto_start)
        self.config_manager.set('default_threshold', default_threshold)
        self.config_manager.set('theme', theme)
        self.config_manager.set('refresh_interval', refresh_interval)
        self.config_manager.set('show_notifications', show_notifications)
        
        # Persist to file
        self.config_manager.save()
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        # Reload settings to discard changes
        self.load_settings()
        self.reject()
    
    def on_theme_changed(self, theme_text: str):
        """Handle theme change for preview."""
        theme = theme_text.lower()
        
        if theme == 'light':
            # Use the proper light theme method
            self._apply_light_theme()
        else:
            # Reapply dark theme
            self._apply_dark_theme()