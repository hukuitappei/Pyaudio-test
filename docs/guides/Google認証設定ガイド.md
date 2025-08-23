# Google認証設定ガイド

## 概要
このガイドでは、StreamlitアプリでGoogleカレンダー連携を使用するためのGoogle認証設定について説明します。

## 前提条件
- Googleアカウント
- Google Cloud Consoleへのアクセス権限

## 設定手順

### 1. Google Cloud Consoleでの設定

#### 1.1 プロジェクトの作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成または既存のプロジェクトを選択

#### 1.2 Google Calendar APIの有効化
1. 「APIとサービス」→「ライブラリ」を選択
2. 「Google Calendar API」を検索して有効化

#### 1.3 OAuth 2.0クライアントIDの作成
1. 「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「OAuth 2.0クライアントID」を選択
3. アプリケーションの種類で「ウェブアプリケーション」を選択
4. 以下の設定を行う：
   - **名前**: 任意の名前（例：「Streamlit Calendar App」）
   - **承認済みのリダイレクトURI**: `urn:ietf:wg:oauth:2.0:oob`
5. 「作成」をクリック

#### 1.4 認証情報の取得
作成後、以下の情報が表示されます：
- **クライアントID**
- **クライアントシークレット**

これらの情報をメモしておいてください。

### 2. Streamlit Secretsの設定

#### 2.1 ローカル環境の場合
`.streamlit/secrets.toml`ファイルを作成し、以下の内容を追加：

```toml
GOOGLE_CLIENT_ID = "your-client-id-here"
GOOGLE_CLIENT_SECRET = "your-client-secret-here"
GOOGLE_REFRESH_TOKEN = ""  # 初回認証後に設定
```

#### 2.2 Streamlit Cloudの場合
1. Streamlit Cloudのダッシュボードにアクセス
2. アプリケーションを選択
3. 「Settings」→「Secrets」を選択
4. 以下の内容を追加：

```toml
GOOGLE_CLIENT_ID = "your-client-id-here"
GOOGLE_CLIENT_SECRET = "your-client-secret-here"
GOOGLE_REFRESH_TOKEN = ""  # 初回認証後に設定
```

### 3. 初回認証の実行

#### 3.1 アプリケーションの起動
1. Streamlitアプリを起動
2. タスク管理機能にアクセス
3. Googleカレンダー連携を有効化

#### 3.2 認証手順
1. 「Google認証画面を開く」ボタンをクリック
2. Googleアカウントでログイン
3. 権限を許可
4. 表示された認証コードをコピー
5. アプリケーションの認証コード入力欄に貼り付け
6. 「認証を完了」をクリック

#### 3.3 リフレッシュトークンの設定
認証完了後、リフレッシュトークンが表示されます：
1. 表示されたリフレッシュトークンをコピー
2. Streamlit Secretsに`GOOGLE_REFRESH_TOKEN`として設定
3. アプリケーションを再起動

## トラブルシューティング

### 認証URLがNoneと表示される場合

#### 原因
- `GOOGLE_CLIENT_ID`または`GOOGLE_CLIENT_SECRET`が設定されていない
- 認証情報の形式が間違っている
- Google Cloud Consoleでの設定が不完全

#### 解決方法
1. **設定の確認**
   ```python
   # アプリケーションで設定状況を確認
   from config.config_manager import show_google_credentials_status
   show_google_credentials_status()
   ```

2. **認証情報の再設定**
   - Google Cloud ConsoleでOAuth 2.0クライアントIDを再作成
   - Streamlit Secretsを更新
   - アプリケーションを再起動

3. **認証フローのリセット**
   - アプリケーションで「認証フローをリセット」ボタンをクリック
   - 再度認証手順を実行

### その他のよくある問題

#### 「認証フローの初期化に失敗しました」
- 認証情報が正しく設定されているか確認
- Google Cloud ConsoleでAPIが有効化されているか確認
- ネットワーク接続を確認

#### 「リフレッシュトークンが取得できませんでした」
- 認証時に適切な権限を許可したか確認
- 認証コードを正しく入力したか確認
- 再度認証手順を実行

## セキュリティ注意事項

### 認証情報の管理
- クライアントシークレットは絶対に公開しない
- リフレッシュトークンは安全に保管
- 定期的に認証情報を更新

### 権限の最小化
- 必要最小限の権限のみを要求
- 不要になった権限は削除

## 設定確認方法

### アプリケーション内での確認
```python
# 設定状況の表示
from config.config_manager import show_google_credentials_status
show_google_credentials_status()

# デバッグ情報の取得
from config.config_manager import get_debug_info
debug_info = get_debug_info()
```

### 手動での確認
1. Streamlit Secretsの内容を確認
2. 環境変数の設定を確認
3. Google Cloud Consoleでの設定を確認

## 更新とメンテナンス

### 定期的な確認
- 認証情報の有効期限を確認
- APIの使用量を監視
- セキュリティ設定の見直し

### 認証情報の更新
- リフレッシュトークンの有効期限が切れた場合
- セキュリティ上の理由で更新が必要な場合
- 上記の初回認証手順を再度実行

## サポート

問題が解決しない場合は、以下を確認してください：
1. エラーメッセージの詳細
2. 設定状況の確認結果
3. Google Cloud Consoleでの設定状況

詳細なログやエラーメッセージがあれば、より具体的な解決方法を提供できます。
