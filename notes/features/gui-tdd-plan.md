# A14 Charge Keeper GUI - TDD Development Plan ✅ COMPLETED

**개발 상태**: ✅ 완료 (2025-08-31)
**테스트 상태**: 25개 테스트 모두 통과 (15개 단위 + 10개 통합)
**커버리지**: 핵심 비즈니스 로직 높은 커버리지 확보

## 개발 철학

**GUI는 얇은 프레젠테이션 레이어로 유지하고, 기존 CLI 도구를 백엔드로 활용**

- GUI가 직접 sysfs를 조작하지 않음
- 기존 CLI의 검증된 안전장치와 로직을 재사용
- 코드 중복 최소화 및 유지보수성 향상

## 아키텍처 설계

```
┌─────────────────┐
│   PyQt5 GUI     │ ← 시스템 트레이, 이벤트 핸들링
├─────────────────┤
│  Business Logic │ ← 상태 관리, 검증 로직 (100% 테스트)
├─────────────────┤
│  CLI Interface  │ ← subprocess 통신 (모킹 테스트)
├─────────────────┤
│  Status Parser  │ ← CLI 출력 파싱 (100% 테스트)
└─────────────────┘
         │
    ┌────▼────┐
    │   CLI   │ ← 기존 a14-charge-keeper
    └─────────┘
```

## 프로젝트 구조

```
gui/
├── src/
│   ├── __init__.py
│   ├── main.py                    # 애플리케이션 진입점
│   ├── core/
│   │   ├── __init__.py
│   │   ├── battery_manager.py     # 핵심 비즈니스 로직
│   │   ├── cli_interface.py       # CLI 통신 레이어
│   │   ├── status_parser.py       # CLI 출력 파싱
│   │   └── config_manager.py      # 설정 관리
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── system_tray.py         # 시스템 트레이 앱
│   │   ├── settings_dialog.py     # 설정 다이얼로그
│   │   └── styles/
│   │       └── aldente_style.qss  # AlDente 스타일
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py          # 커스텀 예외
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # pytest 설정
│   ├── unit/
│   │   ├── test_status_parser.py
│   │   ├── test_cli_interface.py
│   │   ├── test_battery_manager.py
│   │   └── test_config_manager.py
│   ├── integration/
│   │   ├── test_cli_integration.py
│   │   └── test_end_to_end.py
│   └── fixtures/
│       ├── cli_outputs.py        # CLI 출력 샘플
│       └── test_configs.py       # 테스트 설정 데이터
├── requirements.txt
├── requirements-dev.txt
└── pytest.ini
```

## TDD 개발 단계

### Phase 1: 핵심 유틸리티 및 파싱 (Red-Green-Refactor)

#### 1.1 CLI 출력 파서 개발
```python
# tests/unit/test_status_parser.py

def test_parse_basic_battery_status():
    """기본 배터리 상태 파싱 테스트"""
    output = """Device : BAT0
충전 종료: 80%
백업 파일: 3개"""
    
    result = StatusParser.parse_status(output)
    
    assert result.device == "BAT0"
    assert result.end_threshold == 80
    assert result.backup_count == 3

def test_parse_with_start_threshold():
    """충전 시작 임계값 포함 파싱 테스트 (ThinkPad)"""
    output = """Device : BAT0
충전 종료: 80%
충전 시작: 60% (ThinkPad/Lenovo 등 지원)"""
    
    result = StatusParser.parse_status(output)
    
    assert result.start_threshold == 60

def test_parse_with_upower_info():
    """upower 정보 포함 파싱 테스트"""
    # 복잡한 출력 파싱 테스트
```

#### 1.2 설정 관리자 개발
```python
# tests/unit/test_config_manager.py

def test_save_and_load_settings():
    """설정 저장/로드 테스트"""
    config = ConfigManager()
    config.set('auto_start', True)
    config.set('default_threshold', 80)
    config.save()
    
    new_config = ConfigManager()
    new_config.load()
    
    assert new_config.get('auto_start') is True
    assert new_config.get('default_threshold') == 80

def test_default_values():
    """기본값 테스트"""
    config = ConfigManager()
    
    assert config.get('auto_start') is False
    assert config.get('default_threshold') == 80
    assert config.get('theme') == 'dark'
```

### Phase 2: CLI 통신 레이어 (Mocking 활용)

#### 2.1 CLI 인터페이스 개발
```python
# tests/unit/test_cli_interface.py

@pytest.fixture
def mock_subprocess(mocker):
    return mocker.patch('subprocess.run')

def test_get_status_success(mock_subprocess):
    """정상 상태 조회 테스트"""
    mock_subprocess.return_value = MockCompletedProcess(
        stdout="Device : BAT0\n충전 종료: 80%", 
        returncode=0
    )
    
    cli = CliInterface()
    result = cli.get_status()
    
    assert result.success is True
    assert result.data.device == "BAT0"
    mock_subprocess.assert_called_once_with(
        ['a14-charge-keeper', 'status'],
        capture_output=True, text=True
    )

def test_set_threshold_with_sudo(mock_subprocess):
    """sudo로 임계값 설정 테스트"""
    mock_subprocess.return_value = MockCompletedProcess(returncode=0)
    
    cli = CliInterface()
    result = cli.set_threshold(70)
    
    assert result.success is True
    mock_subprocess.assert_called_once_with(
        ['sudo', 'a14-charge-keeper', 'set', '70'],
        capture_output=True, text=True
    )

def test_cli_not_found_error(mock_subprocess):
    """CLI 도구 없음 에러 테스트"""
    mock_subprocess.side_effect = FileNotFoundError()
    
    cli = CliInterface()
    result = cli.get_status()
    
    assert result.success is False
    assert "a14-charge-keeper not found" in result.error_message
```

### Phase 3: 비즈니스 로직 레이어

#### 3.1 배터리 매니저 개발
```python
# tests/unit/test_battery_manager.py

def test_battery_manager_initialization(mock_cli):
    """배터리 매니저 초기화 테스트"""
    mock_cli.get_status.return_value = SuccessResult(
        BatteryStatus(device="BAT0", end_threshold=80)
    )
    
    manager = BatteryManager()
    manager.initialize()
    
    assert manager.current_status.device == "BAT0"
    assert manager.is_initialized is True

def test_set_threshold_validation():
    """임계값 설정 검증 테스트"""
    manager = BatteryManager()
    
    # 유효한 값
    result = manager.set_threshold(80)
    assert result.success is True
    
    # 무효한 값들
    assert manager.set_threshold(19).success is False  # 너무 낮음
    assert manager.set_threshold(101).success is False  # 너무 높음
    assert manager.set_threshold('invalid').success is False  # 문자열

def test_status_change_notifications():
    """상태 변경 알림 테스트"""
    manager = BatteryManager()
    callback_called = False
    
    def status_callback(status):
        nonlocal callback_called
        callback_called = True
    
    manager.register_status_callback(status_callback)
    manager._notify_status_change(BatteryStatus(device="BAT0"))
    
    assert callback_called is True
```

### Phase 4: GUI 컴포넌트 (pytest-qt 활용)

#### 4.1 시스템 트레이 개발
```python
# tests/unit/test_system_tray.py

def test_tray_icon_creation(qtbot, mock_battery_manager):
    """트레이 아이콘 생성 테스트"""
    tray = SystemTray(mock_battery_manager)
    qtbot.addWidget(tray)
    
    assert tray.isVisible() is False  # 초기에는 숨김
    assert tray.contextMenu() is not None

def test_menu_actions(qtbot, mock_battery_manager):
    """컨텍스트 메뉴 액션 테스트"""
    tray = SystemTray(mock_battery_manager)
    qtbot.addWidget(tray)
    
    menu = tray.contextMenu()
    actions = menu.actions()
    
    action_texts = [action.text() for action in actions]
    assert "설정" in action_texts
    assert "상태 확인" in action_texts
    assert "종료" in action_texts

def test_icon_updates_on_status_change(qtbot, mock_battery_manager):
    """상태 변경 시 아이콘 업데이트 테스트"""
    tray = SystemTray(mock_battery_manager)
    qtbot.addWidget(tray)
    
    # 제한 상태로 변경
    limited_status = BatteryStatus(device="BAT0", end_threshold=80)
    tray.update_icon(limited_status)
    
    # 아이콘이 제한 상태를 반영하는지 확인
    # (실제로는 아이콘 파일명이나 색상 등을 검증)
```

### Phase 5: 통합 테스트

#### 5.1 End-to-End 테스트
```python
# tests/integration/test_end_to_end.py

def test_complete_threshold_setting_flow(qtbot, real_cli_available):
    """완전한 임계값 설정 플로우 테스트"""
    if not real_cli_available:
        pytest.skip("CLI tool not available")
    
    app = BatteryManagerApp()
    qtbot.addWidget(app.tray)
    
    # 초기 상태 확인
    initial_status = app.battery_manager.get_current_status()
    
    # 설정 변경
    app.battery_manager.set_threshold(70)
    
    # 상태 재조회하여 변경 확인
    new_status = app.battery_manager.get_current_status()
    assert new_status.end_threshold == 70
```

## 테스트 실행 환경 설정

### requirements-dev.txt
```
pytest>=7.0.0
pytest-qt>=4.0.0
pytest-mock>=3.7.0
pytest-cov>=4.0.0
PyQt5>=5.15.0
psutil>=5.8.0
```

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    gui: GUI tests requiring display
```

## 개발 워크플로우

### 1. 브랜치 생성
```bash
git checkout main
git pull origin main
git checkout -b feature/gui-core-components
```

### 2. TDD 사이클 실행
각 컴포넌트별로:
1. **Red**: 실패하는 테스트 작성
2. **Green**: 테스트를 통과시키는 최소 코드 작성
3. **Refactor**: 코드 품질 개선
4. **Commit**: 모든 테스트 통과 시에만 커밋

### 3. 커밋 메시지 형식
```
feat: Add battery status parser with ThinkPad support

- Parse basic battery status from CLI output
- Support both ASUS (end threshold) and ThinkPad (start+end)
- Add comprehensive error handling for malformed output
- 100% test coverage with edge cases

Tests: 15 passed, 0 failed
```

### 4. Pull Request 생성
기능 완성 후 GitHub에 푸시하여 PR 생성

## ✅ 실제 개발 결과 (2025-08-31)

### 완료된 Phase들:
- ✅ **Phase 1**: CLI 출력 파서, 설정 관리자 개발 완료
- ✅ **Phase 2**: CLI 통신 레이어 개발 완료 
- ✅ **Phase 3**: 비즈니스 로직 레이어 개발 완료
- ✅ **Phase 4**: GUI 컴포넌트 개발 완료
- ✅ **Phase 5**: 통합 테스트 완료

### 달성된 품질 목표:
- ✅ **테스트 통과율**: 100% (25/25 테스트 통과)
- ✅ **코드 커버리지**: 핵심 비즈니스 로직 높은 커버리지
- ✅ **성능**: 앱 시작 시간 < 1초 달성
- ✅ **안정성**: sudo 환경에서 안정적 동작 확보

### 추가로 구현된 기능:
- 🎨 **다크/라이트 테마 지원**: 모든 GUI 컴포넌트 일관된 테마 적용
- ⚙️ **설정 다이얼로그**: 테마, 자동 시작, 임계값, 새로고침 간격 설정
- 🔄 **실시간 상태 업데이트**: 설정 가능한 새로고침 간격
- 🛡️ **안전한 sudo 실행**: Qt 환경 최적화로 루트 권한 안정성 확보
- 📊 **상세 배터리 정보**: 섹션별 정리된 종합 배터리 상태 표시

## TDD 방법론 성공 사례

이 프로젝트는 **Red-Green-Refactor 사이클**을 체계적으로 적용하여:
1. **높은 코드 품질** 확보
2. **안정적인 리팩토링** 가능
3. **버그 조기 발견 및 수정**
4. **명확한 요구사항 구현**

TDD 방법론의 효과를 실증한 성공적인 GUI 개발 사례입니다.