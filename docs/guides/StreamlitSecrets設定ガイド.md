# Streamlit Secrets設定ガイド

## 概要

このドキュメントでは、Streamlitアプリケーションで`st.secrets`オブジェクトを使用して`.toml`ファイルからシークレットキーを読み込む方法について説明します。

## 設定ファイルの構造

### `.streamlit/secrets.toml`

```toml
# Streamlit Secrets設定ファイル
# 全てのキーをルートレベルで統一

OPENAI_API_KEY = "your_openai_api_key_here"
GOOGLE_CLIENT_ID = "your_google_client_id_here"
GOOGLE_CLIENT_SECRET = "your_google_client_secret_here"

# Google認証用リフレッシュトークン（初回認証後に設定）
GOOGLE_REFRESH_TOKEN = "your_refresh_token_here"
```

## 設定の優先順位

アプリケーションは以下の順序で設定を読み込みます：

1. **Streamlit Secrets** (`.streamlit/secrets.toml`)
2. **環境変数** (`.env`ファイルまたはシステム環境変数)
3. **デフォルト値**

## 修正されたファイル

### 1. `config_manager.py`

- `get_secret()`関数を修正して`st.secrets`を優先的に使用
- `is_streamlit_cloud()`関数を改善
- `validate_secrets()`関数を追加
- `show_environment_info()`関数を改善

### 2. `streamlit_app.py`

- `setup_openai()`メソッドを修正して`st.secrets`を優先的に使用
- `main()`関数に設定検証機能を追加

### 3. `utils_audiorec.py`

- `_create_credentials_from_env()`メソッドを修正して`st.secrets`を優先的に使用

### 4. `setup_google_auth.py`

- `setup_environment_variables()`関数を修正して`.streamlit/secrets.toml`ファイルも作成
- `check_current_settings()`関数を修正して`.streamlit/secrets.toml`ファイルも確認

## 使用方法

### 1. ローカル開発環境

```bash
# 設定スクリプトを実行
python setup_google_auth.py

# または手動で.streamlit/secrets.tomlを作成
mkdir -p .streamlit
# .streamlit/secrets.tomlファイルを編集
```

### 2. Streamlit Cloud

1. ローカルの`.streamlit/secrets.toml`ファイルの内容をコピー
2. Streamlit CloudのSecrets設定に貼り付け
3. アプリケーションをデプロイ

## 設定の確認

### アプリケーション内での確認

アプリケーションのサイドバーに環境情報が表示されます：

- 環境（ローカル/Streamlit Cloud）
- 設定状況（OpenAI API、Google Client ID）
- Streamlit Secretsの利用状況

### コマンドラインでの確認

```bash
python setup_google_auth.py
# メニューから「3. 設定の確認」を選択
```

## エラーハンドリング

### 設定不足時のエラー

必要な設定が不足している場合、アプリケーションは以下のエラーメッセージを表示します：

```
⚠️ 必要な設定が不足しています: OPENAI_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
📝 .streamlit/secrets.tomlファイルまたは環境変数で設定してください。
```

### Streamlit Secrets読み込みエラー

Streamlit Secretsの読み込みに失敗した場合、警告メッセージが表示され、環境変数にフォールバックします。

## セキュリティ

### ローカル開発

- `.streamlit/secrets.toml`は`.gitignore`に含まれているため、Gitにコミットされません
- 機密情報はローカル環境でのみ管理されます

### Streamlit Cloud

- Streamlit Cloud Secretsは暗号化されて保存されます
- アプリケーションのログには機密情報が出力されません

## トラブルシューティング

### よくある問題

1. **設定が読み込まれない**
   - `.streamlit/secrets.toml`ファイルの形式を確認
   - キー名が正しいか確認

2. **Streamlit Cloudで設定が反映されない**
   - Streamlit Cloud Secretsの設定を確認
   - アプリケーションを再デプロイ

3. **認証エラー**
   - APIキーの有効性を確認
   - 必要な権限が付与されているか確認

### デバッグ方法

```python
# デバッグ用コード
import streamlit as st

# 設定値の確認（機密情報は一部マスク）
if hasattr(st, 'secrets'):
    st.write("Streamlit Secrets利用可能")
    for key in st.secrets.keys():
        value = st.secrets[key]
        if 'KEY' in key or 'SECRET' in key or 'TOKEN' in key:
            st.write(f"{key}: {'*' * len(value)}")
        else:
            st.write(f"{key}: {value}")
else:
    st.write("Streamlit Secrets利用不可")
```

## まとめ

この修正により、Streamlitアプリケーションは以下の利点を得られます：

1. **統一された設定管理**: `.toml`ファイルによる一元管理
2. **環境別対応**: ローカル開発とStreamlit Cloudの両方に対応
3. **セキュリティ向上**: 機密情報の適切な管理
4. **エラーハンドリング**: 設定不足時の適切なエラー表示
5. **デバッグ支援**: 設定状況の可視化

設定が完了したら、アプリケーションを起動して正常に動作することを確認してください。
