# 패키지 배포 테스트 체크리스트

## 개요
이 문서는 a14-charge-keeper 프로젝트의 Debian 패키지를 배포하기 전에 수행해야 하는 종합적인 테스트 체크리스트입니다.

## 1. 사전 검증 (Pre-distribution Validation)

### 1.1 패키지 구조 검증
- [ ] CLI 패키지 (`a14-charge-keeper_0.3.0_all.deb`)
  - [ ] `dpkg -c` 명령어로 패키지 내용 확인
  - [ ] control 파일 문법 검증
  - [ ] 의존성 정보 정확성 확인 (`bash`, `upower`, `systemd`)
  
- [ ] GUI 패키지 (`a14-charge-keeper-gui_1.0.0_all.deb`)
  - [ ] `dpkg -c` 명령어로 패키지 내용 확인
  - [ ] GUI 의존성 확인 (`python3`, `python3-pyqt5`, `policykit-1`)
  - [ ] CLI 패키지 의존성 확인

### 1.2 Lintian 정적 분석
```bash
# CLI 패키지 검증
lintian cli/a14-charge-keeper_0.3.0_all.deb

# GUI 패키지 검증  
lintian gui/a14-charge-keeper-gui_1.0.0_all.deb
```

## 2. 설치 테스트 (Installation Testing)

### 2.1 클린 시스템 설치 테스트
- [ ] Ubuntu 24.04 LTS 클린 환경
- [ ] Ubuntu 22.04 LTS 클린 환경  
- [ ] Debian 12 (bookworm) 클린 환경
- [ ] Debian 13 (trixie) 클린 환경

### 2.2 설치 시나리오
```bash
# CLI 패키지 설치
sudo dpkg -i a14-charge-keeper_0.3.0_all.deb
sudo apt-get install -f  # 의존성 문제 해결

# GUI 패키지 설치 (CLI 패키지 의존성 자동 설치 확인)
sudo dpkg -i a14-charge-keeper-gui_1.0.0_all.deb
sudo apt-get install -f
```

### 2.3 설치 검증 항목
- [ ] 실행 파일이 PATH에 정상 설치됨
- [ ] systemd 서비스 파일이 올바른 위치에 설치됨
- [ ] system-sleep 훅이 설치됨
- [ ] GUI 데스크톱 파일이 설치됨
- [ ] 아이콘 파일들이 올바른 위치에 설치됨
- [ ] PolicyKit 정책 파일이 설치됨

## 3. 기능 테스트 (Functional Testing)

### 3.1 CLI 기능 테스트
```bash
# 하드웨어 지원 확인
./cli/check-support.sh

# 상태 확인 (root 권한 불필요)
a14-charge-keeper status

# 임계값 설정 (root 권한 필요)
sudo a14-charge-keeper set 80
sudo a14-charge-keeper verify 80

# 영구 설정
sudo a14-charge-keeper persist 80

# 설정 해제
sudo a14-charge-keeper clear

# 완전 제거
sudo a14-charge-keeper uninstall
```

### 3.2 GUI 기능 테스트
- [ ] 시스템 트레이 아이콘 표시
- [ ] 배터리 상태 팝업 동작
- [ ] 설정 다이얼로그 동작
- [ ] 슬라이더로 임계값 조정
- [ ] 테마 변경 기능
- [ ] PolicyKit 권한 상승 동작

### 3.3 systemd 서비스 테스트
```bash
# 서비스 상태 확인
systemctl status a14-charge-keeper.service

# 부팅시 자동 적용 테스트
sudo systemctl enable a14-charge-keeper.service
sudo reboot
# 재부팅 후 임계값 유지 확인

# 절전모드 후 복구 테스트
sudo systemctl suspend
# 절전모드 해제 후 임계값 유지 확인
```

## 4. 호환성 테스트 (Compatibility Testing)

### 4.1 하드웨어 호환성
- [ ] ASUS TUF A14 (주요 대상)
- [ ] ThinkPad 시리즈 (BAT_NAME=BAT1)
- [ ] 기타 지원 하드웨어
- [ ] 미지원 하드웨어에서 graceful failure

### 4.2 소프트웨어 충돌 테스트
- [ ] TLP 설치된 환경에서 경고 표시
- [ ] asusctl 설치된 환경에서 경고 표시
- [ ] 다른 배터리 관리 도구와의 충돌 확인

## 5. 스트레스 테스트 (Stress Testing)

### 5.1 동시 실행 테스트
```bash
# 동시 실행 방지 확인
sudo a14-charge-keeper set 80 &
sudo a14-charge-keeper set 90 &
# 프로세스 잠금 동작 확인
```

### 5.2 장시간 실행 테스트
- [ ] GUI 애플리케이션 24시간 연속 실행
- [ ] 메모리 누수 확인
- [ ] CPU 사용률 모니터링

## 6. 보안 테스트 (Security Testing)

### 6.1 권한 테스트
- [ ] 일반 사용자로 수정 권한 없음 확인
- [ ] sudo 없이 상태 조회 가능 확인
- [ ] PolicyKit 권한 상승 정상 동작

### 6.2 파일 시스템 권한
- [ ] 설치된 파일의 권한 확인
- [ ] 백업 파일 생성/복원 권한 확인
- [ ] 로그 파일 권한 확인

## 7. 제거 테스트 (Removal Testing)

### 7.1 패키지 제거
```bash
# GUI 패키지 제거
sudo apt remove a14-charge-keeper-gui

# CLI 패키지 제거  
sudo apt remove a14-charge-keeper

# 완전 제거 (설정 파일 포함)
sudo apt purge a14-charge-keeper a14-charge-keeper-gui
```

### 7.2 제거 후 정리 확인
- [ ] 시스템 파일이 완전히 제거됨
- [ ] systemd 서비스가 비활성화됨
- [ ] 백업 파일이 적절히 처리됨
- [ ] 사용자 설정이 유지/제거됨 (purge에 따라)

## 8. 업그레이드 테스트 (Upgrade Testing)

### 8.1 패키지 업그레이드
```bash
# 이전 버전에서 현재 버전으로 업그레이드
sudo dpkg -i a14-charge-keeper_0.3.0_all.deb
sudo dpkg -i a14-charge-keeper-gui_1.0.0_all.deb
```

### 8.2 업그레이드 검증
- [ ] 기존 설정이 유지됨
- [ ] 새로운 기능이 정상 동작
- [ ] 서비스 중단 없이 업그레이드됨

## 9. 로그 및 오류 처리 테스트

### 9.1 로그 확인
```bash
# systemd 로그
journalctl -u a14-charge-keeper.service

# GUI 애플리케이션 로그
# 터미널에서 실행하여 오류 메시지 확인
a14-charge-keeper-gui
```

### 9.2 오류 시나리오 테스트
- [ ] 하드웨어 파일 접근 실패시 처리
- [ ] 권한 부족시 적절한 오류 메시지
- [ ] 네트워크 연결 없는 환경에서 동작
- [ ] 디스크 공간 부족시 처리

## 10. 성능 테스트

### 10.1 리소스 사용량
```bash
# CPU 및 메모리 사용량 모니터링
top -p `pgrep -f a14-charge-keeper`
```

### 10.2 응답시간 측정
- [ ] CLI 명령어 응답시간 (< 1초)
- [ ] GUI 인터페이스 반응성
- [ ] 시스템 트레이 아이콘 업데이트 주기

## 11. 문서화 검증

### 11.1 패키지 정보
- [ ] man 페이지 존재 여부
- [ ] --help 옵션 동작
- [ ] README 파일 정확성

### 11.2 사용자 가이드
- [ ] 설치 가이드 정확성
- [ ] 사용 방법 명확성
- [ ] 트러블슈팅 가이드 유효성

## 12. 자동화된 테스트 (Autopkgtest)

### 12.1 테스트 스크립트 준비
```bash
# debian/tests/control 파일 생성
# 자동화된 설치/실행 테스트 스크립트 작성
```

### 12.2 테스트 실행
```bash
# autopkgtest 실행
autopkgtest *.deb -- null
```

## 테스트 완료 체크리스트

- [ ] 모든 지원 플랫폼에서 테스트 완료
- [ ] 치명적 버그 없음
- [ ] 성능 요구사항 만족
- [ ] 보안 검토 통과
- [ ] 문서화 완료
- [ ] 배포 준비 완료

## 배포 후 모니터링

### 지속적 모니터링 항목
- [ ] 사용자 피드백 수집
- [ ] 버그 리포트 추적
- [ ] 성능 메트릭 모니터링
- [ ] 보안 취약점 모니터링
- [ ] 업스트림 의존성 변경사항 추적