"""Tests for ConfigManager - TDD approach."""

import pytest
import tempfile
import os
from pathlib import Path

from src.core.config_manager import ConfigManager


class TestConfigManager:
    """Test cases for configuration management."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_default_values(self, temp_config_dir):
        """Test that default values are properly set."""
        config = ConfigManager(config_dir=temp_config_dir)
        
        # Test default values as specified in TDD plan
        assert config.get('auto_start') is False
        assert config.get('default_threshold') == 80
        assert config.get('theme') == 'dark'
        assert config.get('refresh_interval') == 30
        assert config.get('show_notifications') is True
    
    def test_save_and_load_settings(self, temp_config_dir):
        """Test saving and loading settings."""
        # Create and configure manager
        config = ConfigManager(config_dir=temp_config_dir)
        config.set('auto_start', True)
        config.set('default_threshold', 70)
        config.set('theme', 'light')
        config.save()
        
        # Create new manager and load
        new_config = ConfigManager(config_dir=temp_config_dir)
        new_config.load()
        
        # Verify loaded values
        assert new_config.get('auto_start') is True
        assert new_config.get('default_threshold') == 70
        assert new_config.get('theme') == 'light'
        # Default values should remain
        assert new_config.get('refresh_interval') == 30
    
    def test_invalid_config_values(self, temp_config_dir):
        """Test validation of configuration values."""
        config = ConfigManager(config_dir=temp_config_dir)
        
        # Invalid threshold values
        with pytest.raises(ValueError, match="Threshold must be between 20 and 100"):
            config.set('default_threshold', 15)
        
        with pytest.raises(ValueError, match="Threshold must be between 20 and 100"):
            config.set('default_threshold', 105)
        
        # Invalid theme
        with pytest.raises(ValueError, match="Theme must be 'dark' or 'light'"):
            config.set('theme', 'rainbow')
        
        # Invalid refresh interval
        with pytest.raises(ValueError, match="Refresh interval must be between 5 and 300"):
            config.set('refresh_interval', 2)
    
    def test_config_file_persistence(self, temp_config_dir):
        """Test that config file is actually created and persisted."""
        config = ConfigManager(config_dir=temp_config_dir)
        config.set('auto_start', True)
        config.save()
        
        # Check that config file exists
        config_file = Path(temp_config_dir) / 'config.json'
        assert config_file.exists()
        
        # Check file content structure
        import json
        with open(config_file) as f:
            data = json.load(f)
            assert 'auto_start' in data
            assert data['auto_start'] is True
    
    def test_corrupted_config_file_recovery(self, temp_config_dir):
        """Test recovery from corrupted config file."""
        # Create corrupted config file
        config_file = Path(temp_config_dir) / 'config.json'
        with open(config_file, 'w') as f:
            f.write('invalid json content')
        
        # Manager should handle this gracefully and use defaults
        config = ConfigManager(config_dir=temp_config_dir)
        config.load()
        
        # Should have default values
        assert config.get('auto_start') is False
        assert config.get('default_threshold') == 80
    
    def test_config_change_notifications(self, temp_config_dir):
        """Test configuration change notifications."""
        config = ConfigManager(config_dir=temp_config_dir)
        
        # Track callback invocations
        callback_calls = []
        
        def config_changed(key, old_value, new_value):
            callback_calls.append((key, old_value, new_value))
        
        config.register_change_callback(config_changed)
        
        # Make changes
        config.set('auto_start', True)
        config.set('default_threshold', 70)
        
        # Verify callbacks were called
        assert len(callback_calls) == 2
        assert ('auto_start', False, True) in callback_calls
        assert ('default_threshold', 80, 70) in callback_calls
    
    def test_get_nonexistent_key(self, temp_config_dir):
        """Test behavior when getting non-existent configuration key."""
        config = ConfigManager(config_dir=temp_config_dir)
        
        # Should return None for non-existent keys
        assert config.get('nonexistent_key') is None
        
        # Should return default value when provided
        assert config.get('nonexistent_key', 'default_value') == 'default_value'