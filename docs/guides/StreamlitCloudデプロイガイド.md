# Streamlit Cloud デプロイガイド（Googleカレンダー連携対応）

## 概要

音声録音・文字起こしアプリケーションをStreamlit Cloudにデプロイし、Web上でGoogleカレンダー連携機能を使用する方法を説明します。

## 前提条件

- GitHubアカウント
- Streamlit Cloudアカウント
- Google Cloud Consoleでの設定完了
- ローカルでのGoogleカレンダー認証完了

## デプロイ手順

### 1. GitHubリポジトリの準備

#### 1.1 機密ファイルの除外設定
`.gitignore`ファイルに以下を追加：

```gitignore
# Google認証情報
credentials.json
token.pickle

# Streamlit Secrets（ローカル用）
.streamlit/secrets.toml

# 環境変数
.env

# その他の機密ファイル
*.key
*.pem
```

#### 1.2 リポジトリにプッシュ
```bash
git add .
git commit -m "Googleカレンダー連携機能を追加"
git push origin main
```

### 2. Streamlit Cloudでのデプロイ

#### 2.1 アプリケーションの作成
1. [Streamlit Cloud](https://share.streamlit.io/)にアクセス
2. 「New app」をクリック
3. GitHubリポジトリを選択
4. メインファイルパス: `streamlit_app.py`
5. 「Deploy!」をクリック

#### 2.2 Secrets設定
1. デプロイ後、「Settings」→「Secrets」をクリック
2. 以下の内容を追加：

```toml
# OpenAI API設定
OPENAI_API_KEY = "sk-proj-your-openai-api-key-here"

# Google認証情報
GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-client-secret"
GOOGLE_REFRESH_TOKEN = "your-refresh-token"
```

### 3. Google Cloud Consoleでの設定

#### 3.1 OAuth同意画面の更新
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 「APIとサービス」→「OAuth同意画面」
3. 「承認済みドメイン」に以下を追加：
   - `share.streamlit.io`
   - `your-app-name-xxxxx-xxxxx.streamlit.app`

#### 3.2 認証情報の更新
1. 「APIとサービス」→「認証情報」
2. OAuth 2.0クライアントIDを編集
3. 「承認済みのリダイレクトURI」に以下を追加：
   - `https://your-app-name-xxxxx-xxxxx.streamlit.app/_stcore/authorize`

### 4. デプロイ後の確認

#### 4.1 アプリケーションの動作確認
1. Streamlit Cloudでアプリケーションにアクセス
2. タスク管理タブでGoogleカレンダー認証状態を確認
3. タスクやイベントの追加・同期をテスト

#### 4.2 エラーの対処
- **認証エラー**: OAuth同意画面の設定を確認
- **API制限エラー**: Google Cloud ConsoleでAPI制限を確認
- **権限エラー**: 認証情報の権限設定を確認

## セキュリティ考慮事項

### 1. 認証情報の管理
- 本番環境では環境変数を使用
- 認証情報をGitリポジトリにコミットしない
- 定期的に認証情報を更新

### 2. アクセス制御
- 必要最小限の権限のみを要求
- ユーザーアクセスの監視
- 不要な権限の削除

### 3. データ保護
- 個人情報の適切な処理
- データの暗号化
- アクセスログの記録

## トラブルシューティング

### よくある問題

#### 1. 認証エラー
**症状**: 「Googleカレンダーが認証されていません」
**対処法**:
1. Streamlit Secretsの設定を確認
2. OAuth同意画面の承認済みドメインを確認
3. 認証情報の権限設定を確認

#### 2. API制限エラー
**症状**: 「API制限に達しました」
**対処法**:
1. Google Cloud ConsoleでAPI制限を確認
2. 必要に応じて制限を緩和
3. 使用量の監視

#### 3. デプロイエラー
**症状**: アプリケーションが起動しない
**対処法**:
1. ログを確認
2. 依存関係の確認
3. ファイルパスの確認

### デバッグ方法

#### 1. ログの確認
```bash
# Streamlit Cloudのログを確認
# アプリケーションの「Settings」→「Logs」で確認
```

#### 2. ローカルでのテスト
```bash
# ローカルでテストしてからデプロイ
streamlit run streamlit_app.py
```

#### 3. 段階的なデプロイ
1. 基本的な機能のみでデプロイ
2. 認証機能を追加
3. Googleカレンダー連携を追加

## パフォーマンス最適化

### 1. キャッシュの活用
```python
@st.cache_data
def load_calendar_data():
    # カレンダーデータの読み込み
    pass
```

### 2. 非同期処理
```python
# 重い処理は非同期で実行
import asyncio
```

### 3. エラーハンドリング
```python
try:
    # Googleカレンダー操作
    pass
except Exception as e:
    st.error(f"エラーが発生しました: {e}")
```

## 監視とメンテナンス

### 1. 定期的な確認
- アプリケーションの動作確認
- 認証情報の有効性確認
- API使用量の監視

### 2. 更新とメンテナンス
- 依存関係の更新
- セキュリティパッチの適用
- 機能の改善

### 3. バックアップ
- 設定ファイルのバックアップ
- データの定期バックアップ
- 復旧手順の準備

## まとめ

Streamlit Cloudでのデプロイにより、Web上でGoogleカレンダー連携機能を使用できます。適切な設定とセキュリティ対策により、安全で使いやすいWebアプリケーションを提供できます。

## 参考リンク

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Google Calendar API Documentation](https://developers.google.com/calendar)
- [Google Cloud Console](https://console.cloud.google.com/)
