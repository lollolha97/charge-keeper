<div align="center">

# ⚡ Charge Keeper

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Linux-green.svg)  
![Tests](https://img.shields.io/badge/Tests-25%20Passing-brightgreen.svg)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)

**🔋 Smart Battery Management for Linux**

*Extend your laptop battery life with intelligent charge limiting*

---

### 🛠️ Built With

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/Qt-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt5"/>
<img src="https://img.shields.io/badge/GNU%20Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white" alt="Bash"/>
<img src="https://img.shields.io/badge/systemd-EE0000?style=for-the-badge&logo=systemd&logoColor=white" alt="systemd"/>
<img src="https://img.shields.io/badge/Debian-A81D33?style=for-the-badge&logo=debian&logoColor=white" alt="Debian"/>
</p>

---

</div>

> **⚠️ DEVELOPMENT STATUS**  
> This tool is **currently in development** and has been primarily tested on **ASUS TUF Gaming A14 (FA401)** with Ubuntu 24.04 LTS.  
> **Not a finished product** - use with caution on untested hardware. Always test with temporary settings first!

## ✨ Features

<div align="center">

| 🎨 **Modern GUI** | 💻 **Powerful CLI** | 🔄 **Smart Persistence** |
|:---:|:---:|:---:|
| System tray integration | Bash-powered commands | Auto-reapply after boot/resume |
| Dark/Light themes | systemd service hooks | Sleep/wake compatibility |
| Real-time battery status | Hardware safety checks | Backup/rollback system |

</div>


## 🚀 Quick Start

<div align="center">

### 📦 [Download Latest Release](https://github.com/lollolha97/charge-keeper/releases/tag/v1.0.0)

| Package | Description | Size |
|---------|-------------|------|
| 🖥️ [**GUI Package**](https://github.com/lollolha97/charge-keeper/releases/download/v1.0.0/a14-charge-keeper-gui_1.0.0_all.deb) | Full featured app (includes CLI) | 103KB |
| ⚡ [**CLI Package**](https://github.com/lollolha97/charge-keeper/releases/download/v1.0.0/a14-charge-keeper_0.3.0_all.deb) | Command-line only | 6KB |

</div>

### ⬇️ Install
```bash
# 🎨 GUI Version (Recommended)
sudo dpkg -i a14-charge-keeper-gui_1.0.0_all.deb
sudo apt-get install -f

# ⚡ CLI Only
sudo dpkg -i a14-charge-keeper_0.3.0_all.deb
```

## 🎯 Usage

### 🖥️ GUI Mode
```bash
a14-charge-keeper-gui
```
**Left-click** tray icon → 🎚️ Set threshold with slider  
**Right-click** → 📊 Battery details and settings

### ⚡ CLI Mode
```bash
a14-charge-keeper status          # 📋 Check current status
sudo a14-charge-keeper set 80     # ⚡ Set to 80% (temporary)
sudo a14-charge-keeper persist 80 # 🔒 Set to 80% (permanent)
sudo a14-charge-keeper clear      # 🔄 Reset to 100%
```

## 🔧 Hardware Compatibility

**⚠️ Always test first!** → `./cli/check-support.sh`

<div align="center">

| Status | Device | Notes |
|:---:|---------|-------|
| ✅ | **ASUS TUF Gaming A14 (FA401)** | Ubuntu 24.04 LTS - Fully tested |
| ⚠️ | **ASUS TUF A15, A17** | Community reports - Use with caution |
| ⚠️ | **ThinkPad/Lenovo** | Use `BAT_NAME=BAT1` - Community reports |
| ❓ | **Other Linux Laptops** | Requires sysfs battery control support |

</div>

### 🛡️ Safety Protocol
1. **Check** → `./cli/check-support.sh`
2. **Test** → `sudo a14-charge-keeper set 80`
3. **Verify** → Check if it actually works
4. **Persist** → `sudo a14-charge-keeper persist 80`

---

## 🔬 Development

```bash
git clone https://github.com/lollolha97/charge-keeper.git
cd charge-keeper
pip3 install PyQt5 pytest pytest-mock
python3 -m pytest tests/ -v  # 🧪 25 comprehensive tests
```

**📋 Requirements**: Ubuntu 22.04+ • Python 3.8+ • Linux kernel with sysfs battery control

**🏗️ Architecture**: MVC pattern • Qt event system • Safe sysfs operations • 145MB RAM • 0% idle CPU

---

## ⚠️ Disclaimer & Liability

**USE AT YOUR OWN RISK**

This software is provided "AS IS" without warranty of any kind. The author(s) are **NOT RESPONSIBLE** for:
- Battery damage or degradation
- Hardware malfunction or failure  
- System instability or data loss
- Any direct or indirect damages

**By using this software, you acknowledge that:**
- You understand the risks of modifying system-level battery settings
- You take full responsibility for any consequences
- You will test thoroughly on non-critical systems first
- The software may not work correctly on your specific hardware

**THIS IS EXPERIMENTAL SOFTWARE** - primarily tested on ASUS TUF Gaming A14. Use extreme caution on other devices.

---

<div align="center">

---

## 📜 License

**MIT License** © 2025 lollolha97

## ⭐ Show Your Support

**If this tool saved your battery, give it a star!**

![GitHub stars](https://img.shields.io/github/stars/lollolha97/charge-keeper?style=social)
![GitHub forks](https://img.shields.io/github/forks/lollolha97/charge-keeper?style=social)

**Made with ❤️ for the Linux community**

</div>