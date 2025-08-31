# A14 Charge Keeper (Ubuntu 24.04)

ASUS **TUF A14**(예: FA401)에서 **Ubuntu 24.04 LTS** 기준으로 배터리 \*\*충전 상한(예: 60\~80%)\*\*을 설정·유지하기 위한 초경량 스크립트 + systemd 구성 안내입니다. 커널의 `sysfs` 인터페이스(`/sys/class/power_supply/.../charge_control_end_threshold`)를 직접 사용합니다. 별도 데몬이나 외부 의존성 없이 동작합니다.

> **요약**: A14에서 `/sys/class/power_supply/BAT0/charge_control_end_threshold`가 보이면 지원됩니다. 이 값을 바꾸면 해당 %에서 충전이 멈춥니다. 일부 모델은 재부팅/절전(resume) 시 값이 초기화되므로, systemd로 자동 재적용을 설정합니다.

---

## 지원/전제조건

* Ubuntu **24.04 LTS** (커널 6.8+)
* 배터리 장치: 보통 `BAT0` (모델에 따라 `BAT1`, `BATT` 등일 수 있음)
* 파일 존재 여부로 지원 판별:

  ```bash
  ls /sys/class/power_supply
  # BAT0가 보이면 아래 확인
  [ -e /sys/class/power_supply/BAT0/charge_control_end_threshold ] && echo "지원됨"
  ```
* (선택) `charge_control_start_threshold`는 일부 모델만 제공됩니다. A14는 보통 **end(종료) 임계값만** 동작합니다.

---

## 빠른 시작 (일회성 테스트)

배터리를 **80%까지만 충전**하도록 즉시 적용:

```bash
sudo sh -c 'echo 80 > /sys/class/power_supply/BAT0/charge_control_end_threshold'
```

확인:

```bash
cat /sys/class/power_supply/BAT0/charge_control_end_threshold
```

> 값이 `80`으로 나오면 적용 완료. 배터리가 80%에 도달하면 충전이 멈춥니다(소폭 히스테리시스 존재 가능).

---

## 프로젝트 구조

* **`/usr/local/bin/a14-charge-keeper`**: 단일 Bash CLI (set/status/persist/clear/uninstall)
* **systemd oneshot 서비스**: 부팅 시 임계값 재적용
* **system-sleep 훅**: 절전 후(resume/thaw) 임계값 재적용

---

## 설치 (스크립트 배치)

다음 스크립트를 그대로 저장합니다.

**파일 경로**: `/usr/local/bin/a14-charge-keeper`

```bash
#!/usr/bin/env bash
set -euo pipefail

readonly VERSION="0.1.0"
BAT_DIR="/sys/class/power_supply"
BAT_NAME="${BAT_NAME:-BAT0}"
END_FILE="$BAT_DIR/$BAT_NAME/charge_control_end_threshold"
START_FILE="$BAT_DIR/$BAT_NAME/charge_control_start_threshold"
SERVICE="a14-charge-keeper.service"
SLEEP_HOOK="/lib/systemd/system-sleep/a14-charge-keeper"

usage() {
  cat <<USAGE
A14 Charge Keeper v$VERSION

사용법:
  a14-charge-keeper set <20-100>   # 종료 임계값을 퍼센트로 설정(예: 60)
  a14-charge-keeper status          # 현재 임계값/배터리 상태 표시
  a14-charge-keeper persist <20-100># 부팅/절전 복원 자동적용 구성
  a14-charge-keeper clear           # 임계값 100%로 복원 + 자동적용 해제
  a14-charge-keeper uninstall       # 설치물(서비스/훅) 제거
USAGE
}

require_root() {
  if [[ $EUID -ne 0 ]]; then
    echo "[!] 루트 권한이 필요합니다. 'sudo'로 다시 실행하세요." >&2
    exit 1
  fi
}

assert_supported() {
  if [[ ! -e "$END_FILE" ]]; then
    echo "[!] 지원 파일을 찾을 수 없습니다: $END_FILE" >&2
    echo "    BAT_NAME가 다르다면 'BAT_NAME=BAT1 a14-charge-keeper ...' 식으로 지정하세요." >&2
    exit 2
  fi
}

set_limit() {
  require_root
  assert_supported
  local val="$1"
  if ! [[ "$val" =~ ^[0-9]+$ ]] || (( val < 20 || val > 100 )); then
    echo "[!] 20~100 사이의 정수만 허용됩니다." >&2
    exit 3
  fi
  echo "$val" > "$END_FILE"
  echo "[*] charge_control_end_threshold = $val 적용 완료"
}

show_status() {
  assert_supported
  local end; end=$(cat "$END_FILE" || echo "?" )
  echo "Device : $BAT_NAME"
  echo "End th.: ${end}%"
  if [[ -e "$START_FILE" ]]; then
    local start; start=$(cat "$START_FILE" || echo "?")
    echo "Start th.: ${start}% (지원되는 모델에 한함)"
  fi
  command -v upower >/dev/null 2>&1 && \
    upower -i "$(upower -e | grep BAT || true)" | sed -n '1,25p' || true
}

install_persist() {
  local val="$1"
  set_limit "$val"
  # systemd 서비스 생성
  cat >/etc/systemd/system/$SERVICE <<UNIT
[Unit]
Description=Set ASUS A14 charge threshold at boot
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo $val > $END_FILE'

[Install]
WantedBy=multi-user.target
UNIT

  systemctl daemon-reload
  systemctl enable --now "$SERVICE"

  # 절전 복원 훅
  cat >"$SLEEP_HOOK" <<'HOOK'
#!/bin/sh
case "$1" in
  post|resume|thaw)
    echo "${A14_LIMIT:-60}" > /sys/class/power_supply/${BAT_NAME:-BAT0}/charge_control_end_threshold
  ;;
esac
HOOK
  chmod +x "$SLEEP_HOOK"
  echo "[*] 부팅/절전 후 자동 재적용 구성 완료 (현재 값: $val%)"
}

clear_limit() {
  require_root
  assert_supported
  echo 100 > "$END_FILE"
  systemctl disable --now "$SERVICE" 2>/dev/null || true
  rm -f "/etc/systemd/system/$SERVICE"
  rm -f "$SLEEP_HOOK"
  systemctl daemon-reload || true
  echo "[*] 임계값을 100%로 복원하고 자동 적용을 해제했습니다."
}

uninstall_all() {
  clear_limit
  rm -f "$0"
  echo "[*] a14-charge-keeper를 제거했습니다."
}

cmd="${1:-}"
case "$cmd" in
  set)
    shift; : "${1:?값(20-100)가 필요합니다}"; set_limit "$1" ;;
  status)
    show_status ;;
  persist)
    shift; : "${1:?값(20-100)가 필요합니다}"; require_root; install_persist "$1" ;;
  clear)
    clear_limit ;;
  uninstall)
    uninstall_all ;;
  -h|--help|help|"")
    usage ;;
  *)
    echo "알 수 없는 명령: $cmd" >&2; usage; exit 64 ;;
 esac
```

설치 권한 부여:

```bash
sudo install -m 0755 /usr/local/bin/a14-charge-keeper /usr/local/bin/a14-charge-keeper
```

---

## 사용 예시

* **현재 상태 확인**

  ```bash
  a14-charge-keeper status
  ```
* **60%로 제한(일회성)**

  ```bash
  sudo a14-charge-keeper set 60
  ```
* **60%로 제한 + 부팅/절전 자동 재적용**

  ```bash
  sudo a14-charge-keeper persist 60
  ```
* **원복(100%) & 자동 재적용 해제**

  ```bash
  sudo a14-charge-keeper clear
  ```
* **완전 제거**

  ```bash
  sudo a14-charge-keeper uninstall
  ```

> 참고: 절전 복원 훅은 기본 60%를 사용하며, 필요 시 `sudo env A14_LIMIT=80 BAT_NAME=BAT0 a14-charge-keeper persist 80` 식으로 환경변수로 고정할 수 있습니다.

---

## 문제해결

* **재부팅/절전 후 값이 다시 100으로 돌아옴**
  → `persist`를 적용했는지 확인. `systemctl status a14-charge-keeper.service`에서 성공 여부를 확인하고, `system-sleep` 훅이 실행권한(+x)인지 점검하세요.
* **`Permission denied` 에러**
  → 쓰기 작업은 루트 권한이 필요합니다. `sudo`로 실행하세요.
* **`BAT0`가 아님**
  → `ls /sys/class/power_supply`로 실제 배터리 디바이스명을 확인하고, `BAT_NAME=BAT1 a14-charge-keeper ...`처럼 지정하세요.
* **`charge_control_start_threshold`도 쓰고 싶음**
  → 파일 존재 시 수동으로 설정 가능합니다. (예: `echo 50 > .../charge_control_start_threshold`) 단, 모델 지원 여부가 다릅니다.

---

## 보안/안전

* 본 스크립트는 커널이 제공하는 공식 sysfs 인터페이스만 사용합니다.
* 설정값 범위를 20\~100으로 제한하여 비정상 입력을 차단합니다.
* 배터리 관리 정책은 펌웨어/EC(Embedded Controller)의 동작에 따라 약간의 히스테리시스가 있을 수 있습니다.

---

## 참고 문서 (Ubuntu 24.04 기준)

* Linux 커널 문서(전원/배터리 sysfs ABI):
  [https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-class-power](https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-class-power)
* Ubuntu 22.04/24.04 배터리 충전 한도 설정 가이드:
  [https://ubuntuhandbook.org/index.php/2024/02/limit-battery-charge-ubuntu/](https://ubuntuhandbook.org/index.php/2024/02/limit-battery-charge-ubuntu/)
* ASUS Linux(asusctl) 매뉴얼/아카이브:
  [https://asus-linux.org/manual/asusctl-manual/](https://asus-linux.org/manual/asusctl-manual/)
  [https://wiki.archlinux.org/title/Asusctl](https://wiki.archlinux.org/title/Asusctl)
* TLP 배터리 케어(임계값 개념/설정):
  [https://linrunner.de/tlp/faq/battery.html](https://linrunner.de/tlp/faq/battery.html)
* GNOME 확장(Battery Health Charging – 모델 지원 시):
  [https://extensions.gnome.org/extension/5724/battery-health-charging/](https://extensions.gnome.org/extension/5724/battery-health-charging/)
* 관련 Q\&A/사례(참고):
  [https://askubuntu.com/questions/1526046/setting-the-battery-charge-threshold-in-ubuntu-24-04-lts](https://askubuntu.com/questions/1526046/setting-the-battery-charge-threshold-in-ubuntu-24-04-lts)

---

## 라이선스

* 본 문서/스크립트: MIT

## 변경이력

* v0.1.0 (초판): 기본 CLI + 부팅/절전 자동 재적용 제공
