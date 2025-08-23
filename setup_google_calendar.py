#!/usr/bin/env python3
"""
Googleカレンダー認証設定スクリプト
音声録音・文字起こしアプリケーション用のGoogleカレンダー連携設定
"""

import os
import json
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Google Calendar APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/calendar']

def setup_google_calendar_auth():
    """Googleカレンダー認証の設定"""
    print("🔐 Googleカレンダー認証設定を開始します...")
    
    creds = None
    token_file = 'token.pickle'
    credentials_file = 'credentials.json'
    
    # 既存のトークンがある場合は読み込み
    if os.path.exists(token_file):
        print("📁 既存のトークンファイルを確認中...")
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # 有効な認証情報がない場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 トークンを更新中...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"❌ トークン更新エラー: {e}")
                creds = None
        
        # 認証情報ファイルがない場合
        if not os.path.exists(credentials_file):
            print("❌ credentials.jsonファイルが見つかりません")
            print("\n📋 以下の手順でGoogle Cloud Consoleから認証情報を取得してください：")
            print("1. https://console.cloud.google.com/ にアクセス")
            print("2. プロジェクトを作成または選択")
            print("3. Google Calendar APIを有効化")
            print("4. OAuth 2.0クライアントIDを作成（デスクトップアプリケーション）")
            print("5. JSONファイルをダウンロードしてcredentials.jsonとして保存")
            print("6. このスクリプトを再実行")
            return False
        
        # 新しい認証フローを開始
        print("🔑 新しい認証を開始します...")
        try:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # トークンを保存
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
            print("✅ 認証が完了しました")
            
        except Exception as e:
            print(f"❌ 認証エラー: {e}")
            return False
    
    # 認証テスト
    try:
        print("🧪 認証テストを実行中...")
        service = build('calendar', 'v3', credentials=creds)
        
        # カレンダー一覧を取得
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        if calendars:
            print("✅ 認証テスト成功！利用可能なカレンダー:")
            for calendar in calendars[:5]:  # 最初の5つを表示
                print(f"  📅 {calendar['summary']} ({calendar['id']})")
            if len(calendars) > 5:
                print(f"  ... 他 {len(calendars) - 5} 個のカレンダー")
        else:
            print("⚠️ カレンダーが見つかりませんでした")
        
        # 認証情報をStreamlit Secrets形式で表示
        print("\n📝 Streamlit Secrets設定情報:")
        print("以下の内容を.streamlit/secrets.tomlに追加してください：")
        print()
        print("# Google認証情報")
        print(f'GOOGLE_CLIENT_ID = "{creds.client_id}"')
        print(f'GOOGLE_CLIENT_SECRET = "{creds.client_secret}"')
        if creds.refresh_token:
            print(f'GOOGLE_REFRESH_TOKEN = "{creds.refresh_token}"')
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 認証テストエラー: {e}")
        return False

def check_current_setup():
    """現在の設定状況を確認"""
    print("🔍 現在の設定状況を確認中...")
    
    # ファイルの存在確認
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
    
    # Streamlit Secretsの内容確認
    secrets_file = '.streamlit/secrets.toml'
    if os.path.exists(secrets_file):
        print("\n📄 Streamlit Secretsの内容:")
        try:
            with open(secrets_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 機密情報をマスク
                masked_content = content.replace('sk-', 'sk-***')
                print(masked_content)
        except Exception as e:
            print(f"❌ ファイル読み込みエラー: {e}")
    
    print()

def main():
    """メイン関数"""
    print("=" * 60)
    print("🎯 Googleカレンダー連携設定ツール")
    print("=" * 60)
    
    while True:
        print("\n📋 メニュー:")
        print("1. Googleカレンダー認証を設定")
        print("2. 現在の設定状況を確認")
        print("3. 認証テストを実行")
        print("4. 終了")
        
        choice = input("\n選択してください (1-4): ").strip()
        
        if choice == '1':
            print("\n" + "=" * 40)
            success = setup_google_calendar_auth()
            if success:
                print("\n🎉 Googleカレンダー認証設定が完了しました！")
                print("アプリケーションでタスクやイベントをGoogleカレンダーに同期できます。")
            else:
                print("\n❌ 認証設定に失敗しました。")
                print("手順を確認してから再実行してください。")
            print("=" * 40)
            
        elif choice == '2':
            print("\n" + "=" * 40)
            check_current_setup()
            print("=" * 40)
            
        elif choice == '3':
            print("\n" + "=" * 40)
            print("🧪 認証テストを実行中...")
            if setup_google_calendar_auth():
                print("✅ 認証テスト成功！")
            else:
                print("❌ 認証テスト失敗")
            print("=" * 40)
            
        elif choice == '4':
            print("\n👋 設定ツールを終了します")
            break
            
        else:
            print("❌ 無効な選択です。1-4の数字を入力してください。")

if __name__ == "__main__":
    main()
