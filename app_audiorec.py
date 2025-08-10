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
    save_audio_file,
    save_transcription_file
)
from settings_ui_audiorec import (
    render_enhanced_settings_tab,
    render_user_dictionary_tab,
    render_commands_tab,
    render_file_management_tab,
    render_task_management_tab,
    render_calendar_management_tab,
    render_google_calendar_tab
)
from config_manager import get_secret, show_environment_info

# 環境変数を読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="音声録音・文字起こしアプリ (streamlit-audiorec版)",
    page_icon="��",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AudioTranscriptionManager:
    """音声文字起こし管理クラス"""
    
    def __init__(self) -> None:
        self.openai_client: Optional[openai.OpenAI] = None
        self.task_analyzer: Optional[TaskAnalyzer] = None
        self.event_analyzer: Optional[EventAnalyzer] = None
        self.setup_openai()
    
    def setup_openai(self) -> None:
        """OpenAI APIの設定"""
        api_key = get_secret("OPENAI_API_KEY")
        if api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.task_analyzer = TaskAnalyzer(self.openai_client)
                self.event_analyzer = EventAnalyzer(self.openai_client)
            except Exception as e:
                st.error(f"OpenAI API初期化エラー: {e}")
                self.openai_client = None
        else:
            st.warning("⚠️ OpenAI APIキーが設定されていません。文字起こし機能は利用できません。")
    
    def transcribe_audio(self, audio_data: bytes, filename: str = "recording.wav") -> tuple[Optional[str], Optional[str]]:
        """音声ファイルを文字起こし"""
        if not self.openai_client:
            return None, "OpenAI APIキーが設定されていません"
        
        try:
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            # OpenAI Whisper APIで文字起こし
            with open(tmp_file_path, "rb") as audio_file:
                response = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ja"
                )
            
            # 一時ファイルを削除
            os.unlink(tmp_file_path)
            
            return response.text, None
            
        except Exception as e:
            return None, f"文字起こしエラー: {str(e)}"
    
    def analyze_transcription_for_tasks_and_events(self, transcription_text: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
        """文字起こし結果からタスクとイベントを分析"""
        if not transcription_text:
            return [], [], ["文字起こし結果がありません"]
        
        tasks: List[Dict[str, Any]] = []
        events: List[Dict[str, Any]] = []
        errors: List[str] = []
        
        # タスク分析
        if self.task_analyzer:
            try:
                detected_tasks, task_error = self.task_analyzer.analyze_text_for_tasks(transcription_text)
                if detected_tasks:
                    tasks = detected_tasks
                if task_error:
                    errors.append(task_error)
            except Exception as e:
                errors.append(f"タスク分析エラー: {str(e)}")
        
        # イベント分析
        if self.event_analyzer:
            try:
                detected_events, event_error = self.event_analyzer.analyze_text_for_events(transcription_text)
                if detected_events:
                    events = detected_events
                if event_error:
                    errors.append(event_error)
            except Exception as e:
                errors.append(f"イベント分析エラー: {str(e)}")
        
        return tasks, events, errors

# 設定管理クラスは utils_audiorec.py に移動済み

def main() -> None:
    """メイン関数"""
    st.set_page_config(
        page_title="音声録音・文字起こしアプリ",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # カスタムCSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .shortcut-key {
        background-color: #e0e0e0;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-family: monospace;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ヘッダー
    st.markdown('<h1 class="main-header">🎤 音声録音・文字起こしアプリ</h1>', unsafe_allow_html=True)
    
    # セッション状態の初期化
    if 'audio_transcription_manager' not in st.session_state:
        st.session_state.audio_transcription_manager = AudioTranscriptionManager()
    
    if 'settings_manager' not in st.session_state:
        st.session_state.settings_manager = EnhancedSettingsManager()
    
    if 'detected_tasks' not in st.session_state:
        st.session_state.detected_tasks = []
    
    if 'detected_events' not in st.session_state:
        st.session_state.detected_events = []
    
    # タブを作成
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🎤 録音・文字起こし",
        "⚙️ 設定",
        "📋 タスク管理", 
        "📅 カレンダー",
        "🌐 Googleカレンダー",
        "📚 コマンド管理",
        "📖 ユーザー辞書",
        "📁 ファイル管理"
    ])
    
    # 録音・文字起こしタブ
    with tab1:
        st.subheader("🎤 音声録音・文字起こし")
        
        # 設定を読み込み
        settings = st.session_state.settings_manager.load_settings()
        
        st.write("**機能**: streamlit-audiorec + OpenAI Whisper API + 拡張設定機能")
        st.write("**注意**: このアプリはブラウザのマイク権限を使用します")
        
        # 文字起こし機能の説明
        with st.expander("📝 文字起こし機能について"):
            st.write("""
            **OpenAI Whisper APIを使用した高精度文字起こし**
            
            ✅ **特徴**:
            - 高精度な音声認識
            - 日本語対応
            - 自動言語検出
            - 句読点の自動挿入
            - タスク・イベント自動判定
            
            ✅ **使用方法**:
            1. 録音を開始
            2. 録音完了後、自動または手動で文字起こし
            3. 結果をコピーまたは保存
            4. タスク・イベントの自動追加
            
            ⚠️ **注意**: OpenAI APIキーが必要です
            """)
        
        # 録音インターフェース
        st.write("### 🎤 録音")
        
        # 録音ボタン
        audio = st_audiorec()
        
        if audio is not None:
            # 録音データの処理（st_audiorecは直接bytesを返す）
            audio_data = audio
            
            # 録音情報の表示（簡易版）
            st.write("**録音完了**")
            st.write(f"**データサイズ**: {len(audio_data)} bytes")
            
            # 音声プレイヤー
            st.audio(audio_data, format="audio/wav")
            
            # 自動保存
            if settings["ui"]["auto_save_recordings"]:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recording_{timestamp}.wav"
                if save_audio_file(audio_data, filename):
                    st.success(f"✅ 録音を保存しました: {filename}")
            
            # 文字起こしセクション
            st.write("### 📝 文字起こし")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎙️ 文字起こし開始"):
                    with st.spinner("文字起こし中..."):
                        transcription, error = st.session_state.audio_transcription_manager.transcribe_audio(audio_data)
                        
                        if transcription:
                            st.session_state['transcription'] = transcription
                            st.success("✅ 文字起こし完了")
                            
                            # タスク・イベント分析
                            tasks, events, analysis_errors = st.session_state.audio_transcription_manager.analyze_transcription_for_tasks_and_events(transcription)
                            
                            if tasks or events:
                                st.session_state['detected_tasks'] = tasks
                                st.session_state['detected_events'] = events
                                
                                if tasks:
                                    st.success(f"✅ {len(tasks)}個のタスクを検出しました")
                                if events:
                                    st.success(f"✅ {len(events)}個のイベントを検出しました")
                            
                            if analysis_errors:
                                for error in analysis_errors:
                                    st.warning(f"⚠️ {error}")
                        else:
                            st.error(f"❌ {error}")
            
            with col2:
                if st.button("💾 文字起こし結果を保存"):
                    if 'transcription' in st.session_state:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"transcription_{timestamp}.txt"
                        
                        if save_transcription_file(st.session_state['transcription'], filename):
                            st.success(f"✅ 文字起こし結果を保存しました: {filename}")
                        else:
                            st.error("❌ 保存エラーが発生しました")
            
            # 文字起こし結果の表示
            if 'transcription' in st.session_state:
                st.write("**文字起こし結果:**")
                st.text_area("", st.session_state['transcription'], height=200)
                
                # コピーボタン
                if st.button("📋 クリップボードにコピー"):
                    st.write("文字起こし結果をクリップボードにコピーしました")
                    st.code(st.session_state['transcription'])
                
                # タスク・イベント自動追加セクション
                if 'detected_tasks' in st.session_state or 'detected_events' in st.session_state:
                    st.write("### 🤖 自動検出結果")
                    
                    # タスク追加
                    if 'detected_tasks' in st.session_state and st.session_state['detected_tasks']:
                        st.write("**📋 検出されたタスク:**")
                        for i, task in enumerate(st.session_state['detected_tasks']):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"• {task['title']}")
                            with col2:
                                if st.button(f"➕ タスク追加", key=f"add_task_{i}"):
                                    if TaskManager().add_task(
                                        title=task['title'],
                                        description=task['description'],
                                        priority=task.get('priority', 'medium'),
                                        category=task.get('category', '音声文字起こし')
                                    ):
                                        st.success("✅ タスクを追加しました")
                                    else:
                                        st.error("❌ タスクの追加に失敗しました")
                    
                    # イベント追加
                    if 'detected_events' in st.session_state and st.session_state['detected_events']:
                        st.write("**📅 検出されたイベント:**")
                        for i, event in enumerate(st.session_state['detected_events']):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"• {event['title']}")
                            with col2:
                                if st.button(f"➕ イベント追加", key=f"add_event_{i}"):
                                    if CalendarManager().add_event(
                                        title=event['title'],
                                        description=event['description'],
                                        category=event.get('category', '音声文字起こし')
                                    ):
                                        st.success("✅ イベントを追加しました")
                                    else:
                                        st.error("❌ イベントの追加に失敗しました")
    
    # 設定タブ
    with tab2:
        render_enhanced_settings_tab(st.session_state.settings_manager)
    
    # タスク管理タブ
    with tab3:
        render_task_management_tab()
    
    # カレンダータブ
    with tab4:
        render_calendar_management_tab()
    
    # Googleカレンダータブ
    with tab5:
        render_google_calendar_tab()
    
    # コマンド管理タブ
    with tab6:
        render_commands_tab()
    
    # ユーザー辞書タブ
    with tab7:
        render_user_dictionary_tab()
    
    # ファイル管理タブ
    with tab8:
        render_file_management_tab()
    
    # ショートカットキー説明
    with st.expander("⌨️ ショートカットキー"):
        st.markdown("""
        **録音・文字起こし:**
        - `F11`: 録音開始/停止
        - `Ctrl+S`: 文字起こし結果を保存
        
        **タスク・イベント管理:**
        - `Ctrl+T`: タスク追加
        - `Ctrl+E`: イベント追加
        - `Ctrl+Shift+T`: タスク管理タブを開く
        - `Ctrl+Shift+E`: カレンダータブを開く
        
        **Googleカレンダー:**
        - `Ctrl+Shift+G`: Googleカレンダータブを開く
        """)
    
    # 環境情報の表示（サイドバー）
    show_environment_info()
    
    # フッター
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🎤 音声録音・文字起こしアプリ | 
        📋 タスク管理 | 📅 カレンダー管理 | 🌐 Googleカレンダー連携 | 
        🤖 AI自動判定 | ⌨️ ショートカットキー対応</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 