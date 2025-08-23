# Streamlit Cloud デプロイメントガイド

## 🚀 概要

音声録音・文字起こしアプリをStreamlit Cloudにデプロイするための完全ガイド

## 📁 ファイル構造

### 現在の構造（Streamlit Cloud対応）

```
プロジェクトルート/
├── app_audiorec.py              # ← Streamlit Cloudメインファイル
├── utils_audiorec.py            # ← 依存関係
├── settings_ui_audiorec.py      # ← UI コンポーネント
├── config_manager.py            # ← 設定管理
├── streamlit_app.py             # ← 代替エントリーポイント
├── requirements.txt             # ← 依存関係定義
│
├── src/                         # ← 開発用ソースコード
│   ├── app_audiorec.py          # ← 開発版
│   ├── utils_audiorec.py        # ← 開発版
│   ├── settings_ui_audiorec.py  # ← 開発版
│   └── config_manager.py        # ← 開発版
│
├── .streamlit/
│   ├── config.toml              # ← Streamlit設定
│   └── secrets.toml             # ← ローカル機密情報（.gitignoreで除外）
│
├── settings/                    # ← 設定・データファイル
├── docs/                        # ← ドキュメント
└── ...
```

## ⚙️ Streamlit Cloud 設定

### 1. リポジトリ設定
- **メインファイル**: `app_audiorec.py` (ルートディレクトリ)
- **代替ファイル**: `streamlit_app.py` (利用可能)
- **Python バージョン**: Python 3.8+

### 2. 必要な設定ファイル

#### requirements.txt ✅
```
streamlit>=1.28.0
streamlit-audiorec>=0.1.3
openai>=1.0.0
google-api-python-client>=2.0.0
google-auth-httplib2>=0.2.0
google-auth-oauthlib>=1.0.0
python-dotenv>=1.0.0
numpy>=1.24.0
```

#### .streamlit/config.toml ✅
```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## 🔐 Streamlit Cloud Secrets設定

### Secrets設定（Streamlit Cloud ダッシュボード）

```toml
# OpenAI設定
OPENAI_API_KEY = "sk-proj-your_openai_api_key_here"

# Google OAuth設定
GOOGLE_CLIENT_ID = "your_client_id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-your_client_secret"

# Google認証用リフレッシュトークン（初回認証後に設定）
GOOGLE_REFRESH_TOKEN = "your_refresh_token_here"
```

## 🛠️ デプロイ手順

### Step 1: GitHubリポジトリの準備

```bash
# 変更をコミット
git add .
git commit -m "Streamlit Cloud deployment ready"
git push origin main
```

### Step 2: Streamlit Cloud設定

1. [Streamlit Cloud](https://share.streamlit.io/)にアクセス
2. GitHubアカウントでログイン
3. "New app"をクリック
4. リポジトリを選択
5. **Main file path**: `app_audiorec.py` を指定
6. "Deploy!"をクリック

### Step 3: Secrets設定

1. Streamlit Cloud ダッシュボードでアプリを選択
2. "Settings" → "Secrets"タブ
3. 上記のSecrets設定をコピー＆ペースト
4. "Save"をクリック

### Step 4: デプロイ確認

1. アプリが正常に起動することを確認
2. サイドバーの「🔧 環境情報」で設定状況を確認
3. 音声録音機能をテスト
4. Google認証をテスト

## 🚨 よくあるエラーと解決方法

### エラー1: "Main module does not exist"
```
❗️ The main module file does not exist: /mount/src/project/app_audiorec.py
```

**解決方法**:
- `app_audiorec.py`がルートディレクトリにあることを確認
- ファイル名の大文字小文字を確認
- GitHubにファイルがプッシュされていることを確認

### エラー2: "ModuleNotFoundError"
```
ModuleNotFoundError: No module named 'utils_audiorec'
```

**解決方法**:
- 依存ファイル(`utils_audiorec.py`, `settings_ui_audiorec.py`, `config_manager.py`)がルートディレクトリにあることを確認
- インポートパスが正しいことを確認

### エラー3: "Secrets not found"
```
KeyError: 'OPENAI_API_KEY'
```

**解決方法**:
- Streamlit Cloud SecretsでAPIキーが設定されていることを確認
- キー名が正確であることを確認（大文字小文字区別）

### エラー4: "Google authentication failed"
```
❌ Google認証に失敗しました
```

**解決方法**:
- Google Cloud ConsoleでOAuth2.0認証情報を確認
- リダイレクトURIに `https://your-app-url.streamlit.app` を追加
- GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRETが正しく設定されていることを確認

## 🔧 ローカル開発との違い

| 項目 | ローカル開発 | Streamlit Cloud |
|------|-------------|----------------|
| **メインファイル** | `src/app_audiorec.py` | `app_audiorec.py` (ルート) |
| **設定管理** | `.env`ファイル | Streamlit Secrets |
| **ファイル永続化** | 可能 | 制限あり |
| **Google認証** | ファイルベース可能 | 環境変数のみ |

## 📊 デプロイメント後の確認項目

### ✅ チェックリスト

- [ ] アプリが正常に起動
- [ ] サイドバーに「🔧 環境情報」が表示
- [ ] OpenAI API Key: ✅ 表示
- [ ] Google Client ID/Secret: ✅ 表示
- [ ] 音声録音機能が動作
- [ ] 文字起こし機能が動作
- [ ] Google認証フローが動作
- [ ] タスク・イベント管理が動作

### 🎯 パフォーマンス確認

- [ ] 初回読み込み時間 < 10秒
- [ ] 音声録音の遅延 < 1秒
- [ ] 文字起こし処理時間 < 30秒
- [ ] UI応答性が良好

## 🔄 アップデート手順

1. ローカルで変更・テスト
2. `src/`ディレクトリで開発
3. 動作確認後、ルートディレクトリにコピー
4. GitHubにプッシュ
5. Streamlit Cloudが自動デプロイ

## 📚 関連ドキュメント

- [Streamlit Secrets設定ガイド](./streamlit_secrets_guide.md)
- [セキュリティ設定ガイド](./セキュリティ設定ガイド.md)
- [セットアップガイド](./セットアップガイド.md)
- [プロジェクト構造](./プロジェクト構造.md)
