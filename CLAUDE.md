# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Important**: Update Update.md when finished with major updates.

## Project Overview

This is a lightweight shell script project for Linux laptop battery charge threshold management. Originally designed for ASUS TUF A14 on Ubuntu 24.04 LTS, it now supports any Linux laptop with kernel sysfs battery control interfaces (`/sys/class/power_supply/*/charge_control_*_threshold`).

## Architecture

### Core Components
- **Main CLI**: `cli/a14-charge-keeper` - Full-featured Bash script with backup/rollback, verification, and lock mechanisms
- **Support checker**: `cli/check-support.sh` - Hardware compatibility verification tool
- **systemd integration**: oneshot service for boot-time threshold application
- **system-sleep hooks**: automatically reapplies thresholds after suspend/resume
- **Debian packaging**: Complete .deb package structure in `cli/debian/`

### Key Features
- Multi-brand laptop support (ASUS, ThinkPad/Lenovo via BAT_NAME env var)
- Safe operations with backup/rollback on failure
- Conflict detection (TLP, asusctl)
- Process locking to prevent concurrent modifications
- Extensive logging and verification

## Commands

### Testing Hardware Support
```bash
./cli/check-support.sh  # Check if your laptop supports battery threshold control
```

### Main CLI Commands (requires sudo for modifications)
```bash
# Check current status and battery info
a14-charge-keeper status

# Set threshold (one-time, lost on reboot/resume)
sudo a14-charge-keeper set 80

# Set threshold with persistent auto-reapply
sudo a14-charge-keeper persist 80

# Clear threshold to 100% and disable auto-reapply  
sudo a14-charge-keeper clear

# Verify current sysfs value matches expected
a14-charge-keeper verify 80

# Complete removal
sudo a14-charge-keeper uninstall
```

### Environment Variables
- `BAT_NAME`: Override battery device name (default: BAT0, common alternatives: BAT1, BATT)

## Development Architecture

### Script Structure (cli/a14-charge-keeper)
- **Validation layer**: Input validation, hardware support checking, conflict detection
- **Safety layer**: Process locking, backup/restore, verification with retries
- **Operation layer**: Core sysfs file manipulation
- **Persistence layer**: systemd service and sleep hook management

### Key Safety Mechanisms
- Process locking (`/var/lock/a14-charge-keeper.lock`) prevents concurrent runs
- Automatic backup before changes (`/var/lib/a14-charge-keeper/threshold_backup_*`)
- Rollback on verification failure
- Hardware conflict warnings (TLP, asusctl)
- Input validation (20-100% range only)

## GUI Application

### Installation
```bash
# Install GUI package (requires CLI package as dependency)
sudo dpkg -i gui/a14-charge-keeper-gui_1.0.0_all.deb

# Launch from applications menu or command line
a14-charge-keeper-gui
```

### GUI Features
- **System Tray Integration**: Persistent tray icon with charge-keeper.png icon, right-click menu
- **Battery Threshold Control**: Interactive slider with +/- buttons, fixed popup interaction issues
- **Settings Dialog**: Theme selection (Dark/Light/Auto), refresh interval (5-300s), notifications
- **Battery Details**: Real-time status display with comprehensive battery information
- **PolicyKit Integration**: Secure privilege escalation for threshold changes
- **Performance Optimized**: ~145MB memory, 0% idle CPU usage, minimal battery impact
- **Event Handling**: Robust Qt event system with focus management and signal blocking
- **Theme System**: Full dark/light theme support with system integration

## Testing Commands

### Hardware Testing
```bash
# Check if threshold control files exist
[ -e /sys/class/power_supply/BAT0/charge_control_end_threshold ] && echo "Supported"

# Manual threshold test (requires root)
sudo sh -c 'echo 80 > /sys/class/power_supply/BAT0/charge_control_end_threshold'
cat /sys/class/power_supply/BAT0/charge_control_end_threshold
```

### Service Testing
```bash
# Check systemd service status
systemctl status a14-charge-keeper.service

# Check sleep hook
ls -la /lib/systemd/system-sleep/a14-charge-keeper

# View logs
journalctl -u a14-charge-keeper.service
```

## Packaging

### Debian Packages
**CLI Package**: `cli/a14-charge-keeper_0.3.0_all.deb`
- Installs to `/usr/local/bin/a14-charge-keeper`
- Includes dependencies: bash, upower, systemd
- Complete with postinst/postrm/prerm scripts

**GUI Package**: `gui/a14-charge-keeper-gui_1.0.0_all.deb`
- Installs to `/usr/local/share/a14-charge-keeper/gui/`
- Desktop integration with applications menu entry
- PolicyKit policy for secure privilege escalation
- Icon theme integration (hicolor theme)
- Dependencies: python3, python3-pyqt5, policykit-1, CLI package
- Complete packaging with desktop files, icon installation, policy setup

## Multi-Platform Support Notes

- **ASUS laptops**: Usually only `charge_control_end_threshold` supported
- **ThinkPad/Lenovo**: Often support both start and end thresholds  
- **Other brands**: Varies by model, use `check-support.sh` to verify
- All operations work through standard Linux kernel sysfs interfaces

## Development

**Note**: Development files (tests, dev documentation, additional icons) are maintained only in the `dev` branch. The `master` branch contains only production-ready code and assets for clean releases.

### Recent Major Improvements

#### GUI Application Completion (2025-08-31)
- **System Tray Icon Issues**: Fixed persistent gear/cog icon display, now properly shows charge-keeper.png
- **Slider Interaction Fixes**: Resolved critical issues where clicking slider caused popup closure and mouse tracking problems
- **Event Handling**: Implemented comprehensive Qt event management with focus handling and signal blocking
- **Performance Analysis**: Documented excellent resource efficiency (0% CPU idle, 145MB memory)
- **Professional Packaging**: Complete Debian packaging with PolicyKit integration and desktop integration

#### Architecture Improvements
- **Event System**: Added robust eventFilter with QWindow type checking
- **Signal Management**: Implemented signal blocking for threshold adjustments
- **Focus Management**: Smart focus handling to prevent unwanted popup closure
- **Mouse State**: Proper mouse tracking state cleanup on dialog show/hide events

#### Project Structure Cleanup
- **Clean Master Branch**: Removed all development/test files from production branch
- **Debian Packaging**: Professional packaging structure for both CLI and GUI
- **Documentation**: Comprehensive performance analysis and user guides

### TDD Development Completed
- **5-Phase TDD Methodology**: Complete test-driven development approach
- **Unit Tests**: 15 comprehensive unit tests covering all core components  
- **Integration Tests**: 10 integration tests for CLI communication and end-to-end workflows
- **High Test Coverage**: Extensive mocking and test fixtures for reliable testing
- **Quality Assurance**: Red-Green-Refactor cycles ensuring robust codebase