# RaspGPT

# RaspGPT: 無課金スマートスピーカーの作成プロセス

大学の講義「ICT実践」において、Raspberry Piを活用して無課金スマートスピーカーを作成しました。本プロジェクトの全プロセスを記録します。

## 概要

手順はQiitaの方に詳しく書いています。

https://qiita.com/kyoupattulan/items/ee889f8f6929a4e832c7


### 何をつくるの？
![スマートスピーカーの概要図](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3984207/071c1138-6224-0b8f-a758-56b9953830f7.png)

Geminiとfaster-whisperを利用し、無課金で運用できるスマートスピーカーを作ります。

- ChatGPT APIのクレジット購入ができなかったため、Geminiの無料枠を使用。
- ChatGPT APIと通信するコード（modules/GPT.py）は動作の確認が不十分のため注意。
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

## 今回目指したこと

**実用的なスマートスピーカーを目指して以下の特徴を持たせました。**

- ローカルで文字起こし
- Geminiとの通信
- スプレッドシートへの記録とメール送信
- GPIOピンによる操作
- 起動時の自動実行とプログラム再起動
- Wi-Fi自動再接続

**詳細な手順やコードについてはリポジトリやQiitaの記事をご確認ください。**
