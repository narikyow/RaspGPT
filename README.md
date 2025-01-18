# RaspGPT

# RaspGPT: 無課金スマートスピーカーの作成プロセス

大学の講義「ICT実践」において、Raspberry Piを活用して無課金スマートスピーカーを作成しました。本プロジェクトの全プロセスを記録します。

## 概要

手順はQiitaの方に詳しく書いています。



### 何をつくるの？
![スマートスピーカーの概要図](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3984207/071c1138-6224-0b8f-a758-56b9953830f7.png)

Geminiとfaster-whisperを利用し、無課金で運用できるスマートスピーカーを作ります。

- ChatGPT APIのクレジット購入ができなかったため、Geminiの無料枠を使用。
- ChatGPT APIを想定して設計していたため、一部の機能（DeepL翻訳など）が未完成。
- スマートスピーカーとの会話はGoogleスプレッドシートに記録され、メールで送信されます。

![全体の処理フロー](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3984207/86f30ca3-dfa5-8ec3-484b-64b3d22a4535.png)

本プロジェクトはMITライセンスで公開しています。

## 使用機器
- **Raspberry Pi 5 (8GBモデル)**
- **USBスピーカー**: サンワサプライ MM-SPU218K  
  [Amazonリンク](https://www.amazon.co.jp/dp/B0CKKW6Z32)
- **USBマイク**: MillSO  
  [Amazonリンク](https://www.amazon.co.jp/dp/B0CHTVQK9D/)

## 実行環境
- **OS**: Raspberry Pi OS 64bit
- **Python**: 3.9.21
- **仮想環境管理**: pyenvを使用

---

## 環境構築

### 1. pyenvのインストールと設定
以下の手順でpyenvをインストールします。

```bash
curl https://pyenv.run | bash
```

`.bashrc`に以下を追加してパスを設定します。

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
```

変更を反映します。

```bash
source ~/.bashrc
```

Python 3.9.21をインストールし、仮想環境を作成します。

```bash
pyenv install 3.9.21
pyenv virtualenv 3.9.21 RaspGPT
pyenv activate RaspGPT
```

### 2. 必要なライブラリのインストール
以下のコマンドで依存ライブラリをインストールします。

```bash
sudo apt install portaudio19-dev open-jtalk open-jtalk-mecab-naist-jdic hts-voice-nitech-jp-atr503-m001
```

Pythonライブラリは以下の`requirements.txt`を使用してインストールできます。

```txt
ctranslate2
faster-whisper
openai
gpiozero
requests
pyaudio
pyttsx3
google-generativeai
```

```bash
pip install -r requirements.txt
```

### 3. OpenJTalkの準備
デフォルト音声モデルを使用するか、必要に応じて追加音声モデル（例: MEI音声）をダウンロードしてください。

```bash
wget https://sourceforge.net/projects/mmdagent/files/MMDAgent_Example/MMDAgent_Example-1.6/MMDAgent_Example-1.6.zip
```

解凍後、`.htsvoice`ファイルを以下に移動します。

```bash
sudo mv path_to_htsvoice_file /usr/share/hts-voice/
```

`Main.py`内で使用するモデルを設定してください。

---

## Main.py 実行のための設定

リポジトリをクローンし、適切なディレクトリ構成で配置します。

```bash
git clone https://github.com/narikyow/RaspGPT ~/RaspGPT
```

### 1. APIキーの設定
`Main.py`の以下の部分にAPIキーを設定してください。

```python
API_KEY_DEEPL = "hogehoge_DEEPL"
API_KEY_GPT = None
API_KEY_GEMINI = "hogehoge_GEMINI"
GAS_URL = "hogehoge_GAS_URL"
```

### 2. USBマイクの設定
USBデバイス名を調べて`INPUT_DEVICE_INDEX`に設定します。

```bash
lsusb
```

`modules/Record.py`で対応するデバイス名を指定します。

### 3. Google SpreadSheetの設定
Googleスプレッドシートを作成し、以下のカラムを設定します。

```
Input | TranslatedInput | Response | DateTime
```

Google Apps Script (GAS) を利用してスプレッドシートへのデータ記録とメール送信を行います。GASのコードはリポジトリ内にあります。

---

## 自動実行の設定 (systemd)

`systemd`を使用してラズパイ起動時にプログラムを自動実行する設定を行います。

### 1. start_raspgpt.sh の設定
`start_raspgpt.sh`を編集し、必要な環境変数を設定します。

```bash
chmod +x start_raspgpt.sh
```

### 2. raspgpt.service の設定
以下の内容で`raspgpt.service`を作成します。

```ini
[Unit]
Description=Raspgpt Auto Start Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/RaspGPT
ExecStart=/home/your_username/RaspGPT/start_raspgpt.sh
Environment="XDG_RUNTIME_DIR"=/run/user/your_uid
Restart=always
RestartSec=7

[Install]
WantedBy=multi-user.target
```

設定を反映します。

```bash
sudo cp raspgpt.service /etc/systemd/system/raspgpt.service
sudo systemctl daemon-reload
sudo systemctl enable raspgpt.service
sudo systemctl start raspgpt.service
```

---

## 今回目指したこと

**実用的なスマートスピーカーを目指して以下の特徴を持たせました。**

- ローカルで文字起こし
- Geminiとの通信
- スプレッドシートへの記録とメール送信
- GPIOピンによる操作
- 起動時の自動実行とプログラム再起動
- Wi-Fi自動再接続

**詳細な手順やコードについてはリポジトリやQiitaの記事をご確認ください。**
