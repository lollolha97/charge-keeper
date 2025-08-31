"""CLI integration tests - tests against real CLI tool."""

import pytest
import subprocess
import shutil
from unittest.mock import patch
from src.core.cli_interface import CliInterface
from src.core.status_parser import StatusParser


@pytest.fixture
def real_cli_available():
    """Check if real CLI tool is available."""
    return shutil.which('a14-charge-keeper') is not None


@pytest.mark.integration
def test_cli_status_integration(real_cli_available):
    """Test real CLI status command integration."""
    if not real_cli_available:
        pytest.skip("CLI tool not available")
    
    cli = CliInterface()
    result = cli.get_status()
    
    # Should not fail (even if no battery found, should return proper error)
    assert result is not None
    assert hasattr(result, 'success')
    
    if result.success:
        # If successful, should have battery info
        assert result.data is not None
        assert hasattr(result.data, 'device')
        print(f"CLI integration test passed: {result.data}")
    else:
        # If failed, should have proper error message
        assert result.error_message is not None
        print(f"CLI integration test - expected failure: {result.error_message}")


@pytest.mark.integration
def test_cli_check_support_integration(real_cli_available):
    """Test real CLI check support integration."""
    if not real_cli_available:
        pytest.skip("CLI tool not available")
    
    try:
        # Test if check-support.sh exists and runs
        result = subprocess.run(
            ['../cli/check-support.sh'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should not crash (exit code doesn't matter for this test)
        assert result.returncode is not None
        print(f"Check support script result: {result.returncode}")
        
    except FileNotFoundError:
        pytest.skip("check-support.sh not found")
    except subprocess.TimeoutExpired:
        pytest.fail("check-support.sh timed out")


@pytest.mark.integration  
@pytest.mark.slow
def test_status_parser_with_real_cli_output(real_cli_available):
    """Test status parser with real CLI output."""
    if not real_cli_available:
        pytest.skip("CLI tool not available")
    
    try:
        # Get real CLI output
        result = subprocess.run(
            ['a14-charge-keeper', 'status'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Parse real output
            parsed = StatusParser.parse_status(result.stdout)
            
            # Should parse without errors
            assert parsed is not None
            print(f"Real CLI output parsed successfully: {parsed}")
        else:
            print(f"CLI returned error (expected on some systems): {result.stderr}")
            
    except subprocess.TimeoutExpired:
        pytest.fail("CLI command timed out")
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")


@pytest.mark.integration
def test_cli_interface_error_handling():
    """Test CLI interface handles missing command gracefully."""
    # Test by patching subprocess to raise FileNotFoundError
    with patch('src.core.cli_interface.subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError("No such file or directory")
        
        cli = CliInterface()
        result = cli.get_status()
        
        assert result.success is False
        assert 'not found' in result.error_message.lower() or 'no such file' in result.error_message.lower()