#!/bin/bash

# 再接続を試みるSSIDのリスト（必要に応じて追加・変更）
TARGET_SSIDS=("***SSIDを設定***")

# チェックするネットワークインターフェース名（例: wlan0）
WIFI_INTERFACE="***ネットワークインターフェースを設定***"

# 接続確認と再接続試行のループ
while true; do
    # 現在の接続状態をチェック
    if nmcli -t -f DEVICE,STATE device status | grep "^${WIFI_INTERFACE}:connected" > /dev/null; then
        echo "Wi‑Fiは接続済みです。"
	break
    else
        echo "Wi‑Fi接続がありません。再接続を試みます..."

        # 各SSIDに対して再接続を試みる
        for ssid in "${TARGET_SSIDS[@]}"; do
            echo "SSID: $ssid への接続を試行中..."
            nmcli device wifi connect "$ssid" ifname "$WIFI_INTERFACE"
            # 接続に成功したらループを抜ける
            if nmcli -t -f DEVICE,STATE device status | grep "^${WIFI_INTERFACE}:connected" > /dev/null; then
                echo "$ssid に接続しました。"
                break
            fi
        done
    fi

    # 一定間隔をおいて再チェック（例: 60秒）
    sleep 3
done