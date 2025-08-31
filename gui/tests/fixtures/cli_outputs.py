"""Sample CLI output fixtures for testing."""

FULL_STATUS_OUTPUT = """Device : BAT0
충전 종료: 70%
백업 파일: 2개

  native-path:          BAT0
  vendor:               AS3GYRE3KC
  model:                GA40347
  serial:               06D2
  power supply:         yes
  updated:              Sun 31 Aug 2025 04:36:22 PM KST (23 seconds ago)
  has history:          yes
  has statistics:       yes
  battery
    present:             yes
    rechargeable:        yes
    state:               discharging
    warning-level:       none
    energy:              45.088 Wh
    energy-empty:        0 Wh
    energy-full:         68.314 Wh
    energy-full-design:  73 Wh
    energy-rate:         15.126 W
    voltage:             15.858 V
    charge-cycles:       N/A
    time to empty:       3.0 hours
    percentage:          66%
    capacity:            93.5808%
    icon-name:          'battery-full-symbolic'
  History (charge):"""

CHARGING_STATUS_OUTPUT = """Device : BAT0
충전 종료: 80%
백업 파일: 1개

  native-path:          BAT0
  vendor:               AS3GYRE3KC
  model:                GA40347
  serial:               06D2
  power supply:         yes
  updated:              Sun 31 Aug 2025 04:40:15 PM KST (5 seconds ago)
  has history:          yes
  has statistics:       yes
  battery
    present:             yes
    rechargeable:        yes
    state:               charging
    warning-level:       none
    energy:              55.2 Wh
    energy-empty:        0 Wh
    energy-full:         68.314 Wh
    energy-full-design:  73 Wh
    energy-rate:         45.8 W
    voltage:             16.2 V
    charge-cycles:       N/A
    time to full:        17.5 minutes
    percentage:          81%
    capacity:            93.5808%
    icon-name:          'battery-full-charging-symbolic'
  History (charge):"""

THINKPAD_STATUS_OUTPUT = """Device : BAT0
충전 종료: 80%
충전 시작: 75% (ThinkPad/Lenovo 등 지원)
백업 파일: 0개

  native-path:          BAT0
  vendor:               LGC
  model:                L19M4PC0
  serial:               1234
  power supply:         yes
  updated:              Sun 31 Aug 2025 04:35:00 PM KST (10 seconds ago)
  has history:          yes
  has statistics:       yes
  battery
    present:             yes
    rechargeable:        yes
    state:               not charging
    warning-level:       none
    energy:              55.44 Wh
    energy-empty:        0 Wh
    energy-full:         70.24 Wh
    energy-full-design:  71 Wh
    energy-rate:         0 W
    voltage:             12.48 V
    charge-cycles:       125
    percentage:          79%
    capacity:            98.9296%
    icon-name:          'battery-full-symbolic'
  History (charge):"""

MINIMAL_STATUS_OUTPUT = """Device : BAT1
충전 종료: 100%
백업 파일: 0개"""