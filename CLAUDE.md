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
- **System Tray Integration**: Persistent tray icon with right-click menu
- **Battery Threshold Control**: Interactive slider with +/- buttons
- **Settings Dialog**: Theme selection, refresh interval, notifications
- **Battery Details**: Real-time status display with Korean translations
- **PolicyKit Integration**: Automatic privilege escalation for threshold changes

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

### Debian Package
Built package available: `cli/a14-charge-keeper_0.3.0_all.deb`
- Installs to `/usr/local/bin/a14-charge-keeper`
- Includes dependencies: bash, upower, systemd
- Complete with postinst/postrm/prerm scripts

## Multi-Platform Support Notes

- **ASUS laptops**: Usually only `charge_control_end_threshold` supported
- **ThinkPad/Lenovo**: Often support both start and end thresholds  
- **Other brands**: Varies by model, use `check-support.sh` to verify
- All operations work through standard Linux kernel sysfs interfaces

## Development

**Note**: Development files (tests, dev documentation, additional icons) are maintained only in the `dev` branch. The `master` branch contains only production-ready code and assets for clean releases.