# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Important** : Upadte Update.md wheh finished the major update.

## Project Overview

This is a lightweight shell script project for ASUS TUF A14 battery charge threshold management on Ubuntu 24.04 LTS. The project uses kernel sysfs interfaces (`/sys/class/power_supply/*/charge_control_end_threshold`) to limit battery charging without external dependencies.

## Architecture

- **Single Bash script**: `/usr/local/bin/a14-charge-keeper` - Main CLI tool with commands: set, status, persist, clear, uninstall
- **systemd integration**: oneshot service for boot-time threshold application
- **system-sleep hooks**: automatically reapplies thresholds after suspend/resume
- **Target device**: `/sys/class/power_supply/BAT0/charge_control_end_threshold` (configurable via BAT_NAME env var)

## Key Components

The main script (`a14-charge-keeper`) provides:
- `set <20-100>`: One-time threshold setting
- `persist <20-100>`: Permanent threshold with auto-reapply on boot/resume
- `status`: Display current thresholds and battery info
- `clear`: Reset to 100% and disable auto-reapply
- `uninstall`: Complete removal

## Development Notes

- All functionality is contained in a single Bash script embedded in PLAN.md
- Uses `set -euo pipefail` for strict error handling
- Requires root privileges for sysfs modifications
- Input validation restricts values to 20-100 range
- Environment variable `BAT_NAME` allows different battery device names
- Korean documentation and user interface

## Testing Commands

Since this is a system-level utility:
- Test sysfs file existence: `[ -e /sys/class/power_supply/BAT0/charge_control_end_threshold ]`
- Check current threshold: `cat /sys/class/power_supply/BAT0/charge_control_end_threshold`
- Verify systemd service: `systemctl status a14-charge-keeper.service`
- Check sleep hook: `ls -la /lib/systemd/system-sleep/a14-charge-keeper`

## Safety Constraints

- Only works with supported hardware (ASUS TUF A14 with sysfs battery control)
- Validates input range (20-100%) to prevent invalid values
- Uses read-only kernel interfaces for status checking
- Requires explicit root permission for modifications