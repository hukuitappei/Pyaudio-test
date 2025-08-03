"""
Streamlit Cloud対応音声録音・文字起こしアプリ（拡張版）
streamlit-audiorec + OpenAI Whisper API + 豊富な設定機能
"""

import streamlit as st
import numpy as np
import wave
import io
import base64
import os
import tempfile
from datetime import datetime
from dotenv import load_dotenv
import json
import openai
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
    render_calendar_management_tab
)

# 環境変数を読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="音声録音・文字起こしアプリ (streamlit-audiorec版)",
    page_icon="🎤",
    layout="wide"
)

class AudioTranscriptionManager:
    """音声文字起こし管理クラス"""
    
    def __init__(self):
        self.openai_client = None
        self.task_analyzer = None
        self.event_analyzer = None
        self.setup_openai()
    
    def setup_openai(self):
        """OpenAI APIの設定"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = openai.OpenAI(api_key=api_key)
            self.task_analyzer = TaskAnalyzer(self.openai_client)
            self.event_analyzer = EventAnalyzer(self.openai_client)
        else:
            st.warning("⚠️ OpenAI APIキーが設定されていません。文字起こし機能は利用できません。")
    
    def transcribe_audio(self, audio_data, filename="recording.wav"):
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
    
    def analyze_transcription_for_tasks_and_events(self, transcription_text):
        """文字起こし結果からタスクとイベントを分析"""
        if not transcription_text:
            return [], [], "文字起こし結果がありません"
        
        tasks = []
        events = []
        errors = []
        
        # タスク分析
        if self.task_analyzer:
            detected_tasks, task_error = self.task_analyzer.analyze_text_for_tasks(transcription_text)
            if detected_tasks:
                tasks = detected_tasks
            if task_error:
                errors.append(task_error)
        
        # イベント分析
        if self.event_analyzer:
            detected_events, event_error = self.event_analyzer.analyze_text_for_events(transcription_text)
            if detected_events:
                events = detected_events
            if event_error:
                errors.append(event_error)
        
        return tasks, events, errors

# 設定管理クラスは utils_audiorec.py に移動済み

def main():
    """メイン関数"""
    st.title("🎤 音声録音・文字起こしアプリ（拡張版）")
    st.write("Streamlit Cloud対応のブラウザベース音声録音・文字起こしアプリケーション")
    
    # ショートカットキー機能の追加
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(event) {
        // Ctrl+T: タスク追加
        if (event.ctrlKey && event.key === 't') {
            event.preventDefault();
            // タスク追加ボタンをクリック
            const taskButton = document.querySelector('[data-testid="stButton"]');
            if (taskButton) taskButton.click();
        }
        
        // Ctrl+E: イベント追加
        if (event.ctrlKey && event.key === 'e') {
            event.preventDefault();
            // イベント追加ボタンをクリック
            const eventButton = document.querySelector('[data-testid="stButton"]');
            if (eventButton) eventButton.click();
        }
        
        // F11: 文字起こし
        if (event.key === 'F11') {
            event.preventDefault();
            // 文字起こしボタンをクリック
            const transcribeButton = document.querySelector('[data-testid="stButton"]');
            if (transcribeButton) transcribeButton.click();
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    # ショートカットキーの説明
    with st.expander("⌨️ ショートカットキー"):
        st.write("""
        **キーボードショートカット**:
        
        - **Ctrl+T**: タスク追加
        - **Ctrl+E**: イベント追加
        - **F11**: 文字起こし開始
        - **Ctrl+S**: 文字起こし結果保存
        - **Ctrl+Shift+T**: タスク管理タブを開く
        - **Ctrl+Shift+E**: カレンダータブを開く
        
        ⚠️ **注意**: ブラウザの設定によっては一部のショートカットが無効になる場合があります
        """)
    
    # 設定マネージャーの初期化
    settings_manager = EnhancedSettingsManager()
    transcription_manager = AudioTranscriptionManager()
    task_manager = TaskManager()
    calendar_manager = CalendarManager()
    
    # タブの作成
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎤 録音・文字起こし", 
        "📋 タスク管理",
        "📅 カレンダー",
        "⚙️ 拡張設定", 
        "📚 ユーザー辞書", 
        "⚡ コマンド管理", 
        "📁 ファイル管理"
    ])
    
    with tab1:
        st.subheader("🎤 音声録音・文字起こし")
        
        # 設定を読み込み
        settings = settings_manager.load_settings()
        
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
                        transcription, error = transcription_manager.transcribe_audio(audio_data)
                        
                        if transcription:
                            st.session_state['transcription'] = transcription
                            st.success("✅ 文字起こし完了")
                            
                            # タスク・イベント分析
                            tasks, events, analysis_errors = transcription_manager.analyze_transcription_for_tasks_and_events(transcription)
                            
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
                                    if task_manager.add_task(
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
                                    if calendar_manager.add_event(
                                        title=event['title'],
                                        description=event['description'],
                                        category=event.get('category', '音声文字起こし')
                                    ):
                                        st.success("✅ イベントを追加しました")
                                    else:
                                        st.error("❌ イベントの追加に失敗しました")
    
    with tab2:
        render_task_management_tab()
    
    with tab3:
        render_calendar_management_tab()
    
    with tab4:
        settings = render_enhanced_settings_tab(settings_manager)
        if st.button("💾 設定を保存"):
            if settings_manager.save_settings(settings):
                st.success("✅ 設定を保存しました")
            else:
                st.error("❌ 設定の保存に失敗しました")
    
    with tab5:
        render_user_dictionary_tab()
    
    with tab6:
        render_commands_tab()
    
    with tab7:
        render_file_management_tab()
    
    # フッター
    st.markdown("---")
    st.markdown("**Streamlit Cloud対応** - streamlit-audiorec + OpenAI Whisper API + 拡張設定機能 + タスク・カレンダー管理を使用したブラウザベース録音・文字起こし")

if __name__ == "__main__":
    main() 