# TUF Charge Keeper

<div align="center">

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Linux-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-yellow.svg)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-orange.svg)
![Tests](https://img.shields.io/badge/Tests-25%20Passing-brightgreen.svg)
![Performance](https://img.shields.io/badge/Memory-145MB-blue.svg)
![CPU](https://img.shields.io/badge/CPU-0%25%20Idle-green.svg)

**A production-ready Linux battery charge threshold management tool with modern GUI and robust CLI**

*Originally designed for ASUS TUF A14 on Ubuntu 24.04 LTS, now supports any Linux laptop with kernel sysfs battery control interfaces*

</div>

---

## 🛠️ Tech Stack

### **Core Technologies**
<div align="center">

| Component | Technology | Purpose |
|-----------|------------|---------|
| 🖥️ **GUI Framework** | **PyQt5** | Modern desktop interface with native Linux integration |
| 🔧 **CLI Backend** | **Bash 5.0+** | Rock-solid POSIX-compliant shell scripting |
| 🗄️ **System Integration** | **systemd** | Boot-time services and sleep/wake event handling |
| 🔐 **Security** | **PolicyKit** | Secure privilege escalation for system modifications |
| 📦 **Packaging** | **Debian/dpkg** | Professional Linux distribution packages |
| 🧪 **Testing** | **pytest + TDD** | 25 tests with comprehensive mocking framework |

</div>

### **Architecture & Design Patterns**
- **🎯 MVC Architecture**: Clear separation of GUI, business logic, and data layers
- **🔄 Event-Driven Design**: Robust Qt signal/slot system with custom event filtering
- **🛡️ Defensive Programming**: Extensive error handling, input validation, and rollback mechanisms  
- **📊 Performance-First**: Optimized for minimal resource usage (145MB RAM, 0% idle CPU)
- **🎨 Theme System**: Dynamic light/dark themes with system integration
- **🔒 Security-by-Design**: Process locking, backup/restore, and safe sysfs operations

### **Linux System Integration**
- **🐧 Kernel sysfs Interface**: Direct `/sys/class/power_supply/` manipulation
- **⚡ systemd Services**: Oneshot services for boot-time threshold application
- **😴 Sleep Hook Integration**: Automatic threshold reapplication after suspend/resume
- **🔧 PolicyKit Policies**: Secure GUI privilege escalation without sudo prompts
- **🎭 Desktop Integration**: FreeDesktop.org compliant with hicolor icon theme
- **📱 System Tray**: Native Qt system tray with real-time battery status

### **Development Methodology**
- **🔴🟢🔵 Test-Driven Development (TDD)**: 5-phase methodology with Red-Green-Refactor cycles
- **🧪 Comprehensive Testing**: Unit tests, integration tests, and E2E workflows
- **🎭 Mock-Based Testing**: subprocess and Qt component mocking for reliable CI/CD
- **📈 Performance Monitoring**: Real-time resource usage analysis and documentation
- **📚 Documentation-Driven**: Comprehensive user guides and developer documentation

---

## Features

### 🖥️ GUI Application (PyQt5)
- **System Tray Integration**: Real-time battery status with dynamic icons
- **Interactive Threshold Control**: Intuitive slider and button controls
- **Detailed Battery Information**: Comprehensive battery statistics and health data
- **Theme Support**: Dark/Light themes with system integration
- **Settings Management**: Configurable refresh intervals, auto-start, notifications
- **PolicyKit Integration**: Secure privilege escalation for system modifications

### 💻 CLI Tool
- **Multi-brand Support**: Works with ASUS, ThinkPad, Lenovo, and other Linux laptops
- **Safe Operations**: Backup/rollback system with verification
- **Persistent Settings**: Automatic reapplication after boot/resume
- **Conflict Detection**: Warns about TLP, asusctl conflicts
- **Hardware Verification**: Built-in compatibility checker

## Quick Start

### Check Hardware Support
```bash
./cli/check-support.sh
```

### Install GUI Application (Recommended)
```bash
# Install GUI package (includes CLI as dependency)
sudo dpkg -i gui/a14-charge-keeper-gui_1.0.0_all.deb

# Launch from applications menu or command line
a14-charge-keeper-gui
```

### Install CLI Only
```bash
# Install CLI package
sudo dpkg -i cli/a14-charge-keeper_0.3.0_all.deb

# Basic usage
a14-charge-keeper status              # Check current status
sudo a14-charge-keeper set 80         # Set threshold to 80%
sudo a14-charge-keeper persist 80     # Set and make persistent
```

## Supported Hardware

### Tested Devices
- **ASUS TUF Gaming A14** (FA401) - Ubuntu 24.04 LTS ✅
- **ASUS TUF A15/A17** series (via community reports) ✅
- **ThinkPad/Lenovo** laptops (via `BAT_NAME=BAT1`) ✅

### Compatibility Requirements
- Linux kernel with sysfs battery control support
- Battery control files: `/sys/class/power_supply/*/charge_control_*_threshold`
- Common battery device names: `BAT0`, `BAT1`, `BATT`

## Installation

### Prerequisites
- Ubuntu 22.04+ / Debian 11+ (or compatible distribution)
- Python 3.8+ (for GUI)
- PolicyKit (for GUI privilege escalation)

### GUI Installation
```bash
# Download and install GUI package
wget https://github.com/lollolha97/tuf-charge-keeper/releases/download/v1.0.0/a14-charge-keeper-gui_1.0.0_all.deb
sudo dpkg -i a14-charge-keeper-gui_1.0.0_all.deb
sudo apt-get install -f  # Fix any missing dependencies
```

### CLI-only Installation
```bash
# Download and install CLI package
wget https://github.com/lollolha97/tuf-charge-keeper/releases/download/v0.3.0/a14-charge-keeper_0.3.0_all.deb
sudo dpkg -i a14-charge-keeper_0.3.0_all.deb
```

### Manual Installation
```bash
# Clone repository
git clone https://github.com/lollolha97/tuf-charge-keeper.git
cd tuf-charge-keeper

# Install CLI tool
sudo install -m 755 cli/a14-charge-keeper /usr/local/bin/

# For GUI, install Python dependencies
pip3 install PyQt5
```

## Usage

### GUI Application

**Launch from Applications Menu:**
- Look for "Battery Charge Keeper" in system applications
- Or run `a14-charge-keeper-gui` from terminal

**System Tray Features:**
- Left click: Open threshold control popup
- Right click: Access battery details and settings
- Hover: View current battery status
- Dynamic icons: Battery level and charging status indication

**Settings:**
- Theme selection (Dark/Light/Auto)
- Refresh interval (5-300 seconds)
- Auto-start with system
- Notification preferences

### CLI Commands

```bash
# Check current status and battery info
a14-charge-keeper status

# Set threshold (temporary, lost on reboot/resume)
sudo a14-charge-keeper set 80

# Set threshold with persistent auto-reapply
sudo a14-charge-keeper persist 80

# Clear threshold to 100% and disable auto-reapply
sudo a14-charge-keeper clear

# Verify current setting matches expected value
a14-charge-keeper verify 80

# Complete removal of all components
sudo a14-charge-keeper uninstall
```

### Environment Variables

```bash
# Override battery device name (default: BAT0)
BAT_NAME=BAT1 a14-charge-keeper status

# For ThinkPad/Lenovo laptops
export BAT_NAME=BAT1
sudo a14-charge-keeper persist 60
```

## Architecture

### Project Structure
```
├── cli/                           # Command-line interface
│   ├── a14-charge-keeper         # Main CLI executable
│   ├── check-support.sh          # Hardware compatibility checker
│   └── debian/                   # Debian packaging files
├── gui/                          # GUI application
│   ├── main.py                   # GUI entry point
│   ├── src/
│   │   ├── core/                 # Business logic layer
│   │   │   ├── battery_manager.py
│   │   │   ├── cli_interface.py
│   │   │   ├── status_parser.py
│   │   │   └── config_manager.py
│   │   └── gui/                  # GUI components
│   │       ├── system_tray.py
│   │       ├── battery_popup.py
│   │       ├── battery_detail_dialog.py
│   │       ├── settings_dialog.py
│   │       └── simple_context_menu.py
│   └── debian/                   # GUI packaging files
└── docs/                         # Documentation
```

### Safety Mechanisms
- **Process Locking**: Prevents concurrent modifications
- **Backup/Rollback**: Automatic backup before changes
- **Input Validation**: 20-100% range enforcement
- **Hardware Verification**: Multi-step compatibility checking
- **Conflict Detection**: Warns about competing tools (TLP, asusctl)

### GUI Architecture
- **MVC Pattern**: Clear separation of concerns
- **CLI Backend**: Leverages proven CLI tool for safety
- **Qt Event System**: Robust event handling and signal management
- **PolicyKit Integration**: Secure privilege escalation
- **Theme System**: Consistent UI across light/dark themes

## Development

### Building from Source
```bash
# Clone and setup development environment
git clone https://github.com/lollolha97/tuf-charge-keeper.git
cd tuf-charge-keeper

# Install development dependencies
pip3 install PyQt5 pytest

# Run tests
python3 -m pytest tests/ -v

# Build Debian packages
cd cli && dpkg-deb --build debian/
cd ../gui && dpkg-deb --build debian/
```

### Testing
```bash
# Hardware compatibility test
./cli/check-support.sh

# Manual threshold test (requires root)
sudo sh -c 'echo 80 > /sys/class/power_supply/BAT0/charge_control_end_threshold'
cat /sys/class/power_supply/BAT0/charge_control_end_threshold

# Service testing
systemctl status a14-charge-keeper.service
journalctl -u a14-charge-keeper.service

# GUI testing
python3 gui/main.py  # Run GUI in development mode
```

## 📊 Performance Metrics

<div align="center">

| Metric | Value | Status |
|--------|--------|---------|
| 💾 **Memory Usage** | 145MB | ![Excellent](https://img.shields.io/badge/Status-Excellent-brightgreen.svg) |
| ⚡ **CPU (Idle)** | 0.0% | ![Perfect](https://img.shields.io/badge/Status-Perfect-brightgreen.svg) |
| 🔋 **CPU (Active)** | 3-5% | ![Good](https://img.shields.io/badge/Status-Good-green.svg) |
| 🚀 **Startup Time** | 2-3 seconds | ![Fast](https://img.shields.io/badge/Status-Fast-green.svg) |
| 🔋 **Battery Impact** | Negligible | ![Minimal](https://img.shields.io/badge/Status-Minimal-brightgreen.svg) |

</div>

> **Real-world tested**: Continuous 8+ hour operation with zero memory leaks or performance degradation

See [PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md) for detailed benchmarks and profiling data.

## Troubleshooting

### Common Issues

**Hardware not supported:**
- Run `./cli/check-support.sh` to verify compatibility
- Try different battery names: `BAT_NAME=BAT1 a14-charge-keeper status`
- Check kernel version: `uname -r` (requires 5.4+)

**Permission denied errors:**
- Use `sudo` for all modification commands
- For GUI: PolicyKit should handle privileges automatically
- Verify user is in sudoers group: `groups $USER`

**Settings not persistent after reboot/resume:**
- Use `persist` command instead of `set`
- Check systemd service: `systemctl status a14-charge-keeper.service`
- Verify sleep hook: `ls -la /lib/systemd/system-sleep/a14-charge-keeper`

**GUI issues:**
- Install missing dependencies: `sudo apt-get install python3-pyqt5`
- Check PolicyKit setup: `pkcheck -a org.freedesktop.policykit.exec -u $USER`
- Run from terminal to see error messages: `a14-charge-keeper-gui`

**Conflicts with other tools:**
- TLP users: Disable TLP's battery features or uninstall TLP
- asusctl users: May need to disable asusctl battery management
- Check for conflicts: `which tlp asusctl`

## Multi-brand Support

### ASUS Laptops
- Usually support only `charge_control_end_threshold`
- Default battery device: `BAT0`
- Tested models: TUF A14, TUF A15, ROG series

### ThinkPad/Lenovo Laptops  
- Often support both start and end thresholds
- Common battery device: `BAT1`
- Usage: `BAT_NAME=BAT1 a14-charge-keeper persist 80`

### Other Brands
- Dell, HP, Framework: Check with `check-support.sh`
- Battery devices vary: `BAT0`, `BAT1`, `BATT`
- Refer to kernel documentation for model-specific details

## 🤝 Contributing

<div align="center">

![Contributors Welcome](https://img.shields.io/badge/Contributors-Welcome-brightgreen.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-blue.svg)
![Code Style](https://img.shields.io/badge/Code%20Style-Black-black.svg)
![TDD](https://img.shields.io/badge/Development-TDD-red.svg)

</div>

We welcome contributions! This project follows **Test-Driven Development** and maintains high code quality standards.

### **🚀 Quick Contribution Guide**
1. **🍴 Fork & Clone**: `git clone https://github.com/lollolha97/tuf-charge-keeper.git`
2. **🌿 Branch**: `git checkout -b feature/awesome-improvement`
3. **🧪 Test-First**: Write tests before implementation (TDD methodology)
4. **⚡ Hardware Test**: Verify on real Linux hardware
5. **📦 Package Test**: `dpkg-deb --build debian/`
6. **📤 Submit PR**: Detailed description with test results

### **📋 Development Standards**
- **✅ Test Coverage**: All new features require tests
- **🎨 Code Style**: Follow existing patterns and conventions  
- **📖 Documentation**: Update docs for user-facing changes
- **🔒 Security**: No hardcoded credentials or unsafe operations
- **⚡ Performance**: Profile resource usage for GUI changes

### **🏗️ Development Setup**
```bash
# Clone and setup
git clone https://github.com/lollolha97/tuf-charge-keeper.git
cd tuf-charge-keeper

# Install dev dependencies
pip3 install PyQt5 pytest pytest-mock

# Run full test suite
python3 -m pytest tests/ -v --cov=src/

# Test hardware compatibility
./cli/check-support.sh
```

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

<div align="center">

![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

## 🙏 Acknowledgments

<div align="center">

**Built with ❤️ for the Linux community**

</div>

- **🐧 Linux Kernel Team** - For the robust battery subsystem and sysfs interfaces
- **🖥️ ASUS Linux Community** - Hardware insights and testing feedback
- **📦 Ubuntu/Debian Maintainers** - Excellent packaging guidelines and standards
- **🎨 PyQt5 Team** - Powerful GUI framework enabling native Linux integration
- **🧪 pytest Community** - Outstanding testing framework supporting our TDD approach
- **⚡ systemd Team** - Reliable service management and sleep hook integration
- **🔒 PolicyKit Developers** - Secure privilege escalation framework
- **👥 All Contributors & Testers** - Making this project better every day

## 🔗 References & Resources

### **📚 Technical Documentation**
- [**Linux Kernel Battery ABI**](https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-class-power) - Official sysfs interface documentation
- [**Ubuntu Battery Guide**](https://ubuntuhandbook.org/index.php/2024/02/limit-battery-charge-ubuntu/) - Ubuntu-specific battery management
- [**systemd Documentation**](https://systemd.io/) - Service management and sleep hooks
- [**PolicyKit Manual**](https://www.freedesktop.org/software/polkit/docs/latest/) - Privilege escalation framework

### **🏷️ Community Resources**  
- [**ASUS Linux Project**](https://asus-linux.org/manual/asusctl-manual/) - ASUS-specific Linux tools
- [**TLP Battery Care**](https://linrunner.de/tlp/faq/battery.html) - Advanced battery management
- [**PyQt5 Documentation**](https://doc.qt.io/qtforpython/) - GUI framework reference
- [**FreeDesktop Standards**](https://www.freedesktop.org/wiki/Specifications/) - Linux desktop integration

---

<div align="center">

**🚀 Version 1.0.0** • **📅 August 2025** • **🖥️ Ubuntu 24.04 LTS** • **💻 ASUS TUF Gaming A14**

**⭐ Star this repo if it helped you manage your battery better!**

![GitHub stars](https://img.shields.io/github/stars/lollolha97/tuf-charge-keeper?style=social)
![GitHub forks](https://img.shields.io/github/forks/lollolha97/tuf-charge-keeper?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/lollolha97/tuf-charge-keeper?style=social)

</div>