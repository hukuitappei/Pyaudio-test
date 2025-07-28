# Streamlit Cloud環境での音声処理ガイド

## 🚨 Streamlit Cloud環境の制限事項

### 制限される機能
- **PyAudio**: システムライブラリ（PortAudio）が必要なため使用不可
- **システムライブラリのインストール**: `sudo`権限がないため不可
- **音声デバイスへの直接アクセス**: ブラウザベースの制限
- **リアルタイム録音**: サーバーサイドでの録音は不可

### 利用可能な代替手段
- **sounddevice**: ブラウザベースの音声処理
- **pydub**: 音声ファイル処理
- **librosa**: 音声分析
- **Web Audio API**: ブラウザネイティブ機能

## 🛠️ Streamlit Cloud対応の実装方法

### 1. 代替ライブラリの使用

#### sounddevice（推奨）
```python
import sounddevice as sd
import numpy as np

# 録音（ブラウザ環境では制限あり）
recording = sd.rec(int(duration * sample_rate), 
                   samplerate=sample_rate, 
                   channels=1)
```

#### pydub（音声ファイル処理）
```python
from pydub import AudioSegment
from pydub.playback import play

# 音声ファイルの読み込みと処理
audio = AudioSegment.from_wav("audio.wav")
```

### 2. ブラウザベースの音声処理

#### HTML5 Audio APIの活用
```python
import streamlit as st

# ブラウザネイティブの音声録音
st.markdown("""
<script>
// ブラウザでの音声録音実装
const mediaRecorder = new MediaRecorder(stream);
</script>
""", unsafe_allow_html=True)
```

### 3. ファイルアップロード機能

#### 音声ファイルのアップロード
```python
uploaded_file = st.file_uploader("音声ファイルをアップロード", 
                                 type=['wav', 'mp3', 'm4a'])

if uploaded_file is not None:
    # アップロードされたファイルを処理
    audio_bytes = uploaded_file.read()
    # 音声処理ロジック
```

## 📋 Streamlit Cloud対応のrequirements.txt

```txt
streamlit>=1.28.0
sounddevice>=0.4.6
numpy>=1.21.0
pydub>=0.25.1
librosa>=0.10.0
scipy>=1.7.0
matplotlib>=3.5.0
plotly>=5.0.0
```

## 🔧 実装例

### 1. 音声ファイルアップロードアプリ
```python
import streamlit as st
from pydub import AudioSegment
import io

def process_uploaded_audio(uploaded_file):
    """アップロードされた音声ファイルを処理"""
    audio = AudioSegment.from_file(uploaded_file)
    
    # 音声情報を表示
    st.write(f"長さ: {len(audio)/1000:.2f}秒")
    st.write(f"サンプルレート: {audio.frame_rate}Hz")
    st.write(f"チャンネル数: {audio.channels}")
    
    return audio
```

### 2. 音声分析アプリ
```python
import librosa
import matplotlib.pyplot as plt

def analyze_audio(audio_file):
    """音声ファイルを分析"""
    y, sr = librosa.load(audio_file)
    
    # スペクトログラム
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    
    fig, ax = plt.subplots()
    img = librosa.display.specshow(D, y_axis='linear', x_axis='time', ax=ax)
    ax.set_title('スペクトログラム')
    fig.colorbar(img, ax=ax, format="%+2.f dB")
    
    return fig
```

## ⚠️ 注意事項

### 1. ブラウザの制限
- **HTTPS必須**: 音声アクセスにはHTTPSが必要
- **ユーザー許可**: マイクアクセスにはユーザーの許可が必要
- **セキュリティ制限**: 一部の音声機能は制限される

### 2. パフォーマンス
- **ファイルサイズ**: 大きな音声ファイルは処理に時間がかかる
- **メモリ使用量**: 音声データはメモリを大量に使用
- **ネットワーク**: アップロード/ダウンロードに時間がかかる

### 3. 代替案
- **ローカル開発**: PyAudioを使用したローカル環境での開発
- **Docker**: ローカルでDockerコンテナを使用
- **VPS**: 独自サーバーでのデプロイ

## 🚀 デプロイ手順

### 1. Streamlit Cloudでのデプロイ
1. GitHubリポジトリにコードをプッシュ
2. Streamlit Cloudでリポジトリを接続
3. `streamlit_requirements.txt`を指定
4. デプロイ実行

### 2. 設定ファイル
```toml
# .streamlit/config.toml
[server]
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

## 📚 参考リソース

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [sounddevice Documentation](https://python-sounddevice.readthedocs.io/)
- [pydub Documentation](https://github.com/jiaaro/pydub)
- [librosa Documentation](https://librosa.org/) 