"""CLI interface for communicating with a14-charge-keeper command."""

import os
import subprocess
from dataclasses import dataclass
from typing import Optional, Any
from src.core.status_parser import StatusParser, BatteryStatus


@dataclass
class CliResult:
    """Result from CLI command execution."""
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    
    @classmethod
    def success(cls, data: Any = None) -> 'CliResult':
        """Create successful result."""
        return cls(success=True, data=data)
    
    @classmethod  
    def error(cls, message: str) -> 'CliResult':
        """Create error result."""
        return cls(success=False, error_message=message)
    
    def __str__(self) -> str:
        """String representation of result."""
        if self.success:
            return f"SUCCESS: {self.data}"
        else:
            return f"ERROR: {self.error_message}"


class CliInterface:
    """Interface for communicating with a14-charge-keeper CLI tool."""
    
    CLI_COMMAND = 'a14-charge-keeper'
    TIMEOUT_SECONDS = 30
    
    def get_status(self) -> CliResult:
        """Get current battery status from CLI.
        
        Returns:
            CliResult with BatteryStatus data on success
        """
        try:
            result = subprocess.run(
                [self.CLI_COMMAND, 'status'],
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() or "Unknown CLI error"
                return CliResult.error(error_msg)
            
            # Parse the output
            battery_status = StatusParser.parse_status(result.stdout)
            return CliResult.success(battery_status)
            
        except FileNotFoundError:
            return CliResult.error("a14-charge-keeper not found. Please install the CLI tool first.")
        except subprocess.TimeoutExpired:
            return CliResult.error("Command timed out after 30 seconds")
        except ValueError as e:
            return CliResult.error(f"Failed to parse CLI output: {e}")
        except Exception as e:
            return CliResult.error(f"Unexpected error: {e}")
    
    def set_threshold(self, threshold: int) -> CliResult:
        """Set battery charge threshold.
        
        Args:
            threshold: Threshold percentage (20-100)
            
        Returns:
            CliResult indicating success or failure
        """
        if not self._validate_threshold(threshold):
            return CliResult.error("Threshold must be between 20 and 100")
        
        return self._execute_sudo_command(['set', str(threshold)])
    
    def persist_threshold(self, threshold: int) -> CliResult:
        """Set persistent battery charge threshold.
        
        Args:
            threshold: Threshold percentage (20-100)
            
        Returns:
            CliResult indicating success or failure
        """
        if not self._validate_threshold(threshold):
            return CliResult.error("Threshold must be between 20 and 100")
        
        return self._execute_sudo_command(['persist', str(threshold)])
    
    def clear_threshold(self) -> CliResult:
        """Clear battery charge threshold (reset to 100%).
        
        Returns:
            CliResult indicating success or failure
        """
        return self._execute_sudo_command(['clear'])
    
    def _validate_threshold(self, threshold: int) -> bool:
        """Validate threshold value range.
        
        Args:
            threshold: Threshold value to validate
            
        Returns:
            True if valid, False otherwise
        """
        return isinstance(threshold, int) and 20 <= threshold <= 100
    
    def _execute_sudo_command(self, args: list[str]) -> CliResult:
        """Execute CLI command directly (assuming app is run with sudo).
        
        Args:
            args: Command arguments (without CLI command name)
            
        Returns:
            CliResult indicating success or failure
        """
        try:
            # Since app is run with sudo, execute command directly
            cmd = [self.CLI_COMMAND] + args
            
            print(f"Executing: {' '.join(cmd)}")  # Debug print
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS
            )
            
            print(f"Return code: {result.returncode}")  # Debug print
            if result.stdout:
                print(f"Stdout: {result.stdout}")  # Debug print
            if result.stderr:
                print(f"Stderr: {result.stderr}")  # Debug print
            
            if result.returncode == 0:
                return CliResult.success()
            else:
                error_msg = result.stderr.strip() or "명령 실행에 실패했습니다."
                return CliResult.error(f"오류: {error_msg}")
                    
        except subprocess.TimeoutExpired:
            return CliResult.error("명령 실행 시간이 초과되었습니다.")
        except FileNotFoundError:
            return CliResult.error(f"{self.CLI_COMMAND}을 찾을 수 없습니다.")
        except Exception as e:
            return CliResult.error(f"예상치 못한 오류: {e}")