# 🎤 音声録音＆文字起こしアプリ (sounddevice版)

Streamlit Cloud環境に対応した音声録音アプリケーションです。PyAudioの代わりにsounddeviceライブラリを使用して、クラウド環境でも動作する音声処理機能を実装しています。

## ✨ 主な機能

### 🎤 音声録音機能
- **sounddevice使用**: PyAudioの代替としてsounddeviceライブラリを使用
- **デバイス選択**: 利用可能な音声デバイスを自動検出・選択
- **録音時間設定**: 1秒〜300秒の範囲で録音時間を設定
- **音声ゲイン調整**: 録音音量の調整機能
- **マイクレベル監視**: 音声レベルをリアルタイムで監視

### 📊 音声分析機能
- **波形表示**: 録音した音声の波形を可視化
- **基本統計**: 平均値、標準偏差、最大値、最小値の表示
- **スペクトログラム**: 音声の周波数分析（scipy使用）

### 💾 ファイル管理機能
- **自動保存**: 録音完了時の自動ファイル保存
- **ダウンロード**: 録音ファイルのブラウザダウンロード
- **ファイル一覧**: 保存された録音ファイルの管理
- **ファイル削除**: 不要な録音ファイルの削除

### ⚙️ 設定管理機能
- **音声設定**: 録音時間、ゲイン、サンプルレートの設定
- **デバイス設定**: 録音デバイスの選択とテスト
- **UI設定**: 自動保存、高度なオプションの表示設定
- **設定保存**: 設定の永続化

## 🚀 インストールと実行

### 1. 依存関係のインストール
```bash
pip install -r requirements_sounddevice.txt
```

### 2. アプリケーションの実行
```bash
streamlit run app_sounddevice.py
```

## 📋 必要なライブラリ

- **streamlit**: Webアプリケーションフレームワーク
- **sounddevice**: 音声録音・再生ライブラリ
- **numpy**: 数値計算ライブラリ
- **matplotlib**: グラフ描画ライブラリ
- **scipy**: 科学技術計算ライブラリ
- **python-dotenv**: 環境変数管理

## 🔧 技術仕様

### 音声仕様
- **サンプルレート**: 44.1kHz
- **チャンネル数**: 1（モノラル）
- **ビット深度**: 16bit
- **ファイル形式**: WAV

### 対応環境
- **Streamlit Cloud**: クラウド環境での動作
- **ローカル環境**: Windows、macOS、Linux
- **ブラウザ**: Chrome、Firefox、Safari、Edge

## 🎯 使用方法

### 1. アプリケーション起動
```bash
streamlit run app_sounddevice.py
```

### 2. 録音デバイスの選択
- 設定ボタンをクリック
- デバイス設定タブで録音デバイスを選択
- マイクレベルテストでデバイスを確認

### 3. 録音の実行
- 録音時間を設定（1〜300秒）
- 録音開始ボタンをクリック
- 録音完了まで待機

### 4. 録音結果の確認
- 音声波形の表示
- 録音情報の確認
- ファイルのダウンロード

## 🔍 機能詳細

### SoundDeviceAudioProcessor クラス
```python
class SoundDeviceAudioProcessor:
    def __init__(self):
        self.sample_rate = 44100
        self.channels = 1
        self.dtype = np.int16
    
    def get_audio_devices(self):
        """利用可能な音声デバイスを取得"""
    
    def record_audio(self, duration, device_index=None, gain=1.0):
        """音声を録音する"""
    
    def monitor_audio_level(self, device_index=None, duration=3):
        """音声レベルを監視"""
    
    def save_audio_file(self, audio_data, sample_rate, filename):
        """音声データをWAVファイルとして保存"""
    
    def create_download_link(self, audio_data, sample_rate, filename):
        """音声ファイルのダウンロードリンクを生成"""
```

### SettingsManager クラス
```python
class SettingsManager:
    def __init__(self):
        self.settings_file = "settings/app_settings.json"
    
    def load_settings(self):
        """設定を読み込み"""
    
    def save_settings(self, settings):
        """設定を保存"""
```

## 🆚 元のapp.pyとの比較

| 機能 | app.py (PyAudio) | app_sounddevice.py (sounddevice) |
|------|------------------|----------------------------------|
| 音声録音 | ✅ | ✅ |
| デバイス選択 | ✅ | ✅ |
| 音声レベル監視 | ✅ | ✅ |
| ファイル保存 | ✅ | ✅ |
| 波形表示 | ✅ | ✅ |
| 設定管理 | ✅ | ✅ |
| Streamlit Cloud対応 | ❌ | ✅ |
| システムライブラリ依存 | 高 | 低 |
| インストール難易度 | 困難 | 簡単 |

## ⚠️ 制限事項

### Streamlit Cloud環境での制限
- **リアルタイム録音**: ブラウザベースの制限により、サーバーサイドでの録音は困難
- **音声認識**: Whisperなどの音声認識機能は別途実装が必要
- **マイクアクセス**: ブラウザの音声アクセス許可が必要

### 代替案
- **ファイルアップロード**: ユーザーが録音したファイルをアップロード
- **音声分析**: アップロードされたファイルの分析機能
- **ブラウザネイティブ**: HTML5 Audio APIの活用

## 🛠️ トラブルシューティング

### よくある問題

#### 1. 音声デバイスが見つからない
```bash
# システムの音声デバイスを確認
python -c "import sounddevice as sd; print(sd.query_devices())"
```

#### 2. 録音が失敗する
- マイクの音量設定を確認
- ブラウザの音声アクセス許可を確認
- 他のアプリケーションがマイクを使用していないか確認

#### 3. ファイル保存に失敗する
- recordingsディレクトリの権限を確認
- ディスク容量を確認

## 📚 参考資料

- [sounddevice Documentation](https://python-sounddevice.readthedocs.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)

## 🤝 貢献

バグ報告や機能要望は、GitHubのIssuesでお知らせください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。 