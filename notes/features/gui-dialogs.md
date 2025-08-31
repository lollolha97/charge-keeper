# GUI Dialogs Implementation - TDD Notes

## Current Status
시스템 트레이 앱은 완료되었지만 실제 GUI 창들이 아직 구현되지 않음:
- `_show_status()`: print문만 있음
- `_show_settings()`: print문만 있음

## Phase 5: Settings Dialog (설정 다이얼로그)

### 목표
AlDente 스타일의 설정 윈도우:
- 배터리 충전 제한 슬라이더 (20-100%)
- 현재 배터리 상태 표시
- 적용/취소 버튼
- 실시간 배터리 정보 업데이트

### 기능 요구사항
1. **슬라이더 컨트롤**: 20-100% 범위
2. **현재 상태 표시**: 배터리 %, 충전 상태
3. **버튼**: 적용, 지속적 적용, 초기화, 닫기
4. **실시간 업데이트**: 배터리 정보 자동 갱신

## Phase 6: Battery Status Dialog (배터리 상태 다이얼로그)

### 목표
상세한 배터리 정보 표시:
- 하드웨어 정보 (제조사, 모델, 시리얼)
- 전력 정보 (전압, 에너지, 소비율)
- 배터리 건강도
- 충전 사이클 (지원 시)

### 표시 정보
- Device, Vendor, Model, Serial
- Current/Full/Design Energy
- Voltage, Power Rate
- Battery Health %
- Charge Cycles (if available)

## TDD 개발 순서
1. Settings Dialog 컴포넌트 테스트
2. Settings Dialog UI 구현
3. Battery Status Dialog 컴포넌트 테스트  
4. Battery Status Dialog UI 구현
5. QSS 스타일 적용