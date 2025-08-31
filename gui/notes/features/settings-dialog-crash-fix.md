# Settings Dialog Crash Fix

## Problem
The settings dialog was causing segmentation faults when:
1. Running the GUI as root (with sudo)
2. Clicking "OK" button after changing settings
3. Signal emission and dialog closing happened simultaneously

## Root Cause
Qt applications should not be run as root because:
- Qt's signal/slot mechanism has threading issues when running as root
- XDG_RUNTIME_DIR environment issues cause Qt instability
- Rapid signal emission + dialog.accept() creates race conditions

## Solution Implemented

### 1. Separated Signal Emission from Dialog Closing
- Modified `ok_clicked()` to save settings first, close dialog, then emit signal
- Created `_save_settings_without_signal()` method for safe saving
- Signal emission happens after dialog is safely closed

### 2. Made System Tray Signal Handling More Robust
- Added delays in `_on_settings_changed()` using QTimer.singleShot(100, ...)
- Improved error handling in timer restart operations
- Made timer creation more defensive

### 3. Test Coverage
- Created comprehensive tests to reproduce and verify fixes
- Tests cover isolated dialog, system tray integration, and signal timing
- All tests pass confirming the fixes work

## Usage Recommendation
**DO NOT run the GUI as root**. Instead:
```bash
# Correct way - run GUI as regular user
python3 main.py

# The GUI will prompt for sudo when needed for battery control
# OR configure sudoers to allow battery control without password
```

## Files Modified
- `src/gui/settings_dialog.py`: Separated signal emission from dialog closing
- `src/gui/system_tray.py`: Made signal handling more robust with delays
- `tests/unit/test_settings_dialog_crash.py`: Added comprehensive test coverage

## Test Results
All tests pass, confirming the segmentation fault is fixed:
- Settings dialog works without crashes
- System tray integration is stable
- Signal timing is safe and predictable