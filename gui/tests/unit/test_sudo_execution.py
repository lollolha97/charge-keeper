"""Test for sudo execution environment setup."""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

# Import the setup function
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from main import setup_qt_for_root


class TestSudoExecution:
    """Test cases for sudo execution environment setup."""
    
    def test_setup_qt_for_root_when_not_root(self):
        """Test that setup_qt_for_root does nothing when not running as root."""
        with patch('os.geteuid', return_value=1000):  # Non-root user
            # Should not modify environment
            original_env = dict(os.environ)
            setup_qt_for_root()
            # Environment should be unchanged
            assert dict(os.environ) == original_env
    
    @patch('pwd.getpwnam')
    @patch('os.makedirs')
    @patch('os.geteuid', return_value=0)  # Mock running as root
    def test_setup_qt_for_root_creates_runtime_dir(self, mock_geteuid, mock_makedirs, mock_getpwnam):
        """Test that setup_qt_for_root creates proper runtime directory."""
        # Mock environment
        with patch.dict(os.environ, {'SUDO_USER': 'sang'}, clear=True):
            mock_user = MagicMock()
            mock_user.pw_dir = '/home/sang'
            mock_getpwnam.return_value = mock_user
            
            setup_qt_for_root()
            
            # Should create runtime directory
            mock_makedirs.assert_called_with('/tmp/runtime-sang', mode=0o700, exist_ok=True)
            
            # Should set environment variables
            assert os.environ['XDG_RUNTIME_DIR'] == '/tmp/runtime-sang'
            assert os.environ['HOME'] == '/home/sang'
            assert os.environ['QT_X11_NO_MITSHM'] == '1'
            assert os.environ['QT_QUICK_BACKEND'] == 'software'
    
    @patch('os.makedirs')
    @patch('os.geteuid', return_value=0)
    def test_setup_qt_for_root_without_sudo_user(self, mock_geteuid, mock_makedirs):
        """Test setup when SUDO_USER is not available."""
        with patch.dict(os.environ, {}, clear=True):
            setup_qt_for_root()
            
            # Should still create runtime dir with 'root' as fallback
            mock_makedirs.assert_called_with('/tmp/runtime-root', mode=0o700, exist_ok=True)
            assert os.environ['XDG_RUNTIME_DIR'] == '/tmp/runtime-root'
    
    @patch('os.makedirs')
    @patch('os.geteuid', return_value=0)
    def test_setup_qt_for_root_with_existing_xdg_runtime_dir(self, mock_geteuid, mock_makedirs):
        """Test that existing XDG_RUNTIME_DIR is not overwritten."""
        existing_dir = '/existing/runtime/dir'
        with patch.dict(os.environ, {'XDG_RUNTIME_DIR': existing_dir}, clear=True):
            setup_qt_for_root()
            
            # Should not create new directory or change existing one
            mock_makedirs.assert_not_called()
            assert os.environ['XDG_RUNTIME_DIR'] == existing_dir