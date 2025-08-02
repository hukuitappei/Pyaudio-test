# 🎤 音声録音・文字起こしアプリ（拡張版）

Streamlit Cloud対応のブラウザベース音声録音・文字起こしアプリケーションです。`streamlit-audiorec`とOpenAI Whisper APIを使用し、豊富な設定機能を提供します。

## ✨ 主な機能

### 🎵 基本機能
- **ブラウザベース録音**: マイク権限を使用した録音
- **OpenAI Whisper API**: 高精度な文字起こし
- **ファイル管理**: 録音ファイルと文字起こし結果の保存・管理

### 🎛️ 拡張設定機能
- **音声設定**: 録音時間、ゲイン、サンプルレート、チャンネル数
- **デバイス設定**: マイク選択、デバイス情報表示
- **文字起こし設定**: Whisperモデル、言語、Temperature
- **UI設定**: 詳細オプション、自動保存、レベル監視
- **ショートカット設定**: キーボードショートカットのカスタマイズ

### 📚 ユーザー辞書
- **カテゴリ管理**: 技術用語、略語、カスタムなど
- **エントリ追加**: 用語、定義、発音の登録
- **統計情報**: カテゴリ数、エントリ数、最終更新日時

### ⚡ コマンド管理
- **カスタムコマンド**: 文字起こし結果の後処理
- **LLMプロンプト**: 処理内容のカスタマイズ
- **出力形式**: text、bullet_points、summary、text_file

## 🚀 セットアップ

### 1. 環境準備
```bash
# リポジトリをクローン
git clone <repository-url>
cd streamlit-pyaudio-voice-record

# 依存関係をインストール
pip install -r requirements.txt
```

### 2. APIキー設定
```bash
# 環境変数ファイルをコピー
cp env_example.txt .env

# .envファイルを編集してAPIキーを設定
# OPENAI_API_KEY=your_openai_api_key_here
```

### 3. アプリケーション起動
```bash
streamlit run app_audiorec.py
```

### 4. ブラウザでアクセス
アプリが起動したら、表示されるURL（通常は http://localhost:8501）にアクセスしてください。

## 📖 使用方法

### 基本録音・文字起こし
1. **🎤 録音・文字起こし**タブを選択
2. 録音ボタンをクリックして録音開始
3. 録音完了後、「🎙️ 文字起こし開始」をクリック
4. 文字起こし結果を確認・保存

### 拡張設定の利用
1. **⚙️ 拡張設定**タブを選択
2. 各設定タブで必要な設定を調整
   - **🎵 音声設定**: 録音パラメータの調整
   - **🎙️ デバイス設定**: マイク選択とデバイス情報
   - **📝 文字起こし設定**: Whisper設定と動作
   - **🔧 UI設定**: インターフェースのカスタマイズ
   - **⚡ ショートカット設定**: キーボードショートカット
3. 「💾 設定を保存」をクリック

### ユーザー辞書の活用
1. **📚 ユーザー辞書**タブを選択
2. 「➕ 新しいエントリを追加」で用語を登録
3. カテゴリ別に用語を管理

### コマンドの活用
1. **⚡ コマンド管理**タブを選択
2. 「➕ 新しいコマンドを追加」でカスタムコマンドを作成
3. 文字起こし結果の後処理に活用

## 📁 ファイル構成

```
streamlit-pyaudio-voice-record/
├── app_audiorec.py              # メインアプリケーション
├── utils_audiorec.py            # 統合ユーティリティクラス
├── settings_ui_audiorec.py      # 拡張設定UIコンポーネント
├── requirements.txt              # 依存関係
├── env_example.txt              # 環境変数テンプレート
├── README.md                    # このファイル
├── settings/
│   ├── app_settings.json        # アプリケーション設定
│   ├── user_dictionary.json     # ユーザー辞書
│   └── commands.json           # コマンド設定
├── recordings/                  # 録音ファイル保存先
└── transcriptions/             # 文字起こし結果保存先
```

## ⚙️ 設定ファイル詳細

### app_settings.json
```json
{
  "audio": {
    "duration": 10,
    "gain": 1.0,
    "sample_rate": 44100,
    "channels": 1,
    "chunk_size": 1024,
    "format": "paInt16"
  },
  "device": {
    "selected_device_index": 0,
    "selected_device_name": "Default Microphone",
    "auto_select_default": true,
    "test_device_on_select": false
  },
  "whisper": {
    "model_size": "base",
    "language": "ja",
    "temperature": 0.0,
    "compression_ratio_threshold": 2.4,
    "logprob_threshold": -1.0,
    "no_speech_threshold": 0.6,
    "condition_on_previous_text": false
  },
  "transcription": {
    "auto_transcribe": true,
    "save_transcriptions": true
  },
  "ui": {
    "show_advanced_options": false,
    "auto_save_recordings": true,
    "show_quality_analysis": false,
    "show_level_monitoring": false,
    "auto_start_recording": false,
    "auto_recording_threshold": 500,
    "auto_recording_delay": 0.5
  },
  "shortcuts": {
    "enabled": false,
    "global_hotkeys": false,
    "modifiers": {
      "ctrl": false,
      "shift": false,
      "alt": false
    },
    "keys": {
      "start_recording": "F9",
      "stop_recording": "F10",
      "transcribe": "F11",
      "clear_text": "F12",
      "save_recording": "Ctrl+S",
      "open_settings": "Ctrl+,",
      "open_dictionary": "Ctrl+D",
      "open_commands": "Ctrl+M"
    }
  }
}
```

### user_dictionary.json
```json
{
  "metadata": {
    "version": "1.0",
    "total_entries": 0,
    "last_updated": "2024-12-19T00:00:00Z"
  },
  "categories": {
    "技術用語": {
      "description": "技術的な専門用語",
      "entries": {}
    },
    "略語": {
      "description": "略語とその意味",
      "entries": {}
    },
    "カスタム": {
      "description": "ユーザー定義の用語",
      "entries": {}
    }
  }
}
```

### commands.json
```json
{
  "metadata": {
    "version": "1.0",
    "total_commands": 0,
    "last_updated": "2024-12-19T00:00:00Z"
  },
  "commands": {}
}
```

## 🔧 トラブルシューティング

### よくある問題

#### 1. PyAudioエラー
- **症状**: `OSError: [Errno -9999] Unanticipated host error`
- **解決策**: Windowsのマイク設定を確認、アプリにマイク権限を許可

#### 2. APIキーエラー
- **症状**: `Error code: 401 - Invalid API key`
- **解決策**: `.env`ファイルのAPIキーを確認、先頭の`=`文字を削除

#### 3. Streamlitエラー
- **症状**: `StreamlitDuplicateElementId`
- **解決策**: アプリケーションを再起動

#### 4. ファイル保存エラー
- **症状**: 録音ファイルや文字起こし結果が保存されない
- **解決策**: `recordings/`と`transcriptions/`ディレクトリの権限を確認

### デバッグ方法
1. **設定ページの診断**: 「⚙️ 拡張設定」→「🔧 システム診断」
2. **ログ確認**: ブラウザの開発者ツールでコンソールログを確認
3. **ファイル確認**: `settings/`ディレクトリの設定ファイルを確認

## 📝 開発情報

### 技術スタック
- **フロントエンド**: Streamlit
- **音声録音**: streamlit-audiorec
- **文字起こし**: OpenAI Whisper API
- **設定管理**: JSON + カスタムマネージャークラス
- **ファイル管理**: Python標準ライブラリ

### 依存関係
```
streamlit>=1.28.0
openai>=1.0.0
streamlit-audiorec>=0.1.3
python-dotenv>=1.0.0
```

### 開発環境
- **Python**: 3.8以上
- **OS**: Windows 10/11, macOS, Linux
- **ブラウザ**: Chrome, Firefox, Safari, Edge

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🙏 謝辞

- [Streamlit](https://streamlit.io/) - Webアプリケーションフレームワーク
- [streamlit-audiorec](https://github.com/Joooohan/streamlit-audiorec) - 音声録音コンポーネント
- [OpenAI Whisper](https://openai.com/research/whisper) - 音声認識API

---

**注意**: このアプリはブラウザのマイク権限を使用します。初回実行時にマイクへのアクセス許可が必要です。
