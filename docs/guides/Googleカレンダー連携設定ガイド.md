# Googleカレンダー連携設定ガイド

## 概要

このガイドでは、音声録音・文字起こしアプリケーションでGoogleカレンダーとの連携を設定する方法を説明します。

## 前提条件

- Googleアカウント
- Google Cloud Consoleへのアクセス権限
- Streamlitアプリケーションの実行環境

## 設定手順

### 1. Google Cloud Consoleでの設定

#### 1.1 プロジェクトの作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成または既存のプロジェクトを選択
3. プロジェクト名を記録（例：`voice-recorder-calendar`）

#### 1.2 Google Calendar APIの有効化
1. 左側のメニューから「APIとサービス」→「ライブラリ」を選択
2. 検索バーで「Google Calendar API」を検索
3. 「Google Calendar API」を選択して「有効にする」をクリック

#### 1.3 OAuth 2.0認証情報の作成
1. 「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「OAuth 2.0 クライアントID」を選択
3. アプリケーションの種類で「デスクトップアプリケーション」を選択
4. 名前を入力（例：`Voice Recorder Calendar Integration`）
5. 「作成」をクリック

#### 1.4 認証情報のダウンロード
1. 作成されたOAuth 2.0クライアントIDをクリック
2. 「JSONをダウンロード」をクリック
3. ダウンロードしたJSONファイルを`credentials.json`として保存

### 2. ローカル環境での設定

#### 2.1 認証情報ファイルの配置
```bash
# プロジェクトルートディレクトリに配置
mv ~/Downloads/client_secret_*.json credentials.json
```

#### 2.2 初回認証の実行
```bash
python setup_google_auth.py
```

初回実行時は以下の手順が表示されます：
1. ブラウザが開き、Googleアカウントでの認証を求められます
2. アプリケーションにカレンダーへのアクセス権限を許可
3. 認証コードをコピーしてターミナルに貼り付け
4. 認証が完了すると`token.pickle`ファイルが作成されます

### 3. Streamlit Secretsの設定

#### 3.1 ローカル開発環境
`.streamlit/secrets.toml`ファイルに以下を追加：

```toml
# Google認証情報
GOOGLE_CLIENT_ID = "your_client_id_here"
GOOGLE_CLIENT_SECRET = "your_client_secret_here"
GOOGLE_REFRESH_TOKEN = "your_refresh_token_here"
```

#### 3.2 Streamlit Cloud環境
1. Streamlit Cloudのダッシュボードにアクセス
2. アプリケーションを選択
3. 「Settings」→「Secrets」を選択
4. 上記のTOML形式で認証情報を追加

### 4. 認証情報の取得方法

#### 4.1 Client IDとClient Secret
- ダウンロードした`credentials.json`ファイルから取得
- またはGoogle Cloud Consoleの認証情報ページで確認

#### 4.2 Refresh Token
```bash
# 初回認証後に自動生成される
python setup_google_auth.py
```

## 使用方法

### 1. タスクのGoogleカレンダー同期

#### 1.1 タスク追加時の自動同期
1. タスク管理タブを開く
2. 「➕ タスク追加」タブを選択
3. タスク情報を入力
4. 「Googleカレンダーに同期」チェックボックスを有効化
5. 「タスクを追加」ボタンをクリック

#### 1.2 既存タスクの同期
1. 「📝 タスク一覧」タブを開く
2. 同期したいタスクの「📅 カレンダー同期」ボタンをクリック

#### 1.3 一括同期
1. 「📅 カレンダー連携」タブを開く
2. 「📅 未同期タスクをカレンダーに同期」ボタンをクリック

### 2. イベントのGoogleカレンダー同期

#### 2.1 イベント追加時の自動同期
1. カレンダー管理タブを開く
2. 「➕ イベント追加」タブを選択
3. イベント情報を入力
4. 「Googleカレンダーに同期」チェックボックスを有効化
5. 「イベントを追加」ボタンをクリック

#### 2.2 既存イベントの同期
1. 「📊 イベント一覧」タブを開く
2. 同期したいイベントの「📅 カレンダー同期」ボタンをクリック

### 3. Googleカレンダーからの取得

#### 3.1 タスクとして取得
1. 「📅 カレンダー連携」タブを開く
2. 「🔄 Googleカレンダーからタスクを取得」ボタンをクリック

#### 3.2 イベントとして取得
1. 「🔄 同期管理」タブを開く
2. 「🔄 Googleカレンダーからイベントを取得」ボタンをクリック

## トラブルシューティング

### よくある問題

#### 1. 認証エラー
**症状**: 「Googleカレンダーが認証されていません」エラー
**対処法**:
1. `credentials.json`ファイルが正しく配置されているか確認
2. `python setup_google_auth.py`を再実行
3. 認証情報が正しく設定されているか確認

#### 2. 権限エラー
**症状**: 「権限がありません」エラー
**対処法**:
1. Google Cloud ConsoleでGoogle Calendar APIが有効化されているか確認
2. OAuth同意画面でスコープが正しく設定されているか確認
3. アプリケーションにカレンダーへのアクセス権限を許可

#### 3. 同期エラー
**症状**: タスクやイベントの同期に失敗
**対処法**:
1. インターネット接続を確認
2. Googleカレンダーが利用可能か確認
3. 認証トークンが有効か確認（必要に応じて再認証）

### デバッグ方法

#### 1. 認証状態の確認
```python
# アプリケーション内で確認
# タスク管理タブまたはカレンダー管理タブで認証状態が表示されます
```

#### 2. ログの確認
```bash
# アプリケーション実行時のログを確認
streamlit run streamlit_app.py
```

#### 3. 設定ファイルの確認
```bash
# 認証情報ファイルの存在確認
ls -la credentials.json
ls -la token.pickle

# Streamlit Secretsファイルの確認
cat .streamlit/secrets.toml
```

## セキュリティ注意事項

### 1. 認証情報の管理
- `credentials.json`と`token.pickle`ファイルは`.gitignore`に追加
- 認証情報をGitリポジトリにコミットしない
- 本番環境では環境変数またはStreamlit Secretsを使用

### 2. アクセス権限
- 必要最小限の権限のみを要求
- 定期的にアクセス権限を見直し
- 不要になった場合は権限を削除

### 3. トークンの更新
- リフレッシュトークンは定期的に更新
- トークンの有効期限を監視
- セキュリティ上の理由でトークンを無効化する場合は再認証が必要

## 高度な設定

### 1. 複数カレンダーの管理
```python
# 特定のカレンダーIDを指定
calendar_id = "your_calendar_id@group.calendar.google.com"
```

### 2. カスタムイベント設定
```python
# イベントの詳細設定
event_data = {
    'title': 'カスタムイベント',
    'description': '詳細な説明',
    'start_date': '2025-01-26T10:00:00',
    'end_date': '2025-01-26T11:00:00',
    'all_day': False,
    'location': '会議室A',
    'attendees': ['user@example.com']
}
```

### 3. 繰り返しイベント
```python
# 繰り返しイベントの設定
event_data = {
    'title': '定例会議',
    'start_date': '2025-01-26T10:00:00',
    'end_date': '2025-01-26T11:00:00',
    'recurrence': ['RRULE:FREQ=WEEKLY;COUNT=10']
}
```

## まとめ

このガイドに従って設定を行うことで、音声録音・文字起こしアプリケーションからGoogleカレンダーへのタスク・イベント同期が可能になります。

設定が完了したら、以下の機能が利用可能になります：

1. **タスクの自動同期**: タスク追加時にGoogleカレンダーに自動でイベントとして同期
2. **イベントの自動同期**: イベント追加時にGoogleカレンダーに自動で同期
3. **双方向同期**: Googleカレンダーからタスク・イベントを取得
4. **一括同期**: 未同期のタスク・イベントを一括で同期

何か問題が発生した場合は、トラブルシューティングセクションを参照してください。
