#!/usr/bin/env python3
"""
Google認証設定支援スクリプト
Webアプリケーション用のGoogle認証設定を簡単に行うためのスクリプト
"""

import os
import json
import sys
from pathlib import Path

def setup_google_auth():
    """Google認証設定をセットアップ"""
    print("🔐 Google認証設定支援スクリプト")
    print("=" * 50)
    
    # 設定方法の選択
    print("\n1. 環境変数による認証（推奨・本番環境用）")
    print("2. ファイル認証（開発用）")
    print("3. 設定の確認")
    print("4. 終了")
    
    choice = input("\n選択してください (1-4): ").strip()
    
    if choice == "1":
        setup_environment_variables()
    elif choice == "2":
        setup_file_authentication()
    elif choice == "3":
        check_current_settings()
    elif choice == "4":
        print("終了します。")
        sys.exit(0)
    else:
        print("❌ 無効な選択です。")
        return

def setup_environment_variables():
    """環境変数による認証設定"""
    print("\n🔧 環境変数による認証設定")
    print("-" * 30)
    
    print("\n📋 必要な情報:")
    print("1. Google Cloud Consoleで取得したClient ID")
    print("2. Google Cloud Consoleで取得したClient Secret")
    print("3. 初回認証後に取得するRefresh Token")
    
    # 環境変数の設定
    client_id = input("\nClient IDを入力してください: ").strip()
    client_secret = input("Client Secretを入力してください: ").strip()
    refresh_token = input("Refresh Tokenを入力してください（初回は空欄可）: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Client IDとClient Secretは必須です。")
        return
    
    # .envファイルの作成
    env_content = f"""# Google認証用環境変数
GOOGLE_CLIENT_ID={client_id}
GOOGLE_CLIENT_SECRET={client_secret}
"""
    
    if refresh_token:
        env_content += f"GOOGLE_REFRESH_TOKEN={refresh_token}\n"
    
    # .envファイルに保存
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("\n✅ .envファイルを作成しました")
    except Exception as e:
        print(f"\n❌ .envファイルの作成に失敗しました: {e}")
        print("手動で.envファイルを作成してください")
    
    # .streamlit/secrets.tomlファイルの作成
    try:
        # .streamlitディレクトリの作成
        os.makedirs('.streamlit', exist_ok=True)
        
        # secrets.tomlファイルの作成
        secrets_content = f"""# Streamlit Secrets設定ファイル
# 全てのキーをルートレベルで統一

GOOGLE_CLIENT_ID = "{client_id}"
GOOGLE_CLIENT_SECRET = "{client_secret}"
"""
        
        if refresh_token:
            secrets_content += f'GOOGLE_REFRESH_TOKEN = "{refresh_token}"\n'
        
        with open('.streamlit/secrets.toml', 'w', encoding='utf-8') as f:
            f.write(secrets_content)
        print("✅ .streamlit/secrets.tomlファイルを作成しました")
    except Exception as e:
        print(f"\n❌ .streamlit/secrets.tomlファイルの作成に失敗しました: {e}")
        print("手動で.streamlit/secrets.tomlファイルを作成してください")
    
    print("📝 設定を完了しました:")
    print(f"   GOOGLE_CLIENT_ID={client_id}")
    print(f"   GOOGLE_CLIENT_SECRET={'*' * len(client_secret)}")
    if refresh_token:
        print(f"   GOOGLE_REFRESH_TOKEN={'*' * len(refresh_token)}")
    
    print("\n💡 次のステップ:")
    print("1. Streamlitアプリケーションを起動")
    print("2. Googleカレンダータブで認証状態を確認")
    if not refresh_token:
        print("3. 初回認証後にRefresh Tokenを取得して設定ファイルに追加")
    print("4. Streamlit Cloudにデプロイする場合は、.streamlit/secrets.tomlの内容をStreamlit Cloud Secretsにコピー")

def setup_file_authentication():
    """ファイル認証の設定"""
    print("\n📁 ファイル認証の設定（開発用）")
    print("-" * 30)
    
    print("\n📋 手順:")
    print("1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス")
    print("2. 新しいプロジェクトを作成")
    print("3. Google Calendar APIを有効化")
    print("4. 認証情報を作成（OAuth 2.0クライアントID）")
    print("5. credentials.jsonファイルをダウンロード")
    print("6. このファイルをプロジェクトのルートディレクトリに配置")
    
    # credentials.jsonファイルの確認
    if os.path.exists('credentials.json'):
        print("\n✅ credentials.jsonファイルが見つかりました")
        
        # ファイル内容の確認
        try:
            with open('credentials.json', 'r') as f:
                creds_data = json.load(f)
            
            if 'installed' in creds_data:
                client_id = creds_data['installed']['client_id']
                print(f"✅ Client ID: {client_id}")
                print("✅ ファイル形式が正しいです")
            else:
                print("⚠️ ファイル形式が正しくない可能性があります")
        except Exception as e:
            print(f"❌ ファイルの読み込みに失敗しました: {e}")
    else:
        print("\n❌ credentials.jsonファイルが見つかりません")
        print("上記の手順に従ってファイルを配置してください")

def check_current_settings():
    """現在の設定を確認"""
    print("\n🔍 現在の設定確認")
    print("-" * 30)
    
    # 環境変数の確認
    print("\n📋 環境変数:")
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    
    if client_id:
        print(f"✅ GOOGLE_CLIENT_ID: {client_id}")
    else:
        print("❌ GOOGLE_CLIENT_ID: 未設定")
    
    if client_secret:
        print(f"✅ GOOGLE_CLIENT_SECRET: {'*' * len(client_secret)}")
    else:
        print("❌ GOOGLE_CLIENT_SECRET: 未設定")
    
    if refresh_token:
        print(f"✅ GOOGLE_REFRESH_TOKEN: {'*' * len(refresh_token)}")
    else:
        print("❌ GOOGLE_REFRESH_TOKEN: 未設定")
    
    # ファイルの確認
    print("\n📁 ファイル:")
    if os.path.exists('credentials.json'):
        print("✅ credentials.json: 存在")
    else:
        print("❌ credentials.json: 存在しない")
    
    if os.path.exists('token.pickle'):
        print("✅ token.pickle: 存在")
    else:
        print("❌ token.pickle: 存在しない")
    
    if os.path.exists('.env'):
        print("✅ .env: 存在")
    else:
        print("❌ .env: 存在しない")
    
    # .streamlit/secrets.tomlファイルの確認
    if os.path.exists('.streamlit/secrets.toml'):
        print("✅ .streamlit/secrets.toml: 存在")
        try:
            import toml
            with open('.streamlit/secrets.toml', 'r', encoding='utf-8') as f:
                secrets_data = toml.load(f)
            
            if 'GOOGLE_CLIENT_ID' in secrets_data:
                print(f"✅ Streamlit Secrets GOOGLE_CLIENT_ID: {secrets_data['GOOGLE_CLIENT_ID']}")
            else:
                print("❌ Streamlit Secrets GOOGLE_CLIENT_ID: 未設定")
            
            if 'GOOGLE_CLIENT_SECRET' in secrets_data:
                secret = secrets_data['GOOGLE_CLIENT_SECRET']
                print(f"✅ Streamlit Secrets GOOGLE_CLIENT_SECRET: {'*' * len(secret)}")
            else:
                print("❌ Streamlit Secrets GOOGLE_CLIENT_SECRET: 未設定")
            
            if 'GOOGLE_REFRESH_TOKEN' in secrets_data:
                token = secrets_data['GOOGLE_REFRESH_TOKEN']
                print(f"✅ Streamlit Secrets GOOGLE_REFRESH_TOKEN: {'*' * len(token)}")
            else:
                print("❌ Streamlit Secrets GOOGLE_REFRESH_TOKEN: 未設定")
                
        except ImportError:
            print("⚠️ tomlライブラリがインストールされていないため、詳細確認ができません")
        except Exception as e:
            print(f"❌ .streamlit/secrets.tomlの読み込みエラー: {e}")
    else:
        print("❌ .streamlit/secrets.toml: 存在しない")
    
    # 推奨設定の確認
    print("\n💡 推奨設定:")
    if client_id and client_secret:
        print("✅ 環境変数による認証が設定されています（推奨）")
    elif os.path.exists('.streamlit/secrets.toml'):
        print("✅ Streamlit Secretsによる認証が設定されています（Streamlit Cloud推奨）")
    elif os.path.exists('credentials.json'):
        print("⚠️ ファイル認証が設定されています（開発用）")
    else:
        print("❌ 認証設定が不完全です")

def main():
    """メイン関数"""
    try:
        setup_google_auth()
    except KeyboardInterrupt:
        print("\n\n👋 終了します。")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main() 