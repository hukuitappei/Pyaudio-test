"""
Streamlit Cloud対応音声録音・文字起こしアプリ（拡張版）
streamlit-audiorec + OpenAI Whisper API + 豊富な設定機能
"""

# 標準ライブラリ
import base64
import io
import json
import os
import sys
import tempfile
import traceback
import wave
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent))

# サードパーティライブラリ
import numpy as np
import openai
import streamlit as st
from dotenv import load_dotenv

# st_audiorecのインポート（エラーハンドリング付き）
try:
    from st_audiorec import st_audiorec
    ST_AUDIOREC_AVAILABLE = True
except ImportError as e:
    st.warning(f"st_audiorec のインポートに失敗しました: {e}")
    ST_AUDIOREC_AVAILABLE = False
    # フォールバック用のダミー関数
    def st_audiorec(*args, **kwargs):
        st.error("音声録音機能が利用できません")
        return None
except Exception as e:
    st.warning(f"st_audiorec で予期しないエラーが発生しました: {e}")
    ST_AUDIOREC_AVAILABLE = False
    # フォールバック用のダミー関数
    def st_audiorec(*args, **kwargs):
        st.error("音声録音機能が利用できません")
        return None

# 拡張機能のインポート
try:
    from src.utils_audiorec import (
        EnhancedSettingsManager, 
        UserDictionaryManager, 
        CommandManager, 
        DeviceManager,
        TaskManager,
        CalendarManager,
        TaskAnalyzer,
        EventAnalyzer,
        GoogleCalendarManager,
        PYAUDIO_AVAILABLE,
        OPENAI_AVAILABLE
    )
    UTILS_AVAILABLE = True
    st.success("拡張機能が正常に読み込まれました")
except ImportError as e:
    st.error(f"utils_audiorec のインポートに失敗しました: {e}")
    st.info("基本機能のみで動作します")
    UTILS_AVAILABLE = False
    PYAUDIO_AVAILABLE = False
    OPENAI_AVAILABLE = False
except Exception as e:
    st.error(f"予期しないエラーが発生しました: {e}")
    st.info("基本機能のみで動作します")
    UTILS_AVAILABLE = False
    PYAUDIO_AVAILABLE = False
    OPENAI_AVAILABLE = False

try:
    from src.settings_ui_audiorec import SettingsUI
    SETTINGS_UI_AVAILABLE = True
except ImportError as e:
    st.warning(f"settings_ui_audiorec のインポートに失敗しました: {e}")
    SETTINGS_UI_AVAILABLE = False
except Exception as e:
    st.warning(f"settings_ui_audiorec で予期しないエラーが発生しました: {e}")
    SETTINGS_UI_AVAILABLE = False

try:
    from config.config_manager import get_secret, get_google_credentials
    CONFIG_AVAILABLE = True
except ImportError as e:
    st.warning(f"config_manager のインポートに失敗しました: {e}")
    CONFIG_AVAILABLE = False
except Exception as e:
    st.warning(f"config_manager で予期しないエラーが発生しました: {e}")
    CONFIG_AVAILABLE = False

# 設定確認機能の追加
CONFIG_UI_AVAILABLE = False
show_environment_info = None
if CONFIG_AVAILABLE:
    try:
        from config.config_manager import show_environment_info
        CONFIG_UI_AVAILABLE = True
    except ImportError as e:
        st.warning(f"設定確認機能のインポートに失敗しました: {e}")
        CONFIG_UI_AVAILABLE = False
    except Exception as e:
        st.warning(f"設定確認機能で予期しないエラーが発生しました: {e}")
        CONFIG_UI_AVAILABLE = False

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
        # 基本状態
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
        if 'transcription_timestamp' not in st.session_state:
            st.session_state.transcription_timestamp = None
        
        # Google認証関連のセッション状態初期化
        if 'google_auth_url' not in st.session_state:
            st.session_state.google_auth_url = None
        if 'google_auth_flow' not in st.session_state:
            st.session_state.google_auth_flow = None
        if 'google_auth_key' not in st.session_state:
            st.session_state.google_auth_key = None
        if 'google_credentials' not in st.session_state:
            st.session_state.google_credentials = None
        if 'google_auth_status' not in st.session_state:
            st.session_state.google_auth_status = False
    
    def setup_openai(self) -> Optional[openai.OpenAI]:
        """OpenAI APIの設定"""
        if not OPENAI_AVAILABLE:
            st.error("⚠️ OpenAIライブラリが利用できません")
            return None
        
        # APIキーの取得
        api_key = None
        
        # 1. config_managerから取得を試行
        try:
            api_key = get_secret("OPENAI_API_KEY")
        except:
            pass
        
        # 2. Streamlit Secretsから取得を試行
        if not api_key:
            try:
                api_key = st.secrets.get("OPENAI_API_KEY")
            except:
                pass
        
        # 3. 環境変数から取得を試行
        if not api_key:
            try:
                api_key = os.getenv("OPENAI_API_KEY")
            except:
                pass
        
        if not api_key:
            st.error("⚠️ OpenAI APIキーが設定されていません。")
            st.info("設定タブでOpenAI APIキーを設定してください。")
            return None
        
        try:
            client = openai.OpenAI(api_key=api_key)
            return client
        except Exception as e:
            st.error(f"OpenAI APIの初期化に失敗しました: {e}")
            return None
    
    def transcribe_audio(self, client: openai.OpenAI, audio_data: bytes) -> Optional[str]:
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
        try:
            # 絶対パスでディレクトリ作成
            transcriptions_dir = os.path.join(os.getcwd(), "transcriptions")
            os.makedirs(transcriptions_dir, exist_ok=True)
            
            filename = f"transcription_{timestamp}.txt"
            filepath = os.path.join(transcriptions_dir, filename)
            
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
        try:
            # 絶対パスでディレクトリ作成
            recordings_dir = os.path.join(os.getcwd(), "recordings")
            os.makedirs(recordings_dir, exist_ok=True)
            
            filename = f"recording_{timestamp}.wav"
            filepath = os.path.join(recordings_dir, filename)
            
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
            
            # タスク追加コマンドの処理
            task_commands = [cmd for cmd in commands if cmd.get('command') == 'タスク追加']
            if task_commands:
                st.info("📋 タスク追加コマンドが検出されました")
                
                # タスク自動生成オプション
                if st.button("📋 タスクとして保存", key="save_task_commands"):
                    if self.task_manager:
                        saved_count = 0
                        for cmd in task_commands:
                            if self.task_manager.add_task(
                                title=cmd.get('title', '無題'),
                                description=cmd.get('description', ''),
                                priority=cmd.get('priority', '中'),
                                category=cmd.get('category', 'その他'),
                                auto_sync=True  # 自動同期を有効化
                            ):
                                saved_count += 1
                        
                        if saved_count > 0:
                            st.success(f"✅ {saved_count}件のタスクを保存しました")
                            if saved_count > 0:
                                st.info("💡 タスクは自動的にGoogleカレンダーと同期されます")
                        else:
                            st.error("❌ タスクの保存に失敗しました")
                    else:
                        st.error("❌ タスクマネージャーが利用できません")
            
            # その他のコマンド表示
            other_commands = [cmd for cmd in commands if cmd.get('command') != 'タスク追加']
            for cmd in other_commands:
                with st.expander(f"コマンド: {cmd.get('command', 'Unknown')}"):
                    st.json(cmd)
        
        # タスク分析結果（既存の機能）
        tasks = self.analyze_tasks(transcription)
        if tasks:
            st.subheader("📋 検出されたタスク")
            
            # タスク自動生成オプション
            if st.button("📋 タスクとして保存", key="save_tasks_from_transcription"):
                if self.task_manager:
                    saved_count = 0
                    for task in tasks:
                        if self.task_manager.add_task(
                            title=task.get('title', '無題'),
                            description=task.get('description', ''),
                            priority=task.get('priority', 'medium'),
                            category='音声文字起こし'
                        ):
                            saved_count += 1
                    
                    if saved_count > 0:
                        st.success(f"✅ {saved_count}件のタスクを保存しました")
                    else:
                        st.error("❌ タスクの保存に失敗しました")
                else:
                    st.error("❌ タスクマネージャーが利用できません")
            
            for task in tasks:
                with st.expander(f"タスク: {task.get('title', 'Untitled')}"):
                    st.json(task)
        
        # イベント分析結果
        events = self.analyze_events(transcription)
        if events:
            st.subheader("📅 検出されたイベント")
            
            # イベント自動生成オプション
            if st.button("📅 イベントとして保存", key="save_events_from_transcription"):
                if self.calendar_manager:
                    saved_count = 0
                    for event in events:
                        if self.calendar_manager.add_event(
                            title=event.get('title', '無題'),
                            description=event.get('description', ''),
                            start_date=event.get('start_date'),
                            end_date=event.get('end_date'),
                            category='音声文字起こし'
                        ):
                            saved_count += 1
                    
                    if saved_count > 0:
                        st.success(f"✅ {saved_count}件のイベントを保存しました")
                    else:
                        st.error("❌ イベントの保存に失敗しました")
                else:
                    st.error("❌ カレンダーマネージャーが利用できません")
            
            for event in events:
                with st.expander(f"イベント: {event.get('title', 'Untitled')}"):
                    st.json(event)
    
    def display_sidebar(self):
        """サイドバー表示"""
        with st.sidebar:
            st.title("🎙️ 音声録音アプリ")
            
            # ページ選択（シンプル化）
            page = st.selectbox(
                "表示モード",
                ["メイン（タブ形式）", "クラシック表示"]
            )
            
            # メインページはタブ形式、他は従来通り
            if page == "メイン（タブ形式）":
                st.session_state.current_page = "メイン"
            else:
                classic_page = st.selectbox(
                    "クラシック表示ページ",
                    ["設定", "履歴", "統計", "デバイス管理", "ユーザー辞書", "コマンド管理", "タスク管理", "カレンダー"]
                )
                st.session_state.current_page = classic_page
            
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
                    if device_info.get('description'):
                        st.write(f"説明: {device_info.get('description')}")
            else:
                st.subheader("🎤 デバイス情報")
                st.write("デバイス情報が取得できません")
    
    def main_page(self):
        """メインページ（タブ形式）"""
        st.title("🎙️ 音声録音・文字起こしアプリ")
        st.write("音声を録音して、OpenAI Whisper APIで文字起こしを行います。")
        st.info("💡 各機能はタブから簡単にアクセスできます。")
        
        # タブの作成
        tabs = st.tabs([
            "🎤 録音・文字起こし",
            "⚙️ 設定", 
            "📚 ユーザー辞書",
            "🔧 コマンド管理",
            "🎙️ デバイス管理",
            "📋 タスク管理",
            "📅 カレンダー",
            "📜 履歴",
            "📊 統計"
        ])
        
        # 録音・文字起こしタブ
        with tabs[0]:
            self.display_recording_tab()
        
        # 設定タブ
        with tabs[1]:
            if self.settings_ui:
                self.settings_ui.display_settings_page()
            else:
                st.error("設定UIが利用できません。")
                st.info("💡 解決方法: settings_ui_audiorec.pyの読み込みに失敗しました。")
        
        # ユーザー辞書タブ
        with tabs[2]:
            if self.settings_ui:
                self.settings_ui.display_user_dictionary_page()
            else:
                st.error("ユーザー辞書UIが利用できません。")
                st.info("💡 解決方法: settings_ui_audiorec.pyの読み込みに失敗しました。")
        
        # コマンド管理タブ
        with tabs[3]:
            if self.settings_ui:
                self.settings_ui.display_command_management_page()
            else:
                st.error("コマンド管理UIが利用できません。")
                st.info("💡 解決方法: settings_ui_audiorec.pyの読み込みに失敗しました。")
        
        # デバイス管理タブ
        with tabs[4]:
            if self.settings_ui:
                self.settings_ui.display_device_management_page()
            else:
                st.error("デバイス管理UIが利用できません。")
                st.info("💡 解決方法: settings_ui_audiorec.pyの読み込みに失敗しました。")
        
        # タスク管理タブ
        with tabs[5]:
            if self.settings_ui:
                self.settings_ui.display_task_management_page()
            else:
                st.error("タスク管理UIが利用できません。")
                st.info("💡 解決方法: settings_ui_audiorec.pyの読み込みに失敗しました。")
        
        # カレンダータブ
        with tabs[6]:
            if self.settings_ui:
                self.settings_ui.display_calendar_page()
            else:
                st.error("カレンダーUIが利用できません。")
                st.info("💡 解決方法: settings_ui_audiorec.pyの読み込みに失敗しました。")
        
        # 履歴タブ
        with tabs[7]:
            if self.settings_ui:
                self.settings_ui.display_history_page()
            else:
                st.error("履歴UIが利用できません。")
                st.info("💡 解決方法: settings_ui_audiorec.pyの読み込みに失敗しました。")
        
        # 統計タブ
        with tabs[8]:
            if self.settings_ui:
                self.settings_ui.display_statistics_page()
            else:
                st.error("統計UIが利用できません。")
                st.info("💡 解決方法: settings_ui_audiorec.pyの読み込みに失敗しました。")
    
    def display_recording_tab(self):
        """録音・文字起こしタブの表示"""
        # OpenAI クライアント設定
        client = self.setup_openai()
        if not client:
            return
        
        # 環境情報の表示
        if not PYAUDIO_AVAILABLE:
            st.info("📝 **録音環境**: Streamlit Cloud環境では直接録音は利用できません")
            st.info("💡 **録音代替案**: streamlit-audiorecコンポーネントを使用してください")
            st.info("🎤 **現在の録音方法**: 下の録音ボタンで音声を録音できます")
        else:
            st.success("✅ **録音環境**: ローカル環境で録音機能が利用可能です")
            st.info("🎤 **録音方法**: 下の録音ボタンまたはstreamlit-audiorecコンポーネントを使用")
        
        if not OPENAI_AVAILABLE:
            st.warning("⚠️ **AI環境**: OpenAI APIが利用できません")
            st.info("💡 **AI代替案**: OpenAI APIキーを設定してください")
        else:
            st.success("✅ **AI環境**: OpenAI APIが利用可能です")
        
        # 音声録音
        st.subheader("🎤 音声録音")
        
        # streamlit-audiorecコンポーネントを使用（エラーハンドリング付き）
        if ST_AUDIOREC_AVAILABLE:
            try:
                audio_data = st_audiorec()
            except Exception as e:
                st.error(f"音声録音コンポーネントでエラーが発生しました: {e}")
                st.info("音声録音機能を再読み込みしてください")
                audio_data = None
        else:
            st.error("音声録音機能が利用できません")
            st.info("streamlit-audiorecライブラリの読み込みに失敗しました")
            audio_data = None
        
        if audio_data is not None:
            st.session_state.audio_data = audio_data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 音声プレイヤー
            self.display_audio_player(audio_data)
            
            # ボタン列
            col1, col2 = st.columns(2)
            
            with col1:
                # 音声保存
                if st.button("💾 音声ファイルを保存", key="save_audio_main"):
                    filepath = self.save_audio_file(audio_data, timestamp)
                    if filepath:
                        st.success(f"音声ファイルを保存しました: {filepath}")
            
            with col2:
                # 文字起こし実行
                if st.button("🎯 文字起こし実行", key="transcribe_main", type="primary"):
                    with st.spinner("文字起こし中..."):
                        transcription = self.transcribe_audio(client, audio_data)
                        if transcription:
                            st.session_state.transcription = transcription
                            st.session_state.transcription_timestamp = timestamp
                            self.display_transcription_results(transcription, timestamp)
                            self.display_analysis_results(transcription)
        
        # 既存の文字起こし結果の表示
        if 'transcription' in st.session_state and st.session_state.transcription:
            self.display_transcription_results(
                st.session_state.transcription, 
                st.session_state.transcription_timestamp
            )
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
    # WebSocket接続エラーのハンドリング
    try:
        st.set_page_config(
            page_title="音声録音・文字起こしアプリ",
            page_icon="🎙️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except Exception as e:
        st.error(f"ページ設定エラー: {e}")
        st.info("ページを再読み込みしてください")
        return
    
    # 音声処理ライブラリの状況表示（サイドバーに残す）
    try:
        if UTILS_AVAILABLE:
            try:
                from src.utils_audiorec import show_audio_library_status
                show_audio_library_status()
            except Exception as e:
                st.sidebar.warning(f"音声処理ライブラリ状況の表示エラー: {e}")
        else:
            st.sidebar.warning("音声処理ライブラリ状況が確認できません")
    except Exception as e:
        st.sidebar.warning(f"音声処理ライブラリ状況の確認エラー: {e}")
    
    # アプリケーション実行
    try:
        app = AudioRecorderApp()
        app.run()
    except Exception as e:
        st.error(f"アプリケーション実行エラー: {e}")
        st.info("ページを再読み込みしてください")
        st.exception(e)


if __name__ == "__main__":
    main()
