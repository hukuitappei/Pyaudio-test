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


def check_google_credentials() -> dict:
    """
    Google認証情報の設定状況を確認
    
    Returns:
        設定状況を示す辞書
    """
    client_id, client_secret, refresh_token = get_google_credentials()
    
    status = {
        'client_id': {
            'exists': bool(client_id),
            'value': client_id[:10] + '...' if client_id and len(client_id) > 10 else client_id
        },
        'client_secret': {
            'exists': bool(client_secret),
            'value': client_secret[:10] + '...' if client_secret and len(client_secret) > 10 else client_secret
        },
        'refresh_token': {
            'exists': bool(refresh_token),
            'value': refresh_token[:10] + '...' if refresh_token and len(refresh_token) > 10 else refresh_token
        },
        'all_required': bool(client_id and client_secret),
        'ready_for_auth': bool(client_id and client_secret and refresh_token)
    }
    
    return status


def show_google_credentials_status() -> None:
    """
    Google認証情報の設定状況を表示
    """
    status = check_google_credentials()
    
    st.subheader("🔐 Google認証情報の設定状況")
    
    # 各設定項目の状況を表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if status['client_id']['exists']:
            st.success("✅ GOOGLE_CLIENT_ID")
            st.caption(f"設定済み: {status['client_id']['value']}")
        else:
            st.error("❌ GOOGLE_CLIENT_ID")
            st.caption("未設定")
    
    with col2:
        if status['client_secret']['exists']:
            st.success("✅ GOOGLE_CLIENT_SECRET")
            st.caption(f"設定済み: {status['client_secret']['value']}")
        else:
            st.error("❌ GOOGLE_CLIENT_SECRET")
            st.caption("未設定")
    
    with col3:
        if status['refresh_token']['exists']:
            st.success("✅ GOOGLE_REFRESH_TOKEN")
            st.caption(f"設定済み: {status['refresh_token']['value']}")
        else:
            st.warning("⚠️ GOOGLE_REFRESH_TOKEN")
            st.caption("未設定（初回認証が必要）")
    
    # 全体状況の表示
    st.markdown("---")
    
    if status['all_required']:
        if status['ready_for_auth']:
            st.success("🎉 すべての認証情報が設定されています！")
        else:
            st.warning("⚠️ 基本認証情報は設定済みですが、リフレッシュトークンが未設定です")
            st.info("初回認証を実行してリフレッシュトークンを取得してください")
    else:
        st.error("❌ 必要な認証情報が不足しています")
        st.info("Google Cloud ConsoleでOAuth 2.0クライアントIDを作成し、設定してください")


def get_openai_api_key() -> Optional[str]:
    """
    OpenAI APIキーを取得
    
    Returns:
        OpenAI APIキー
    """
    return get_secret('OPENAI_API_KEY')


def show_environment_info() -> None:
    """
    環境情報を表示
    """
    st.subheader("🌍 環境情報")
    
    # Streamlit Cloud判定
    is_cloud = is_streamlit_cloud()
    if is_cloud:
        st.success("✅ Streamlit Cloud環境")
    else:
        st.info("💻 ローカル環境")
    
    # 主要な環境変数の確認
    st.markdown("### 設定状況")
    
    # Google認証情報の状況を表示
    try:
        show_google_credentials_status()
    except Exception as e:
        st.warning(f"Google認証情報の表示に失敗しました: {e}")
    
    # OpenAI APIキーの状況
    openai_key = get_openai_api_key()
    if openai_key:
        st.success("✅ OPENAI_API_KEY: 設定済み")
    else:
        st.error("❌ OPENAI_API_KEY: 未設定")


def get_debug_info() -> dict:
    """
    デバッグ情報を取得
    
    Returns:
        デバッグ情報の辞書
    """
    return {
        'is_streamlit_cloud': is_streamlit_cloud(),
        'google_credentials': check_google_credentials(),
        'openai_api_key': bool(get_openai_api_key()),
        'environment_vars': {
            'STREAMLIT_SHARING': os.getenv('STREAMLIT_SHARING'),
            'STREAMLIT_CLOUD': os.getenv('STREAMLIT_CLOUD'),
            'HOSTNAME': os.getenv('HOSTNAME')
        }
    }


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
