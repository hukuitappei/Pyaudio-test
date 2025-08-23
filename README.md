# 音声録音・文字起こしアプリケーション

音声録音、文字起こし、タスク管理、Googleカレンダー連携機能を備えたStreamlitアプリケーションです。

## 🌟 主な機能

- 🎤 **音声録音**: リアルタイム音声録音と保存
- 📝 **文字起こし**: OpenAI Whisperを使用した高精度文字起こし
- 📋 **タスク管理**: 音声から自動タスク抽出と管理
- 📅 **カレンダー管理**: イベント管理とGoogleカレンダー連携
- 🔄 **Googleカレンダー同期**: タスクとイベントの双方向同期
- 📚 **ユーザー辞書**: カスタム辞書機能
- ⚡ **コマンド管理**: カスタムコマンド実行
- 🎛️ **設定管理**: 詳細な設定オプション

## 🚀 デプロイ方法

### ローカル実行
```bash
# 依存関係のインストール
pip install -r requirements.txt

# アプリケーションの起動
streamlit run streamlit_app.py
```

### Webデプロイ（Streamlit Cloud）

#### 1. GitHubリポジトリの準備
```bash
git add .
git commit -m "Googleカレンダー連携機能を追加"
git push origin main
```

#### 2. Streamlit Cloudでのデプロイ
1. [Streamlit Cloud](https://share.streamlit.io/)にアクセス
2. 「New app」をクリック
3. GitHubリポジトリを選択
4. メインファイルパス: `streamlit_app.py`
5. 「Deploy!」をクリック

#### 3. Secrets設定
Streamlit Cloudの「Settings」→「Secrets」で以下を設定：

```toml
# OpenAI API設定
OPENAI_API_KEY = "sk-proj-your-openai-api-key-here"

# Google認証情報
GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-client-secret"
GOOGLE_REFRESH_TOKEN = "your-refresh-token"
```

#### 4. Google Cloud Console設定
- OAuth同意画面の承認済みドメインに`share.streamlit.io`を追加
- 認証情報のリダイレクトURIにStreamlit CloudのURLを追加

詳細な設定手順は[StreamlitCloudデプロイガイド](docs/StreamlitCloudデプロイガイド.md)を参照してください。

## ⚙️ 設定

### 必要な環境変数
- `OPENAI_API_KEY`: OpenAI APIキー
- `GOOGLE_CLIENT_ID`: Google OAuth 2.0クライアントID
- `GOOGLE_CLIENT_SECRET`: Google OAuth 2.0クライアントシークレット
- `GOOGLE_REFRESH_TOKEN`: Google認証リフレッシュトークン

### 設定ファイル
- `.streamlit/secrets.toml`: ローカル開発用の設定
- `settings/app_settings.json`: アプリケーション設定
- `settings/tasks.json`: タスクデータ
- `settings/calendar.json`: カレンダーデータ

## 📖 使用方法

### 1. 音声録音・文字起こし
1. 「録音」タブを開く
2. 録音デバイスを選択
3. 「録音開始」ボタンをクリック
4. 音声を録音
5. 「録音停止」ボタンをクリック
6. 「文字起こし」ボタンで文字起こし実行

### 2. タスク管理
1. 「タスク管理」タブを開く
2. 「➕ タスク追加」で新しいタスクを作成
3. 「Googleカレンダーに同期」でカレンダー連携
4. 「📅 カレンダー連携」で一括同期

### 3. カレンダー管理
1. 「カレンダー」タブを開く
2. 「➕ イベント追加」で新しいイベントを作成
3. 「Googleカレンダーに同期」でカレンダー連携
4. 「🔄 同期管理」で双方向同期

### 4. 音声からの自動生成
1. 音声を録音・文字起こし
2. 「📋 検出されたタスク」で「タスクとして保存」
3. 「📅 検出されたイベント」で「イベントとして保存」

## 🔧 技術仕様

### 使用技術
- **フロントエンド**: Streamlit
- **音声処理**: PyAudio
- **文字起こし**: OpenAI Whisper
- **AI処理**: OpenAI GPT
- **カレンダー連携**: Google Calendar API
- **データ保存**: JSON形式

### ファイル構成
```
streamlit-pyaudio-voice-record/
├── streamlit_app.py          # メインアプリケーション
├── settings_ui_audiorec.py   # 設定UI
├── utils_audiorec.py         # ユーティリティ
├── config_manager.py         # 設定管理
├── requirements.txt          # 依存関係
├── .streamlit/               # Streamlit設定
│   └── secrets.toml         # ローカル用設定
├── settings/                 # アプリケーション設定
│   ├── app_settings.json
│   ├── tasks.json
│   └── calendar.json
├── recordings/               # 録音ファイル
├── transcriptions/           # 文字起こし結果
└── docs/                     # ドキュメント
```

## 📚 ドキュメント

- [セットアップガイド](docs/セットアップガイド.md)
- [Googleカレンダー連携設定ガイド](docs/Googleカレンダー連携設定ガイド.md)
- [StreamlitCloudデプロイガイド](docs/StreamlitCloudデプロイガイド.md)
- [StreamlitSecrets設定ガイド](docs/StreamlitSecrets設定ガイド.md)
- [タスク管理・カレンダー連携改善報告書](docs/タスク管理・カレンダー連携改善報告書.md)

## 🔒 セキュリティ

- 認証情報は環境変数またはStreamlit Secretsで管理
- 機密ファイルは`.gitignore`で除外
- Google OAuth 2.0を使用した安全な認証
- 必要最小限の権限のみを要求

## 🐛 トラブルシューティング

### よくある問題

#### 1. 音声録音エラー
- マイクの権限を確認
- 録音デバイスが正しく選択されているか確認

#### 2. 文字起こしエラー
- OpenAI APIキーが正しく設定されているか確認
- インターネット接続を確認

#### 3. Googleカレンダー連携エラー
- Google認証情報が正しく設定されているか確認
- OAuth同意画面の設定を確認

詳細なトラブルシューティングは各ドキュメントを参照してください。

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 📞 サポート

問題や質問がある場合は、GitHubのIssuesで報告してください。

---

**注意**: このアプリケーションは音声データを処理します。プライバシーとセキュリティに注意してご利用ください。
