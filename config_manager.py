"""
Streamlit Cloud対応の設定管理ユーティリティ
環境変数とStreamlit Secretsの両方に対応
"""

import os
import streamlit as st
from typing import Optional


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    環境変数またはStreamlit Secretsから値を取得
    Streamlit Secretsを優先して使用
    
    Args:
        key: 設定キー
        default: デフォルト値
        
    Returns:
        設定値またはデフォルト値
    """
    # 1. Streamlit Secretsを優先（.tomlファイルから読み込み）
    try:
        if hasattr(st, 'secrets') and st.secrets is not None:
            if key in st.secrets:
                value = st.secrets[key]
                if value and value.strip():  # 空でないことを確認
                    return value
    except Exception as e:
        st.warning(f"Streamlit Secretsの読み込みエラー: {e}")
    
    # 2. 環境変数を確認
    value = os.getenv(key)
    if value and value.strip():
        return value
    
    # 3. デフォルト値を返す
    return default


def is_streamlit_cloud() -> bool:
    """
    Streamlit Cloud環境かどうかを判定
    
    Returns:
        Streamlit Cloud環境の場合True
    """
    # Streamlit Secretsが利用可能かどうかを最優先でチェック
    try:
        if hasattr(st, 'secrets') and st.secrets is not None:
            return True
    except Exception:
        pass
    
    # Streamlit Cloud特有の環境変数をチェック
    streamlit_cloud_indicators = [
        'STREAMLIT_SHARING',
        'STREAMLIT_CLOUD',
        'HOSTNAME'  # Streamlit Cloudでは特定のホスト名パターン
    ]
    
    for indicator in streamlit_cloud_indicators:
        value = os.getenv(indicator)
        if value:
            # HOSTNAMEの場合はStreamlit Cloudのパターンをチェック
            if indicator == 'HOSTNAME' and 'streamlit' in value.lower():
                return True
            elif indicator != 'HOSTNAME':
                return True
    
    return False


def get_google_credentials() -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Google認証情報を取得
    
    Returns:
        (client_id, client_secret, refresh_token)のタプル
    """
    client_id = get_secret('GOOGLE_CLIENT_ID')
    client_secret = get_secret('GOOGLE_CLIENT_SECRET') 
    refresh_token = get_secret('GOOGLE_REFRESH_TOKEN')
    
    return client_id, client_secret, refresh_token


def get_openai_api_key() -> Optional[str]:
    """
    OpenAI APIキーを取得
    
    Returns:
        OpenAI APIキー
    """
    return get_secret('OPENAI_API_KEY')


def show_environment_info() -> None:
    """
    現在の環境情報を表示（デバッグ用）
    """
    st.sidebar.write("### 🔧 環境情報")
    
    is_cloud = is_streamlit_cloud()
    st.sidebar.write(f"**環境**: {'☁️ Streamlit Cloud' if is_cloud else '💻 ローカル'}")
    
    # 設定値の確認（機密情報は一部マスク）
    openai_key = get_openai_api_key()
    google_client_id = get_secret('GOOGLE_CLIENT_ID')
    
    st.sidebar.write("**設定状況**:")
    st.sidebar.write(f"OpenAI API: {'✅ 設定済み' if openai_key else '❌ 未設定'}")
    st.sidebar.write(f"Google Client ID: {'✅ 設定済み' if google_client_id else '❌ 未設定'}")
    
    # Streamlit Secretsの利用状況
    try:
        if hasattr(st, 'secrets') and st.secrets is not None:
            st.sidebar.write("**Secrets**: ✅ 利用可能")
        else:
            st.sidebar.write("**Secrets**: ❌ 利用不可")
    except Exception:
        st.sidebar.write("**Secrets**: ❌ エラー")


def validate_secrets() -> bool:
    """
    必要なシークレットが設定されているかチェック
    
    Returns:
        必要な設定が揃っている場合True
    """
    required_secrets = [
        'OPENAI_API_KEY',
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET'
    ]
    
    missing_secrets = []
    for secret in required_secrets:
        if not get_secret(secret):
            missing_secrets.append(secret)
    
    if missing_secrets:
        st.error(f"⚠️ 必要な設定が不足しています: {', '.join(missing_secrets)}")
        st.info("📝 `.streamlit/secrets.toml`ファイルまたは環境変数で設定してください。")
        return False
    
    return True
