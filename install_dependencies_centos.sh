#!/bin/bash

# CentOS/RHEL系でのPyAudio依存関係インストールスクリプト
echo "PyAudio依存関係をインストールしています..."

# EPELリポジトリの有効化
sudo yum install -y epel-release

# 必要なライブラリをインストール
sudo yum install -y \
    portaudio-devel \
    python3-devel \
    gcc \
    gcc-c++ \
    make \
    alsa-lib-devel

echo "依存関係のインストールが完了しました"
echo "次に、PyAudioをインストールしてください:"
echo "pip install pyaudio" 