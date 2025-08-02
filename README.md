# 🎤 音声録音・文字起こしアプリ

Streamlit Cloud対応の音声録音・文字起こしアプリケーションです。複数の実装方法を提供しています。

## 🚀 実装バージョン

### 1. HTML5版 (`app.py`)
- **HTML5 Audio API + Web Speech API**を使用
- ブラウザネイティブの音声認識
- サーバーサイド処理不要
- 無料で使用可能

### 2. streamlit-audiorec版 (`app_audiorec.py`) - **推奨**
- **streamlit-audiorec + OpenAI Whisper API**を使用
- 高精度な文字起こし
- 日本語対応
- 自動言語検出

## 🛠️ インストール

### 必要な環境
- Python 3.8以上
- Streamlit Cloud対応
- モダンブラウザ（Chrome、Firefox、Safari、Edge）

### 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 🔒 セキュリティ設定（重要）

#### APIキーの管理
1. **環境変数ファイルの作成**:
   ```bash
   # env_example.txtを.envにコピー
   cp env_example.txt .env
   ```

2. **APIキーの設定**:
   `.env`ファイルを編集して実際のAPIキーを設定:
   ```env
   OPENAI_API_KEY=your_actual_openai_api_key
   ```

## 🎯 使用方法

### HTML5版の実行
```bash
streamlit run app.py
```

### streamlit-audiorec版の実行（推奨）
```bash
streamlit run app_audiorec.py
```

## 📋 機能比較

| 機能 | HTML5版 | streamlit-audiorec版 |
|------|---------|---------------------|
| 録音 | ✅ HTML5 Audio API | ✅ streamlit-audiorec |
| 文字起こし | ✅ Web Speech API | ✅ OpenAI Whisper API |
| 精度 | 中 | 高 |
| コスト | 無料 | 有料（API使用量） |
| サーバー処理 | 不要 | 必要 |
| 日本語対応 | ✅ | ✅ |

## 🎤 主な機能

### 🎤 録音機能
- **ブラウザベース録音**: HTML5 Audio APIまたはstreamlit-audiorec
- **自動録音時間**: 設定可能な録音時間（1-30秒）
- **リアルタイム再生**: 録音完了後の即座再生
- **ダウンロード機能**: WAV形式での録音ファイルダウンロード
- **Streamlit Cloud対応**: クラウド環境での完全動作

### 🎙️ 文字起こし機能
- **高精度文字起こし**: OpenAI Whisper API使用
- **日本語対応**: 完全な日本語音声認識
- **自動言語検出**: 多言語対応
- **句読点自動挿入**: 自然な文章生成
- **結果保存**: テキストファイルでの保存

### ⚙️ 設定機能
- **🎤 録音設定**: 録音時間、ゲイン設定
- **📁 ファイル管理**: 録音ファイルの一覧表示と削除
- **🎨 UI設定**: 表示オプション、ファイル保存設定
- **📝 文字起こし設定**: 自動文字起こし、結果保存設定

## 🔧 トラブルシューティング

### 文字起こしが動作しない場合
1. **OpenAI APIキーの確認**
   - `.env`ファイルに正しいAPIキーが設定されているか確認
   - APIキーが有効かどうか確認

2. **ブラウザの確認**
   - Chrome、Edge、Firefoxなどのモダンブラウザを使用
   - マイク権限が許可されているか確認

3. **ネットワーク接続**
   - インターネット接続が安定しているか確認
   - ファイアウォール設定を確認

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 貢献

バグ報告や機能要望は、GitHubのIssuesでお知らせください。
