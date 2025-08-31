# A14 Charge Keeper GUI

PyQt5 기반 배터리 충전 임계값 관리를 위한 시스템 트레이 애플리케이션

## 🎯 기능

- **시스템 트레이 통합**: 배터리 아이콘으로 상시 모니터링
- **실시간 배터리 정보**: 충전 상태, 용량, 임계값 표시
- **한국어 지원**: 직관적인 한국어 인터페이스
- **자동 새로고침**: 30초마다 자동 상태 업데이트
- **CLI 백엔드 통합**: 기존 a14-charge-keeper와 완벽 연동

## 📋 요구사항

### 시스템 요구사항
- Ubuntu 24.04 LTS (또는 PyQt5 지원 Linux)
- Python 3.8+
- 지원 하드웨어: ASUS TUF A14, ThinkPad 등

### 의존성
```bash
# Python 패키지
pip install PyQt5 psutil

# 시스템 패키지 (Ubuntu)
sudo apt install python3-pyqt5
```

### 필수 조건
- `a14-charge-keeper` CLI 도구가 설치되어 있어야 함
- 시스템 트레이가 활성화되어 있어야 함

## 🚀 설치 및 실행

### 방법 1: 직접 실행
```bash
cd gui
python3 main.py
```

### 방법 2: 개발 모드 설치
```bash
cd gui
pip install -e .
a14-charge-keeper-gui
```

### 방법 3: CLI 경로 지정
```bash
cd gui
PATH=$PATH:../cli python3 main.py
```

## 💡 사용법

### 시스템 트레이 아이콘
- **좌클릭**: 설정 윈도우 열기 (향후 구현)
- **우클릭**: 컨텍스트 메뉴
  - 📊 **배터리 상태**: 현재 배터리 정보 표시
  - ⚙️ **설정**: 임계값 설정 (향후 구현)
  - 🚪 **종료**: 애플리케이션 종료

### 툴팁 정보
시스템 트레이 아이콘에 마우스를 올리면 다음 정보 표시:
- 배터리 용량 (%)
- 충전 상태 (충전 중/방전 중/완충)
- 설정된 충전 제한 (100%가 아닌 경우)

## 🔧 문제해결

### GUI가 시작되지 않는 경우
```bash
# PyQt5 설치 확인
python3 -c "import PyQt5; print('PyQt5 OK')"

# 시스템 트레이 지원 확인
python3 -c "from PyQt5.QtWidgets import QApplication, QSystemTrayIcon; app = QApplication([]); print('Tray available:', QSystemTrayIcon.isSystemTrayAvailable())"
```

### CLI를 찾을 수 없는 경우
```bash
# CLI 도구 설치 확인
which a14-charge-keeper

# 직접 경로 지정
PATH=/path/to/cli:$PATH python3 main.py
```

### 권한 오류
```bash
# CLI 도구 실행 권한 확인
sudo a14-charge-keeper status
```

## 🏗️ 개발자 정보

### 아키텍처
```
GUI Layer (PyQt5)
├── TrayIcon: 시스템 트레이 아이콘
└── SystemTrayApp: 메인 애플리케이션

Business Logic
├── BatteryManager: 상태 관리
├── CliInterface: CLI 통신
└── StatusParser: 출력 파싱

CLI Backend
└── a14-charge-keeper: 실제 하드웨어 제어
```

### 테스트 실행
```bash
cd gui
python3 -m pytest tests/ -v
```

### 코드 커버리지
```bash
python3 -m pytest tests/ --cov=src --cov-report=html
```

## 📈 향후 계획

- [ ] AlDente 스타일 현대적 UI 디자인
- [ ] 설정 다이얼로그 구현
- [ ] 상세한 배터리 정보 표시 윈도우
- [ ] 자동 시작 옵션
- [ ] 시스템 알림 통합
- [ ] 다크/라이트 테마 지원

## 🐛 알려진 문제

- GUI 테스트가 headless 환경에서 제한적
- PyQt5 의존성으로 인한 패키지 크기
- 일부 최소 설치 환경에서 시스템 트레이 미지원 가능성

## 📄 라이선스

MIT License - 자세한 내용은 LICENSE 파일 참조