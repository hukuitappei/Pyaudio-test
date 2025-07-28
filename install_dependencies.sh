#!/bin/bash

# PyAudio依存関係のインストールスクリプト
echo "PyAudio依存関係をインストールしています..."

# システムパッケージの更新
sudo apt-get update

# PortAudioとその他の必要なライブラリをインストール
sudo apt-get install -y \
    portaudio19-dev \
    python3-dev \
    build-essential \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0

echo "依存関係のインストールが完了しました"
echo "次に、PyAudioをインストールしてください:"
echo "pip install pyaudio" 