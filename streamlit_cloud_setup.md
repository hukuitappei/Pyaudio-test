# Streamlit Cloud デプロイメントガイド

## 🌐 Streamlit Cloud対応の追加設定

### 1. Secrets設定（必須）

Streamlit Cloud管理画面で以下のsecretsを設定：

```toml
# Streamlit Cloud > Settings > Secrets
GOOGLE_CLIENT_ID = "your_google_client_id"
GOOGLE_CLIENT_SECRET = "your_google_client_secret"
GOOGLE_REFRESH_TOKEN = "your_refresh_token"
OPENAI_API_KEY = "your_openai_api_key"
```

### 2. Google Cloud Console設定の修正

**重要**: OAuth2設定でWebアプリケーション用に変更が必要

1. **Google Cloud Console**:
   - アプリケーションの種類を「Webアプリケーション」に変更
   - 承認済みリダイレクトURIに追加:
     ```
     https://your-app-name.streamlit.app/
     urn:ietf:wg:oauth:2.0:oob
     ```

### 3. 初回認証手順（WEB環境）

1. **ローカルで初回認証を実行**:
   ```bash
   python setup_google_auth.py
   ```

2. **取得したリフレッシュトークンをStreamlit Cloudに設定**:
   - Streamlit Cloud管理画面 > Settings > Secrets
   - `GOOGLE_REFRESH_TOKEN` に設定

3. **アプリをデプロイ**:
   - GitHubにプッシュ
   - Streamlit Cloudで自動デプロイ

### 4. ファイル永続化の制限事項

⚠️ **重要な制限**:
- Streamlit Cloudではファイルが永続化されません
- アプリ再起動時に以下が失われます:
  - 録音ファイル (`recordings/`)
  - 文字起こし結果 (`transcriptions/`)
  - 設定ファイル (`settings/`)

**対策オプション**:
1. **セッション状態のみ使用** (現在の実装)
2. **外部ストレージ連携** (要追加実装)
3. **データベース連携** (要追加実装)

## 🛠️ 追加の環境変数対応

現在の実装は `os.getenv()` を使用していますが、Streamlit Cloudでは `st.secrets` も対応する必要があります。
