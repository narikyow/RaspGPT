#!/bin/bash

# pyenv の環境変数とパスを設定
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

# pyenv を初期化
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# 指定の仮想環境を有効化
pyenv shell RaspGPT

# スクリプト実行ディレクトリに移動
cd /home/***自分のユーザー名***/RaspGPT

# Python スクリプトを実行
python button_shutdown.py