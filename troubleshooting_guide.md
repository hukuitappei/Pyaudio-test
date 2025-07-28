# PyAudioインストール問題のトラブルシューティングガイド

## 問題の概要
PyAudioのインストール時に `portaudio.h: No such file or directory` エラーが発生する問題です。

## 原因
- PortAudioライブラリがシステムにインストールされていない
- 必要な開発ライブラリが不足している
- コンパイラがPortAudioヘッダーファイルを見つけられない

## 解決方法

### 1. Ubuntu/Debian系Linux
```bash
# システムパッケージの更新
sudo apt-get update

# 必要なライブラリをインストール
sudo apt-get install -y \
    portaudio19-dev \
    python3-dev \
    build-essential \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0

# PyAudioをインストール
pip install pyaudio
```

### 2. CentOS/RHEL系Linux
```bash
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

# PyAudioをインストール
pip install pyaudio
```

### 3. macOS
```bash
# Homebrewを使用
brew install portaudio

# PyAudioをインストール
pip install pyaudio
```

### 4. Windows
```bash
# pipwinを使用
pip install pipwin
pipwin install pyaudio
```

### 5. 代替方法

#### condaを使用
```bash
conda install -c conda-forge pyaudio
```

#### 事前ビルドされたwheelを使用
```bash
# Python 3.10用のwheelをダウンロード
pip install https://www.lfd.uci.edu/~gohlke/pythonlibs/pyaudio-0.2.11-cp310-cp310-win_amd64.whl
```

## 確認方法
インストール後、以下のコマンドで確認できます：
```python
import pyaudio
print("PyAudioが正常にインストールされました")
```

## よくある問題

### 1. 権限エラー
```bash
# sudoを使用してインストール
sudo pip install pyaudio
```

### 2. 仮想環境での問題
```bash
# 仮想環境をアクティベートしてからインストール
source venv/bin/activate
pip install pyaudio
```

### 3. Docker環境での問題
Dockerfileに必要なライブラリを追加：
```dockerfile
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-dev \
    build-essential
```

## 参考リンク
- [PyAudio公式ドキュメント](https://people.csail.mit.edu/hubert/pyaudio/)
- [PortAudio公式サイト](http://www.portaudio.com/) 