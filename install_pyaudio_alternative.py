#!/usr/bin/env python3
"""
PyAudioの代替インストール方法
"""

import subprocess
import sys
import os

def install_pyaudio_alternative():
    """PyAudioの代替インストール方法を実行"""
    
    print("PyAudioの代替インストール方法を試行します...")
    
    # 方法1: pipwinを使用（Windows環境）
    try:
        print("1. pipwinを使用してPyAudioをインストール...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pipwin"])
        subprocess.check_call([sys.executable, "-m", "pipwin", "install", "pyaudio"])
        print("✅ pipwinを使用したインストールが成功しました")
        return True
    except subprocess.CalledProcessError:
        print("❌ pipwinでのインストールが失敗しました")
    
    # 方法2: condaを使用
    try:
        print("2. condaを使用してPyAudioをインストール...")
        subprocess.check_call(["conda", "install", "-c", "conda-forge", "pyaudio", "-y"])
        print("✅ condaを使用したインストールが成功しました")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ condaでのインストールが失敗しました")
    
    # 方法3: 事前ビルドされたwheelを使用
    try:
        print("3. 事前ビルドされたwheelを使用...")
        # プラットフォームに応じたwheelをダウンロード
        import platform
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == "linux":
            wheel_url = f"https://www.lfd.uci.edu/~gohlke/pythonlibs/pyaudio-0.2.11-cp310-cp310-{machine}.whl"
        else:
            wheel_url = f"https://www.lfd.uci.edu/~gohlke/pythonlibs/pyaudio-0.2.11-cp310-cp310-{machine}.whl"
        
        subprocess.check_call([sys.executable, "-m", "pip", "install", wheel_url])
        print("✅ 事前ビルドされたwheelでのインストールが成功しました")
        return True
    except subprocess.CalledProcessError:
        print("❌ 事前ビルドされたwheelでのインストールが失敗しました")
    
    print("❌ すべての代替方法が失敗しました")
    print("システムライブラリのインストールが必要です")
    return False

if __name__ == "__main__":
    install_pyaudio_alternative() 