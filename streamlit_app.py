"""
Streamlit Cloud対応音声録音・文字起こしアプリ（拡張版）
streamlit-audiorec + OpenAI Whisper API + 豊富な設定機能
"""

# 標準ライブラリ
import base64
import io
import json
import os
import tempfile
import wave
from datetime import datetime, date
from typing import Optional, List, Dict, Any

# サードパーティライブラリ
import numpy as np
import openai
import streamlit as st
from dotenv import load_dotenv
from st_audiorec import st_audiorec

# 拡張機能のインポート
from utils_audiorec import (
    EnhancedSettingsManager, 
    UserDictionaryManager, 
    CommandManager, 
    DeviceManager,
    TaskManager,
    CalendarManager,
    TaskAnalyzer,
    EventAnalyzer,
    GoogleCalendarManager
)
from settings_ui_audiorec import SettingsUI
from config_manager import get_secret, get_google_credentials

# 環境変数の読み込み
load_dotenv()


class AudioRecorderApp:
    """音声録音・文字起こしアプリケーションクラス"""
    
    def __init__(self):
        self.settings_manager = EnhancedSettingsManager()
        self.user_dict_manager = UserDictionaryManager()
        self.command_manager = CommandManager()
        self.device_manager = DeviceManager()
        self.task_manager = TaskManager()
        self.calendar_manager = CalendarManager()
        self.task_analyzer = TaskAnalyzer()
        self.event_analyzer = EventAnalyzer()
        self.google_calendar = GoogleCalendarManager()
        self.settings_ui = SettingsUI()
        
        # セッション状態の初期化
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """セッション状態の初期化"""
        if 'audio_data' not in st.session_state:
            st.session_state.audio_data = None
        if 'transcription' not in st.session_state:
            st.session_state.transcription = ""
        if 'processed_commands' not in st.session_state:
            st.session_state.processed_commands = []
        if 'google_authenticated' not in st.session_state:
            st.session_state.google_authenticated = False
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "メイン"
    
    def setup_openai(self) -> Optional[openai.OpenAI]:
        """OpenAI APIの設定"""
        api_key = get_secret("OPENAI_API_KEY")
        if not api_key:
            st.error("OpenAI APIキーが設定されていません。設定画面で設定してください。")
            return None
        
        try:
            client = openai.OpenAI(api_key=api_key)
            return client
        except Exception as e:
            st.error(f"OpenAI APIの初期化に失敗しました: {e}")
            return None
    
    def transcribe_audio(self, audio_data: bytes, client: openai.OpenAI) -> Optional[str]:
        """音声を文字起こし"""
        if not audio_data:
            return None
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file.flush()
                
                with open(tmp_file.name, "rb") as audio_file:
                    settings = self.settings_manager.load_settings()
                    
                    transcript = client.audio.transcriptions.create(
                        model=settings["transcription"]["model"],
                        file=audio_file,
                        language=settings["transcription"]["language"]
                    )
                    
                os.unlink(tmp_file.name)
                return transcript.text
                
        except Exception as e:
            st.error(f"文字起こしに失敗しました: {e}")
            return None
    
    def save_transcription(self, transcription: str, timestamp: str) -> str:
        """文字起こし結果を保存"""
        os.makedirs("transcriptions", exist_ok=True)
        filename = f"transcription_{timestamp}.txt"
        filepath = os.path.join("transcriptions", filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"文字起こし結果 - {timestamp}\n")
                f.write("="*50 + "\n")
                f.write(transcription)
            return filepath
        except Exception as e:
            st.error(f"ファイル保存に失敗しました: {e}")
            return ""
    
    def save_audio_file(self, audio_data: bytes, timestamp: str) -> str:
        """音声ファイルを保存"""
        os.makedirs("recordings", exist_ok=True)
        filename = f"recording_{timestamp}.wav"
        filepath = os.path.join("recordings", filename)
        
        try:
            with open(filepath, "wb") as f:
                f.write(audio_data)
            return filepath
        except Exception as e:
            st.error(f"音声ファイル保存に失敗しました: {e}")
            return ""
    
    def process_commands(self, text: str) -> List[Dict[str, Any]]:
        """コマンド処理"""
        return self.command_manager.process_text(text)
    
    def analyze_tasks(self, text: str) -> List[Dict[str, Any]]:
        """タスク分析"""
        return self.task_analyzer.analyze_text(text)
    
    def analyze_events(self, text: str) -> List[Dict[str, Any]]:
        """イベント分析"""
        return self.event_analyzer.analyze_text(text)
    
    def display_audio_player(self, audio_data: bytes):
        """音声プレイヤー表示"""
        if audio_data:
            st.audio(audio_data, format='audio/wav')
    
    def display_transcription_results(self, transcription: str, timestamp: str):
        """文字起こし結果表示"""
        if transcription:
            st.subheader("📝 文字起こし結果")
            st.text_area("結果", transcription, height=200, key=f"transcription_{timestamp}")
            
            # 保存ボタン
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 文字起こし結果を保存", key=f"save_trans_{timestamp}"):
                    filepath = self.save_transcription(transcription, timestamp)
                    if filepath:
                        st.success(f"保存しました: {filepath}")
            
            with col2:
                if st.button("📋 クリップボードにコピー", key=f"copy_{timestamp}"):
                    st.write("文字起こし結果をコピーしました（手動でコピーしてください）")
    
    def display_analysis_results(self, transcription: str):
        """分析結果表示"""
        if not transcription:
            return
        
        # コマンド処理結果
        commands = self.process_commands(transcription)
        if commands:
            st.subheader("🔧 検出されたコマンド")
            for cmd in commands:
                with st.expander(f"コマンド: {cmd.get('command', 'Unknown')}"):
                    st.json(cmd)
        
        # タスク分析結果
        tasks = self.analyze_tasks(transcription)
        if tasks:
            st.subheader("📋 検出されたタスク")
            for task in tasks:
                with st.expander(f"タスク: {task.get('title', 'Untitled')}"):
                    st.json(task)
        
        # イベント分析結果
        events = self.analyze_events(transcription)
        if events:
            st.subheader("📅 検出されたイベント")
            for event in events:
                with st.expander(f"イベント: {event.get('title', 'Untitled')}"):
                    st.json(event)
    
    def display_sidebar(self):
        """サイドバー表示"""
        with st.sidebar:
            st.title("🎙️ 音声録音アプリ")
            
            # ページ選択
            page = st.selectbox(
                "ページを選択",
                ["メイン", "設定", "履歴", "統計", "デバイス管理", "ユーザー辞書", "コマンド管理", "タスク管理", "カレンダー"]
            )
            st.session_state.current_page = page
            
            # 設定情報表示
            settings = self.settings_manager.load_settings()
            st.subheader("⚙️ 現在の設定")
            st.write(f"サンプリングレート: {settings['audio']['sample_rate']} Hz")
            st.write(f"録音時間: {settings['audio']['duration']} 秒")
            st.write(f"文字起こしモデル: {settings['transcription']['model']}")
            
            # デバイス情報
            if hasattr(self.device_manager, 'get_current_device_info'):
                device_info = self.device_manager.get_current_device_info()
                if device_info:
                    st.subheader("🎤 デバイス情報")
                    st.write(f"デバイス: {device_info.get('name', 'Unknown')}")
    
    def main_page(self):
        """メインページ"""
        st.title("🎙️ 音声録音・文字起こしアプリ")
        st.write("音声を録音して、OpenAI Whisper APIで文字起こしを行います。")
        
        # OpenAI クライアント設定
        client = self.setup_openai()
        if not client:
            return
        
        # 音声録音
        st.subheader("🎤 音声録音")
        audio_data = st_audiorec()
        
        if audio_data is not None:
            st.session_state.audio_data = audio_data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 音声プレイヤー
            self.display_audio_player(audio_data)
            
            # 音声保存
            if st.button("💾 音声ファイルを保存"):
                filepath = self.save_audio_file(audio_data, timestamp)
                if filepath:
                    st.success(f"音声ファイルを保存しました: {filepath}")
            
            # 文字起こし実行
            if st.button("🔄 文字起こし実行", type="primary"):
                with st.spinner("文字起こし中..."):
                    transcription = self.transcribe_audio(audio_data, client)
                    if transcription:
                        st.session_state.transcription = transcription
                        st.success("文字起こしが完了しました！")
        
        # 文字起こし結果表示
        if st.session_state.transcription:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.display_transcription_results(st.session_state.transcription, timestamp)
            self.display_analysis_results(st.session_state.transcription)
    
    def run(self):
        """アプリケーション実行"""
        # サイドバー表示
        self.display_sidebar()
        
        # ページ表示
        page = st.session_state.current_page
        
        if page == "メイン":
            self.main_page()
        elif page == "設定":
            self.settings_ui.display_settings_page()
        elif page == "履歴":
            self.settings_ui.display_history_page()
        elif page == "統計":
            self.settings_ui.display_statistics_page()
        elif page == "デバイス管理":
            self.settings_ui.display_device_management_page()
        elif page == "ユーザー辞書":
            self.settings_ui.display_user_dictionary_page()
        elif page == "コマンド管理":
            self.settings_ui.display_command_management_page()
        elif page == "タスク管理":
            self.settings_ui.display_task_management_page()
        elif page == "カレンダー":
            self.settings_ui.display_calendar_page()


def main():
    """メイン関数"""
    # Streamlit設定
    st.set_page_config(
        page_title="音声録音・文字起こしアプリ",
        page_icon="🎙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # アプリケーション実行
    app = AudioRecorderApp()
    app.run()


if __name__ == "__main__":
    main()
