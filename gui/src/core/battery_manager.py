"""Battery manager for handling business logic and state management."""

import re
import time
from dataclasses import dataclass
from typing import Optional, Callable, Any, Dict
from src.core.cli_interface import CliInterface, CliResult
from src.core.status_parser import StatusParser


@dataclass
class BatteryInfo:
    """Extended battery information including hardware and power details."""
    
    # Basic threshold info
    device: str
    end_threshold: int
    start_threshold: Optional[int] = None
    backup_count: int = 0
    
    # Hardware info
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial: Optional[str] = None
    
    # Power status
    state: Optional[str] = None  # charging, discharging, not charging, etc.
    percentage: Optional[int] = None
    energy_current: Optional[float] = None  # Wh
    energy_full: Optional[float] = None  # Wh
    energy_full_design: Optional[float] = None  # Wh
    energy_rate: Optional[float] = None  # W
    voltage: Optional[float] = None  # V
    capacity: Optional[float] = None  # %
    charge_cycles: Optional[int] = None
    
    # Time estimates
    time_to_empty: Optional[str] = None
    time_to_full: Optional[str] = None
    
    @classmethod
    def from_cli_output(cls, output: str) -> 'BatteryInfo':
        """Create BatteryInfo from CLI status output.
        
        Args:
            output: Raw CLI output containing battery information
            
        Returns:
            BatteryInfo object with parsed data
        """
        # Parse basic status first
        basic_status = StatusParser.parse_status(output)
        
        # Create base info from basic status
        info = cls(
            device=basic_status.device,
            end_threshold=basic_status.end_threshold,
            start_threshold=basic_status.start_threshold,
            backup_count=basic_status.backup_count
        )
        
        # Parse extended information from upower output
        lines = output.split('\n')
        
        # Hardware info patterns
        info.vendor = cls._extract_field(lines, r'vendor:\s*(.+)')
        info.model = cls._extract_field(lines, r'model:\s*(.+)')
        info.serial = cls._extract_field(lines, r'serial:\s*(.+)')
        
        # Power status patterns
        info.state = cls._extract_field(lines, r'state:\s*(.+)')
        
        percentage_str = cls._extract_field(lines, r'percentage:\s*(\d+)%')
        info.percentage = int(percentage_str) if percentage_str else None
        
        energy_current_str = cls._extract_field(lines, r'energy:\s*([\d.]+)\s*Wh')
        info.energy_current = float(energy_current_str) if energy_current_str else None
        
        energy_full_str = cls._extract_field(lines, r'energy-full:\s*([\d.]+)\s*Wh')
        info.energy_full = float(energy_full_str) if energy_full_str else None
        
        energy_design_str = cls._extract_field(lines, r'energy-full-design:\s*([\d.]+)\s*Wh')
        info.energy_full_design = float(energy_design_str) if energy_design_str else None
        
        energy_rate_str = cls._extract_field(lines, r'energy-rate:\s*([\d.]+)\s*W')
        info.energy_rate = float(energy_rate_str) if energy_rate_str else None
        
        voltage_str = cls._extract_field(lines, r'voltage:\s*([\d.]+)\s*V')
        info.voltage = float(voltage_str) if voltage_str else None
        
        capacity_str = cls._extract_field(lines, r'capacity:\s*([\d.]+)%')
        info.capacity = float(capacity_str) if capacity_str else None
        
        cycles_str = cls._extract_field(lines, r'charge-cycles:\s*(\d+)')
        info.charge_cycles = int(cycles_str) if cycles_str and cycles_str != "N/A" else None
        
        # Time estimates
        info.time_to_empty = cls._extract_field(lines, r'time to empty:\s*(.+)')
        info.time_to_full = cls._extract_field(lines, r'time to full:\s*(.+)')
        
        return info
    
    @staticmethod
    def _extract_field(lines: list, pattern: str) -> Optional[str]:
        """Extract field using regex pattern from lines.
        
        Args:
            lines: List of output lines to search
            pattern: Regex pattern to match
            
        Returns:
            Matched value or None
        """
        compiled_pattern = re.compile(pattern)
        for line in lines:
            match = compiled_pattern.search(line.strip())
            if match:
                return match.group(1).strip()
        return None
    
    @property
    def health_percentage(self) -> Optional[float]:
        """Calculate battery health percentage.
        
        Returns:
            Health percentage based on energy_full vs energy_full_design
        """
        if self.energy_full and self.energy_full_design:
            return (self.energy_full / self.energy_full_design) * 100
        return None
    
    def __str__(self) -> str:
        """String representation of battery info."""
        return f"BatteryInfo(device={self.device}, threshold={self.end_threshold}%, state={self.state})"


@dataclass
class BatteryEvent:
    """Battery status change event."""
    event_type: str
    data: Dict[str, Any]
    timestamp: float = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def __str__(self) -> str:
        """String representation of event."""
        return f"BatteryEvent(type={self.event_type}, data={self.data})"


class BatteryManager:
    """Business logic manager for battery operations and state management."""
    
    def __init__(self, cli_interface: Optional[CliInterface] = None):
        """Initialize battery manager.
        
        Args:
            cli_interface: CLI interface instance (creates new if None)
        """
        self.cli_interface = cli_interface or CliInterface()
        self.current_info: Optional[BatteryInfo] = None
        self.is_initialized = False
        self.auto_refresh_enabled = False
        self._event_callbacks: list[Callable[[BatteryEvent], None]] = []
    
    def initialize(self) -> CliResult:
        """Initialize battery manager by fetching current status.
        
        Returns:
            CliResult indicating initialization success or failure
        """
        result = self.cli_interface.get_status()
        
        if not result.success:
            return CliResult.error(f"Failed to initialize: {result.error_message}")
        
        # Convert to extended battery info
        try:
            self.current_info = self._create_battery_info_from_result(result)
            self.is_initialized = True
            return CliResult.success()
        except Exception as e:
            return CliResult.error(f"Failed to process battery info: {e}")
    
    def refresh_status(self) -> CliResult:
        """Refresh current battery status from CLI.
        
        Returns:
            CliResult indicating refresh success or failure
        """
        if not self.is_initialized:
            return CliResult.error("Manager not initialized")
        
        result = self.cli_interface.get_status()
        
        if not result.success:
            return CliResult.error(f"Failed to refresh status: {result.error_message}")
        
        # Store old values for change detection
        old_threshold = self.current_info.end_threshold if self.current_info else None
        
        # Update current info
        self.current_info = self._create_battery_info_from_result(result)
        
        # Trigger events for changes
        if old_threshold and old_threshold != self.current_info.end_threshold:
            self._trigger_event(BatteryEvent(
                event_type="threshold_changed",
                data={
                    "old_threshold": old_threshold,
                    "new_threshold": self.current_info.end_threshold
                }
            ))
        
        return CliResult.success()
    
    def set_threshold(self, threshold: int) -> CliResult:
        """Set battery charge threshold with validation.
        
        Args:
            threshold: Threshold percentage (20-100)
            
        Returns:
            CliResult indicating success or failure
        """
        if not self.is_initialized:
            return CliResult.error("Manager not initialized")
        
        if not isinstance(threshold, int) or threshold < 20 or threshold > 100:
            return CliResult.error("Threshold must be between 20 and 100")
        
        result = self.cli_interface.set_threshold(threshold)
        
        if result.success:
            # Refresh status to get updated information
            self.refresh_status()
        
        return result
    
    def persist_threshold(self, threshold: int) -> CliResult:
        """Set persistent battery charge threshold.
        
        Args:
            threshold: Threshold percentage (20-100)
            
        Returns:
            CliResult indicating success or failure
        """
        if not self.is_initialized:
            return CliResult.error("Manager not initialized")
        
        if not isinstance(threshold, int) or threshold < 20 or threshold > 100:
            return CliResult.error("Threshold must be between 20 and 100")
        
        result = self.cli_interface.persist_threshold(threshold)
        
        if result.success:
            # Refresh status to get updated information
            self.refresh_status()
        
        return result
    
    def clear_threshold(self) -> CliResult:
        """Clear battery charge threshold (reset to 100%).
        
        Returns:
            CliResult indicating success or failure
        """
        if not self.is_initialized:
            return CliResult.error("Manager not initialized")
        
        result = self.cli_interface.clear_threshold()
        
        if result.success:
            # Refresh status to get updated information
            self.refresh_status()
        
        return result
    
    def register_event_callback(self, callback: Callable[[BatteryEvent], None]) -> None:
        """Register callback for battery events.
        
        Args:
            callback: Function to call when battery events occur
        """
        self._event_callbacks.append(callback)
    
    def enable_auto_refresh(self, interval_seconds: int = 30) -> None:
        """Enable automatic status refresh.
        
        Args:
            interval_seconds: Refresh interval in seconds
        """
        self.auto_refresh_enabled = True
        # TODO: Implement actual timer-based refresh in future
    
    def disable_auto_refresh(self) -> None:
        """Disable automatic status refresh."""
        self.auto_refresh_enabled = False
    
    def _create_battery_info_from_result(self, result: CliResult) -> BatteryInfo:
        """Create BatteryInfo from CLI result.
        
        Args:
            result: Successful CliResult with battery status data
            
        Returns:
            BatteryInfo object with basic information
        """
        # For now, create basic info from parsed status
        # In future, we could pass the full CLI output to BatteryInfo.from_cli_output()
        return BatteryInfo(
            device=result.data.device,
            end_threshold=result.data.end_threshold,
            start_threshold=result.data.start_threshold,
            backup_count=result.data.backup_count
        )
    
    def _trigger_event(self, event: BatteryEvent) -> None:
        """Trigger event to all registered callbacks.
        
        Args:
            event: Battery event to trigger
        """
        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception as e:
                # Log error but don't fail other callbacks
                print(f"Error in event callback: {e}")