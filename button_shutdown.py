from gpiozero import Button
import os
import time

# GPIOの設定
BUTTON_GPIO = Button(18, pull_up=True)

def main():
    try:
        while True:
            # ボタンが押されているかチェック
            if BUTTON_GPIO.is_pressed:
                print("ボタンが押されました。システムを再起動します。")
                time.sleep(1)  # 誤作動防止のためのディレイ
                os.system("sudo shutdown -h now")
            time.sleep(0.2)  # ループの遅延
    except KeyboardInterrupt:
        print("プログラムを終了します。")

if __name__ == "__main__":
    main()
