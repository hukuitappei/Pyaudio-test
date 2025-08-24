# Streamlit Cloud Google認証ガイド

## 概要

Streamlit Cloudでは、ブラウザベースのOAuth認証フローが制限されているため、特別な認証方法が必要です。このガイドでは、Streamlit Cloud環境でGoogle Calendar認証を設定する方法を説明します。

## 認証方法

### 方法1: ローカル環境での認証（推奨）

#### 手順1: ローカル環境での認証実行
1. ローカル環境でアプリケーションを実行
   ```bash
   streamlit run streamlit_app.py
   ```

2. 設定タブでGoogle認証を実行
3. 認証URLをクリックしてGoogle認証画面を開く
4. 認証コードを入力して認証を完了
5. 表示されたリフレッシュトークンをコピー

#### 手順2: Streamlit Cloud Secretsへの設定
1. Streamlit Cloudのダッシュボードにアクセス
2. アプリケーションの設定画面を開く
3. Secrets設定で以下の内容を追加：

```toml
OPENAI_API_KEY = "your-openai-api-key"
GOOGLE_CLIENT_ID = "your-google-client-id"
GOOGLE_CLIENT_SECRET = "your-google-client-secret"
GOOGLE_REFRESH_TOKEN = "your-refresh-token-from-local-auth"
```

#### 手順3: アプリケーションの再起動
1. Streamlit Cloudでアプリケーションを再起動
2. 認証が正常に動作することを確認

### 方法2: 手動での認証URL生成

#### 手順1: 認証URLの生成
1. Streamlit Cloudでアプリケーションを実行
2. 設定タブでGoogle認証を実行
3. 生成された認証URLを新しいタブで開く

#### 手順2: 認証の完了
1. Googleアカウントでログイン
2. 権限を許可
3. 表示された認証コードをアプリケーションに入力
4. リフレッシュトークンを取得

#### 手順3: Secrets設定
1. 取得したリフレッシュトークンをStreamlit Cloud Secretsに設定
2. アプリケーションを再起動

### 方法3: 既存のリフレッシュトークンの使用

既にリフレッシュトークンをお持ちの場合は、直接Streamlit Cloud Secretsに設定できます。

## Google Cloud Console設定

### OAuth 2.0クライアントIDの作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. プロジェクトを選択または作成
3. 「APIとサービス」→「認証情報」を開く
4. 「認証情報を作成」→「OAuth 2.0クライアントID」を選択
5. アプリケーションの種類で「ウェブアプリケーション」を選択
6. 承認済みのリダイレクトURIに以下を追加：
   - `urn:ietf:wg:oauth:2.0:oob`
   - `http://localhost:8501`
   - `https://your-app-name.streamlit.app`

### Google Calendar APIの有効化

1. 「APIとサービス」→「ライブラリ」を開く
2. 「Google Calendar API」を検索
3. APIを有効化

## トラブルシューティング

### よくある問題

#### 1. 認証URLが生成されない
- **原因**: Client IDまたはClient Secretが正しく設定されていない
- **解決**: Streamlit Cloud Secretsの設定を確認

#### 2. リフレッシュトークンが取得できない
- **原因**: 認証スコープに'offline_access'が含まれていない
- **解決**: 認証時に「オフラインアクセス」を許可する

#### 3. 認証エラーが発生する
- **原因**: リダイレクトURIが正しく設定されていない
- **解決**: Google Cloud ConsoleでリダイレクトURIを確認

#### 4. Streamlit Cloudで認証が動作しない
- **原因**: Streamlit Cloudの制限によりブラウザ認証ができない
- **解決**: ローカル環境で認証を実行してリフレッシュトークンを取得

### デバッグ情報

アプリケーションでは以下のデバッグ情報が表示されます：

- 認証情報の設定状況
- 認証URLの生成結果
- セッション状態の確認
- エラーの詳細情報

## セキュリティ注意事項

1. **リフレッシュトークンの保護**: リフレッシュトークンは機密情報です。適切に管理してください
2. **Secrets設定**: Streamlit Cloud Secretsを使用して機密情報を管理
3. **アクセス権限**: 必要最小限の権限のみを要求
4. **定期的な更新**: リフレッシュトークンは定期的に更新することを推奨

## 設定確認

認証が正常に設定されているか確認する方法：

1. 設定タブでGoogle認証情報の設定状況を確認
2. タスク管理またはカレンダー管理でGoogle認証を実行
3. 認証状態が「認証済み」と表示されることを確認

## サポート

問題が解決しない場合は、以下を確認してください：

1. Google Cloud Consoleの設定
2. Streamlit Cloud Secretsの設定
3. アプリケーションのログ
4. デバッグ情報の詳細

---

**注意**: このガイドはStreamlit Cloud環境でのGoogle認証に特化しています。ローカル環境での認証方法は異なる場合があります。
