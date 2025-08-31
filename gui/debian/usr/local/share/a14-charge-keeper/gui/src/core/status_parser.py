"""CLI output parser for battery status information."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class BatteryStatus:
    """Battery status data structure."""
    device: str
    end_threshold: int
    start_threshold: Optional[int] = None
    backup_count: int = 0
    
    def __str__(self) -> str:
        """String representation of battery status."""
        return f"BatteryStatus(device={self.device}, end_threshold={self.end_threshold}%)"


class StatusParser:
    """Parser for CLI output from a14-charge-keeper status command."""
    
    # Regex patterns for parsing different fields
    DEVICE_PATTERN = re.compile(r'^Device\s*:\s*(.+)$')
    END_THRESHOLD_PATTERN = re.compile(r'충전 종료:\s*(\d+)%')
    START_THRESHOLD_PATTERN = re.compile(r'충전 시작:\s*(\d+)%')
    BACKUP_COUNT_PATTERN = re.compile(r'백업 파일:\s*(\d+)개')
    
    @staticmethod
    def parse_status(output: str) -> BatteryStatus:
        """Parse CLI status output into BatteryStatus object.
        
        Args:
            output: Raw output from 'a14-charge-keeper status' command
            
        Returns:
            BatteryStatus object with parsed information
            
        Raises:
            ValueError: If output format is invalid or incomplete
        """
        if not output or not output.strip():
            raise ValueError("Empty or invalid status output")
        
        lines = output.strip().split('\n')
        
        # Parse required fields
        device = StatusParser._extract_device(lines)
        end_threshold = StatusParser._extract_end_threshold(lines)
        
        # Parse optional fields
        start_threshold = StatusParser._extract_start_threshold(lines)
        backup_count = StatusParser._extract_backup_count(lines)
        
        return BatteryStatus(
            device=device,
            end_threshold=end_threshold,
            start_threshold=start_threshold,
            backup_count=backup_count
        )
    
    @staticmethod
    def _extract_device(lines: list[str]) -> str:
        """Extract device name from status output."""
        for line in lines:
            match = StatusParser.DEVICE_PATTERN.match(line.strip())
            if match:
                return match.group(1).strip()
        raise ValueError("Unable to parse device information")
    
    @staticmethod
    def _extract_end_threshold(lines: list[str]) -> int:
        """Extract end threshold from status output."""
        for line in lines:
            match = StatusParser.END_THRESHOLD_PATTERN.search(line)
            if match:
                return int(match.group(1))
        raise ValueError("Unable to parse threshold information")
    
    @staticmethod
    def _extract_start_threshold(lines: list[str]) -> Optional[int]:
        """Extract start threshold from status output (optional)."""
        for line in lines:
            match = StatusParser.START_THRESHOLD_PATTERN.search(line)
            if match:
                return int(match.group(1))
        return None
    
    @staticmethod
    def _extract_backup_count(lines: list[str]) -> int:
        """Extract backup file count from status output."""
        for line in lines:
            match = StatusParser.BACKUP_COUNT_PATTERN.search(line)
            if match:
                return int(match.group(1))
        return 0