"""Configuration management for A14 Charge Keeper GUI."""

import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


class ConfigManager:
    """Manages application configuration with validation and persistence."""
    
    # Default configuration values
    DEFAULTS = {
        'auto_start': False,
        'default_threshold': 80,
        'theme': 'dark',
        'refresh_interval': 30,
        'show_notifications': True
    }
    
    # Validation rules
    VALIDATORS = {
        'default_threshold': lambda x: 20 <= x <= 100,
        'theme': lambda x: x in ['dark', 'light'],
        'refresh_interval': lambda x: 5 <= x <= 300,
        'auto_start': lambda x: isinstance(x, bool),
        'show_notifications': lambda x: isinstance(x, bool)
    }
    
    # Validation error messages
    ERROR_MESSAGES = {
        'default_threshold': "Threshold must be between 20 and 100",
        'theme': "Theme must be 'dark' or 'light'",
        'refresh_interval': "Refresh interval must be between 5 and 300",
        'auto_start': "Auto start must be a boolean value",
        'show_notifications': "Show notifications must be a boolean value"
    }
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_dir: Custom configuration directory (for testing)
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Use XDG config directory
            xdg_config = os.environ.get('XDG_CONFIG_HOME', 
                                       os.path.expanduser('~/.config'))
            self.config_dir = Path(xdg_config) / 'a14-charge-keeper'
        
        self.config_file = self.config_dir / 'config.json'
        self._config: Dict[str, Any] = self.DEFAULTS.copy()
        self._change_callbacks: List[Callable[[str, Any, Any], None]] = []
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value with validation.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Raises:
            ValueError: If value is invalid
        """
        # Validate value if validator exists
        if key in self.VALIDATORS:
            if not self.VALIDATORS[key](value):
                raise ValueError(self.ERROR_MESSAGES[key])
        
        # Store old value for callbacks
        old_value = self._config.get(key)
        
        # Set new value
        self._config[key] = value
        
        # Notify callbacks
        if old_value != value:
            self._notify_change(key, old_value, value)
    
    def save(self) -> None:
        """Save configuration to file.
        
        Raises:
            OSError: If file cannot be written
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except OSError as e:
            raise OSError(f"Failed to save configuration: {e}")
    
    def load(self) -> None:
        """Load configuration from file.
        
        If file is corrupted or doesn't exist, uses defaults.
        """
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file) as f:
                data = json.load(f)
            
            # Validate and merge loaded data
            for key, value in data.items():
                try:
                    if key in self.VALIDATORS:
                        if self.VALIDATORS[key](value):
                            self._config[key] = value
                    else:
                        # Allow unknown keys for future compatibility
                        self._config[key] = value
                except (TypeError, ValueError):
                    # Skip invalid values, keep defaults
                    continue
                    
        except (json.JSONDecodeError, OSError):
            # File is corrupted or unreadable, keep defaults
            pass
    
    def register_change_callback(self, callback: Callable[[str, Any, Any], None]) -> None:
        """Register callback for configuration changes.
        
        Args:
            callback: Function called with (key, old_value, new_value)
        """
        self._change_callbacks.append(callback)
    
    def _notify_change(self, key: str, old_value: Any, new_value: Any) -> None:
        """Notify all registered callbacks of configuration change.
        
        Args:
            key: Changed configuration key
            old_value: Previous value
            new_value: New value
        """
        for callback in self._change_callbacks:
            try:
                callback(key, old_value, new_value)
            except Exception:
                # Don't let callback errors break configuration
                pass
    
    def reset_to_defaults(self) -> None:
        """Reset all configuration to default values."""
        old_config = self._config.copy()
        self._config = self.DEFAULTS.copy()
        
        # Notify callbacks for all changed values
        for key in set(old_config.keys()) | set(self._config.keys()):
            old_val = old_config.get(key)
            new_val = self._config.get(key)
            if old_val != new_val:
                self._notify_change(key, old_val, new_val)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values.
        
        Returns:
            Copy of current configuration
        """
        return self._config.copy()