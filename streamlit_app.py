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
try:
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
    UTILS_AVAILABLE = True
except ImportError as e:
    print(f"utils_audiorec のインポートに失敗しました: {e}")
    UTILS_AVAILABLE = False

try:
    from settings_ui_audiorec import SettingsUI
    SETTINGS_UI_AVAILABLE = True
except ImportError as e:
    print(f"settings_ui_audiorec のインポートに失敗しました: {e}")
    SETTINGS_UI_AVAILABLE = False

try:
    from config_manager import get_secret, get_google_credentials
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"config_manager のインポートに失敗しました: {e}")
    CONFIG_AVAILABLE = False

# 環境変数の読み込み
load_dotenv()


class AudioRecorderApp:
    """音声録音・文字起こしアプリケーションクラス"""
    
    def __init__(self):
        # 拡張機能の初期化（インポート可能な場合のみ）
        if UTILS_AVAILABLE:
            self.settings_manager = EnhancedSettingsManager()
            self.user_dict_manager = UserDictionaryManager()
            self.command_manager = CommandManager()
            self.device_manager = DeviceManager()
            self.task_manager = TaskManager()
            self.calendar_manager = CalendarManager()
            self.task_analyzer = TaskAnalyzer()
            self.event_analyzer = EventAnalyzer()
            self.google_calendar = GoogleCalendarManager()
        else:
            # フォールバック: 基本機能のみ
            self.settings_manager = None
            self.user_dict_manager = None
            self.command_manager = None
            self.device_manager = None
            self.task_manager = None
            self.calendar_manager = None
            self.task_analyzer = None
            self.event_analyzer = None
            self.google_calendar = None
        
        if SETTINGS_UI_AVAILABLE:
            self.settings_ui = SettingsUI()
        else:
            self.settings_ui = None
        
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
        if CONFIG_AVAILABLE:
            api_key = get_secret("OPENAI_API_KEY")
        else:
            # フォールバック: 環境変数またはStreamlit Secretsから直接取得
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                try:
                    api_key = st.secrets.get("OPENAI_API_KEY")
                except:
                    api_key = None
        
        if not api_key:
            st.error("OpenAI APIキーが設定されていません。環境変数またはStreamlit Secretsで設定してください。")
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
                    # 設定の取得（フォールバック対応）
                    if self.settings_manager:
                        try:
                            settings = self.settings_manager.load_settings()
                            # transcription.modelまたはwhisper.model_sizeから取得
                            model = settings.get('transcription', {}).get('model') or settings.get('whisper', {}).get('model_size', 'whisper-1')
                            if model == 'base':  # whisperのmodel_sizeの場合はOpenAI APIモデル名に変換
                                model = 'whisper-1'
                            language = settings.get('transcription', {}).get('language') or settings.get('whisper', {}).get('language', 'ja')
                        except Exception as e:
                            print(f"設定読み込みエラー: {e}")
                            model = "whisper-1"
                            language = "ja"
                    else:
                        # デフォルト設定
                        model = "whisper-1"
                        language = "ja"
                    
                    transcript = client.audio.transcriptions.create(
                        model=model,
                        file=audio_file,
                        language=language
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
        if self.command_manager:
            return self.command_manager.process_text(text)
        return []
    
    def analyze_tasks(self, text: str) -> List[Dict[str, Any]]:
        """タスク分析"""
        if self.task_analyzer:
            return self.task_analyzer.analyze_text(text)
        return []
    
    def analyze_events(self, text: str) -> List[Dict[str, Any]]:
        """イベント分析"""
        if self.event_analyzer:
            return self.event_analyzer.analyze_text(text)
        return []
    
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
            if self.settings_manager:
                try:
                    settings = self.settings_manager.load_settings()
                    st.subheader("⚙️ 現在の設定")
                    st.write(f"サンプリングレート: {settings.get('audio', {}).get('sample_rate', 44100)} Hz")
                    st.write(f"録音時間: {settings.get('audio', {}).get('duration', 5)} 秒")
                    # transcription.modelの代わりにwhisper.model_sizeを使用
                    model = settings.get('transcription', {}).get('model') or settings.get('whisper', {}).get('model_size', 'whisper-1')
                    st.write(f"文字起こしモデル: {model}")
                except Exception as e:
                    st.subheader("⚙️ デフォルト設定（設定読み込みエラー）")
                    st.write("サンプリングレート: 44100 Hz")
                    st.write("録音時間: 5 秒")
                    st.write("文字起こしモデル: whisper-1")
                    print(f"設定読み込みエラー: {e}")
            else:
                st.subheader("⚙️ デフォルト設定")
                st.write("サンプリングレート: 44100 Hz")
                st.write("録音時間: 5 秒")
                st.write("文字起こしモデル: whisper-1")
            
            # デバイス情報
            if self.device_manager and hasattr(self.device_manager, 'get_current_device_info'):
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
            if self.settings_ui:
                self.settings_ui.display_settings_page()
            else:
                st.error("設定UIが利用できません。settings_ui_audiorec.pyの読み込みに失敗しました。")
        elif page == "履歴":
            if self.settings_ui:
                self.settings_ui.display_history_page()
            else:
                st.error("履歴UIが利用できません。settings_ui_audiorec.pyの読み込みに失敗しました。")
        elif page == "統計":
            if self.settings_ui:
                self.settings_ui.display_statistics_page()
            else:
                st.error("統計UIが利用できません。settings_ui_audiorec.pyの読み込みに失敗しました。")
        elif page == "デバイス管理":
            if self.settings_ui:
                self.settings_ui.display_device_management_page()
            else:
                st.error("デバイス管理UIが利用できません。settings_ui_audiorec.pyの読み込みに失敗しました。")
        elif page == "ユーザー辞書":
            if self.settings_ui:
                self.settings_ui.display_user_dictionary_page()
            else:
                st.error("ユーザー辞書UIが利用できません。settings_ui_audiorec.pyの読み込みに失敗しました。")
        elif page == "コマンド管理":
            if self.settings_ui:
                self.settings_ui.display_command_management_page()
            else:
                st.error("コマンド管理UIが利用できません。settings_ui_audiorec.pyの読み込みに失敗しました。")
        elif page == "タスク管理":
            if self.settings_ui:
                self.settings_ui.display_task_management_page()
            else:
                st.error("タスク管理UIが利用できません。settings_ui_audiorec.pyの読み込みに失敗しました。")
        elif page == "カレンダー":
            if self.settings_ui:
                self.settings_ui.display_calendar_page()
            else:
                st.error("カレンダーUIが利用できません。settings_ui_audiorec.pyの読み込みに失敗しました。")


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
