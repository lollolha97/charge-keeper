#!/usr/bin/env bash
set -euo pipefail

readonly VERSION="0.1.0"

echo "=== 배터리 충전 임계값 지원 여부 확인 도구 v$VERSION ==="
echo

# 시스템 정보 수집
echo "🖥️  시스템 정보:"
echo "   OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "   커널: $(uname -r)"
echo "   아키텍처: $(uname -m)"

# DMI 정보 (제조사/모델)
if [[ -r /sys/class/dmi/id/sys_vendor && -r /sys/class/dmi/id/product_name ]]; then
    vendor=$(cat /sys/class/dmi/id/sys_vendor 2>/dev/null || echo "알 수 없음")
    model=$(cat /sys/class/dmi/id/product_name 2>/dev/null || echo "알 수 없음")
    echo "   제조사: $vendor"
    echo "   모델: $model"
fi

echo

# 전원 공급 장치 검색
echo "🔋 배터리 장치 검색:"
power_supply_dir="/sys/class/power_supply"
batteries=()

if [[ -d "$power_supply_dir" ]]; then
    for device in "$power_supply_dir"/*; do
        if [[ -f "$device/type" ]]; then
            device_type=$(cat "$device/type" 2>/dev/null || echo "")
            if [[ "$device_type" == "Battery" ]]; then
                device_name=$(basename "$device")
                batteries+=("$device_name")
                echo "   ✓ 발견: $device_name"
            fi
        fi
    done
else
    echo "   ❌ /sys/class/power_supply 디렉토리를 찾을 수 없습니다"
    exit 1
fi

if [[ ${#batteries[@]} -eq 0 ]]; then
    echo "   ❌ 배터리 장치를 찾을 수 없습니다"
    exit 1
fi

echo

# 각 배터리에 대한 충전 제어 지원 확인
supported_batteries=()
echo "⚡ 충전 임계값 제어 지원 확인:"

for bat in "${batteries[@]}"; do
    bat_path="$power_supply_dir/$bat"
    echo "   $bat 배터리:"
    
    # 종료 임계값 지원 확인
    end_threshold_file="$bat_path/charge_control_end_threshold"
    start_threshold_file="$bat_path/charge_control_start_threshold"
    
    if [[ -f "$end_threshold_file" ]]; then
        if [[ -r "$end_threshold_file" ]]; then
            current_end=$(cat "$end_threshold_file" 2>/dev/null || echo "읽기 실패")
            echo "      ✅ 충전 종료 임계값: 지원됨 (현재: ${current_end}%)"
            
            # 쓰기 권한 확인
            if [[ -w "$end_threshold_file" ]]; then
                echo "      ✅ 쓰기 권한: 있음"
            else
                echo "      ⚠️  쓰기 권한: 없음 (root 권한 필요)"
            fi
            
            supported_batteries+=("$bat")
        else
            echo "      ❌ 충전 종료 임계값: 읽기 불가"
        fi
    else
        echo "      ❌ 충전 종료 임계값: 지원되지 않음"
    fi
    
    # 시작 임계값 지원 확인 (옵션)
    if [[ -f "$start_threshold_file" ]]; then
        if [[ -r "$start_threshold_file" ]]; then
            current_start=$(cat "$start_threshold_file" 2>/dev/null || echo "읽기 실패")
            echo "      ✅ 충전 시작 임계값: 지원됨 (현재: ${current_start}%)"
        else
            echo "      ❌ 충전 시작 임계값: 읽기 불가"
        fi
    else
        echo "      ➖ 충전 시작 임계값: 지원되지 않음 (선택사항)"
    fi
    
    # 현재 배터리 상태
    if [[ -f "$bat_path/capacity" ]]; then
        capacity=$(cat "$bat_path/capacity" 2>/dev/null || echo "알 수 없음")
        echo "      📊 현재 용량: ${capacity}%"
    fi
    
    if [[ -f "$bat_path/status" ]]; then
        status=$(cat "$bat_path/status" 2>/dev/null || echo "알 수 없음")
        echo "      🔌 충전 상태: $status"
    fi
    echo
done

echo "📋 최종 결과:"
if [[ ${#supported_batteries[@]} -gt 0 ]]; then
    echo "   ✅ 지원되는 배터리: ${supported_batteries[*]}"
    echo "   ✅ a14-charge-keeper 사용 가능!"
    echo
    echo "💡 다음 단계:"
    echo "   1. sudo로 테스트: sudo sh -c 'echo 80 > $power_supply_dir/${supported_batteries[0]}/charge_control_end_threshold'"
    echo "   2. 확인: cat $power_supply_dir/${supported_batteries[0]}/charge_control_end_threshold"
    echo "   3. 원복: sudo sh -c 'echo 100 > $power_supply_dir/${supported_batteries[0]}/charge_control_end_threshold'"
    
    # 환경변수 제안
    if [[ "${supported_batteries[0]}" != "BAT0" ]]; then
        echo
        echo "⚠️  주의: 기본 배터리명이 BAT0이 아닙니다."
        echo "   a14-charge-keeper 사용 시 환경변수 지정 필요:"
        echo "   BAT_NAME=${supported_batteries[0]} a14-charge-keeper status"
    fi
else
    echo "   ❌ 지원되지 않는 시스템입니다"
    echo "   ❌ a14-charge-keeper 사용 불가"
    echo
    echo "💡 대안:"
    echo "   - BIOS/UEFI에서 배터리 보호 설정 확인"
    echo "   - 제조사별 도구 사용 (예: ASUS Armoury Crate, Lenovo Vantage)"
    echo "   - TLP 같은 전원 관리 도구의 배터리 기능 확인"
fi

# 기존 충전 관리 도구 감지
echo
echo "🔍 기존 배터리 관리 도구 확인:"
tools_found=false

# TLP 확인
if command -v tlp >/dev/null 2>&1; then
    if systemctl is-active --quiet tlp 2>/dev/null; then
        echo "   ⚠️  TLP가 실행 중입니다 (충돌 가능성)"
        tools_found=true
    else
        echo "   ➖ TLP 설치되어 있지만 비활성화됨"
    fi
fi

# auto-cpufreq 확인  
if command -v auto-cpufreq >/dev/null 2>&1; then
    echo "   ➖ auto-cpufreq 발견됨"
    tools_found=true
fi

# asusctl 확인
if command -v asusctl >/dev/null 2>&1; then
    echo "   ⚠️  asusctl 발견됨 (ASUS 공식 도구와 충돌 가능)"
    tools_found=true
fi

if ! $tools_found; then
    echo "   ✅ 충돌 가능한 도구 없음"
fi