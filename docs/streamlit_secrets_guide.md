# Streamlit Secrets設定ガイド

## 🔐 概要

このアプリケーションはStreamlit Cloud環境でのセキュアな設定管理のため、`.streamlit/secrets.toml`ファイルを使用します。

## 📁 設定ファイルの場所

```
プロジェクトルート/
└── .streamlit/
    └── secrets.toml  # ← このファイルに機密情報を設定
```

## ⚙️ 設定形式

### 推奨設定（統一形式）

```toml
# Streamlit Secrets設定ファイル
# 全てのキーをルートレベルで統一

OPENAI_API_KEY = "sk-proj-your_openai_api_key_here"
GOOGLE_CLIENT_ID = "your_google_client_id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-your_google_client_secret"

# Google認証用リフレッシュトークン（初回認証後に設定）
GOOGLE_REFRESH_TOKEN = "your_refresh_token_here"
```

### ❌ 避けるべき形式（ネスト構造）

```toml
# この形式は使わないでください
[openai]
api_key = "sk-proj-..."

[google]
client_id = "..."
client_secret = "..."
```

## 🔧 アプリケーションでの使用方法

### config_manager.pyでの取得

```python
from src.config_manager import get_secret

# 設定値の取得
openai_key = get_secret('OPENAI_API_KEY')
client_id = get_secret('GOOGLE_CLIENT_ID')
client_secret = get_secret('GOOGLE_CLIENT_SECRET')
refresh_token = get_secret('GOOGLE_REFRESH_TOKEN')
```

### 優先順位

1. **環境変数** (最優先)
2. **Streamlit Secrets** (.streamlit/secrets.toml)
3. **デフォルト値** (None)

## 🚀 Streamlit Cloud デプロイ時の設定

### 1. リポジトリの準備
- `.streamlit/secrets.toml`は.gitignoreで除外されています
- 機密情報をGitにコミットしないでください

### 2. Streamlit Cloud での設定
1. Streamlit Cloud のダッシュボードにアクセス
2. アプリケーション設定 → "Secrets"タブ
3. 以下の形式で設定を入力：

```toml
OPENAI_API_KEY = "sk-proj-your_key_here"
GOOGLE_CLIENT_ID = "your_client_id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-your_secret"
GOOGLE_REFRESH_TOKEN = "your_refresh_token"
```

## 🔍 設定確認方法

### 1. テストスクリプトの実行

```bash
streamlit run test_secrets.py
```

### 2. アプリケーション内での確認

アプリケーション実行時、サイドバーの「🔧 環境情報」セクションで設定状況を確認できます。

### 3. 設定状況の表示例

```
🔧 環境情報
環境: ☁️ Streamlit Cloud

設定状況:
- Google Client ID: ✅
- Google Client Secret: ✅  
- Google Refresh Token: ❌ 未設定（初回認証後に設定）
- OpenAI API Key: ✅
```

## 🛡️ セキュリティ

### ✅ 安全な設定
- `.streamlit/secrets.toml`は.gitignoreで除外
- Streamlit Cloud Secretsを使用
- 環境変数での管理

### ❌ 危険な設定
- ソースコードにAPIキーをハードコーディング
- publicリポジトリにsecrets.tomlをコミット
- プレーンテキストでの機密情報共有

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. "OpenAI APIキーが設定されていません"
```bash
# 確認方法
streamlit run test_secrets.py

# 解決方法
# secrets.tomlでOPENAI_API_KEYを確認
```

#### 2. "Google認証に失敗しました"
```bash
# 確認項目
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- GOOGLE_REFRESH_TOKEN（初回認証後）
```

#### 3. "st.secretsが利用できません"
- ローカル環境では.streamlit/secrets.tomlが必要
- Streamlit Cloud環境ではSecrets設定が必要

## 📚 関連ドキュメント

- [セットアップガイド](./セットアップガイド.md)
- [セキュリティ設定ガイド](./セキュリティ設定ガイド.md)
- [Streamlit Cloud設定](./streamlit_cloud_setup.md)
