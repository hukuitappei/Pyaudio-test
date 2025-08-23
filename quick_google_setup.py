#!/usr/bin/env python3
"""
Googleカレンダー連携の簡易設定スクリプト
"""

import os
import json
import toml
from pathlib import Path

def create_sample_credentials():
    """サンプルのcredentials.jsonファイルを作成"""
    sample_credentials = {
        "installed": {
            "client_id": "your_client_id_here.apps.googleusercontent.com",
            "project_id": "your_project_id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "your_client_secret_here",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    with open('credentials.json', 'w', encoding='utf-8') as f:
        json.dump(sample_credentials, f, indent=2)
    
    print("✅ サンプルのcredentials.jsonファイルを作成しました")
    print("📝 このファイルを実際のGoogle Cloud Consoleからダウンロードした認証情報で置き換えてください")

def update_streamlit_secrets():
    """Streamlit Secretsファイルを更新"""
    secrets_file = '.streamlit/secrets.toml'
    
    # 既存の設定を読み込み
    if os.path.exists(secrets_file):
        with open(secrets_file, 'r', encoding='utf-8') as f:
            secrets = toml.load(f)
    else:
        secrets = {}
    
    # Google認証情報を追加
    secrets.update({
        'GOOGLE_CLIENT_ID': 'your_client_id_here.apps.googleusercontent.com',
        'GOOGLE_CLIENT_SECRET': 'your_client_secret_here',
        'GOOGLE_REFRESH_TOKEN': 'your_refresh_token_here'
    })
    
    # ディレクトリが存在しない場合は作成
    os.makedirs('.streamlit', exist_ok=True)
    
    # ファイルに保存
    with open(secrets_file, 'w', encoding='utf-8') as f:
        toml.dump(secrets, f)
    
    print("✅ Streamlit Secretsファイルを更新しました")
    print("📝 実際の認証情報で値を置き換えてください")

def show_setup_instructions():
    """設定手順を表示"""
    print("\n" + "=" * 60)
    print("🔧 Googleカレンダー連携設定手順")
    print("=" * 60)
    
    print("\n📋 手順1: Google Cloud Consoleでの設定")
    print("1. https://console.cloud.google.com/ にアクセス")
    print("2. プロジェクトを作成または選択")
    print("3. Google Calendar APIを有効化:")
    print("   - 左側メニュー → 「APIとサービス」→「ライブラリ」")
    print("   - 検索バーで「Google Calendar API」を検索")
    print("   - 「Google Calendar API」を選択して「有効にする」")
    print("4. OAuth 2.0認証情報を作成:")
    print("   - 「APIとサービス」→「認証情報」")
    print("   - 「認証情報を作成」→「OAuth 2.0 クライアントID」")
    print("   - アプリケーションの種類で「デスクトップアプリケーション」を選択")
    print("   - 名前を入力（例：「Voice Recorder Calendar Integration」）")
    print("   - 「作成」をクリック")
    print("5. JSONファイルをダウンロード:")
    print("   - 作成されたOAuth 2.0クライアントIDをクリック")
    print("   - 「JSONをダウンロード」をクリック")
    print("   - ダウンロードしたファイルをcredentials.jsonとして保存")
    
    print("\n📋 手順2: 認証の実行")
    print("1. credentials.jsonファイルをプロジェクトルートに配置")
    print("2. 以下のコマンドを実行:")
    print("   python setup_google_calendar.py")
    print("3. ブラウザで認証を完了")
    print("4. 表示された認証情報を.streamlit/secrets.tomlに追加")
    
    print("\n📋 手順3: アプリケーションでの使用")
    print("1. アプリケーションを再起動")
    print("2. タスク管理タブまたはカレンダー管理タブで認証状態を確認")
    print("3. タスクやイベントをGoogleカレンダーに同期")
    
    print("\n⚠️ 注意事項:")
    print("- credentials.jsonとtoken.pickleファイルは.gitignoreに追加してください")
    print("- 認証情報をGitリポジトリにコミットしないでください")
    print("- 本番環境では環境変数またはStreamlit Secretsを使用してください")

def main():
    """メイン関数"""
    print("🎯 Googleカレンダー連携簡易設定ツール")
    print("=" * 50)
    
    while True:
        print("\n📋 メニュー:")
        print("1. サンプルファイルを作成")
        print("2. Streamlit Secretsを更新")
        print("3. 設定手順を表示")
        print("4. 現在の状況を確認")
        print("5. 終了")
        
        choice = input("\n選択してください (1-5): ").strip()
        
        if choice == '1':
            print("\n" + "=" * 40)
            create_sample_credentials()
            print("=" * 40)
            
        elif choice == '2':
            print("\n" + "=" * 40)
            update_streamlit_secrets()
            print("=" * 40)
            
        elif choice == '3':
            print("\n" + "=" * 40)
            show_setup_instructions()
            print("=" * 40)
            
        elif choice == '4':
            print("\n" + "=" * 40)
            print("🔍 現在の状況:")
            
            files_to_check = [
                ('credentials.json', 'Google認証情報ファイル'),
                ('token.pickle', '認証トークンファイル'),
                ('.streamlit/secrets.toml', 'Streamlit Secretsファイル')
            ]
            
            for filename, description in files_to_check:
                if os.path.exists(filename):
                    print(f"✅ {description}: {filename}")
                else:
                    print(f"❌ {description}: {filename} (見つかりません)")
            
            print("=" * 40)
            
        elif choice == '5':
            print("\n👋 設定ツールを終了します")
            break
            
        else:
            print("❌ 無効な選択です。1-5の数字を入力してください。")

if __name__ == "__main__":
    main()
