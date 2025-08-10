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
    
    Args:
        key: 設定キー
        default: デフォルト値
        
    Returns:
        設定値またはデフォルト値
    """
    # 1. 環境変数を優先
    value = os.getenv(key)
    if value:
        return value
    
    # 2. Streamlit Secretsを確認
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        # Streamlit Secretsが利用できない場合は無視
        pass
    
    # 3. デフォルト値を返す
    return default


def is_streamlit_cloud() -> bool:
    """
    Streamlit Cloud環境かどうかを判定
    
    Returns:
        Streamlit Cloud環境の場合True
    """
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
    
    # Streamlit Secretsが利用可能かどうかもチェック
    try:
        return hasattr(st, 'secrets') and bool(st.secrets)
    except Exception:
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
    
    # 設定状況の確認
    client_id, client_secret, refresh_token = get_google_credentials()
    openai_key = get_openai_api_key()
    
    st.sidebar.write("**設定状況**:")
    st.sidebar.write(f"- Google Client ID: {'✅' if client_id else '❌'}")
    st.sidebar.write(f"- Google Client Secret: {'✅' if client_secret else '❌'}")
    st.sidebar.write(f"- Google Refresh Token: {'✅' if refresh_token else '❌'}")
    st.sidebar.write(f"- OpenAI API Key: {'✅' if openai_key else '❌'}")
    
    if is_cloud and not all([client_id, client_secret, openai_key]):
        st.sidebar.warning("⚠️ Streamlit Cloud Secretsで設定を確認してください")
