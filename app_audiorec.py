"""
Streamlit Cloud対応音声録音・文字起こしアプリ
streamlit-audiorec + OpenAI Whisper APIを使用
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
from audiorecorder import audiorecorder

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
        self.setup_openai()
    
    def setup_openai(self):
        """OpenAI APIの設定"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = openai.OpenAI(api_key=api_key)
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

class SettingsManager:
    """アプリケーション設定管理クラス"""
    
    def __init__(self):
        self.settings_file = "settings/app_settings.json"
        self.ensure_settings_directory()
    
    def ensure_settings_directory(self):
        """設定ディレクトリの作成"""
        os.makedirs("settings", exist_ok=True)
    
    def load_settings(self):
        """設定を読み込み"""
        default_settings = {
            "audio": {
                "duration": 5,
                "gain": 1.0
            },
            "ui": {
                "show_advanced_options": False,
                "auto_save_recordings": True
            },
            "transcription": {
                "auto_transcribe": False,
                "save_transcriptions": True
            }
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return default_settings
        except Exception as e:
            st.error(f"設定読み込みエラー: {e}")
            return default_settings
    
    def save_settings(self, settings):
        """設定を保存"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"設定保存エラー: {e}")

def save_audio_file(audio_data, filename):
    """音声ファイルを保存"""
    try:
        os.makedirs("recordings", exist_ok=True)
        filepath = os.path.join("recordings", filename)
        with open(filepath, "wb") as f:
            f.write(audio_data)
        return True
    except Exception as e:
        st.error(f"ファイル保存エラー: {e}")
        return False

def render_settings_tab(settings_manager):
    """設定タブの表示"""
    st.subheader("⚙️ 設定")
    
    settings = settings_manager.load_settings()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**録音設定**")
        duration = st.slider("録音時間 (秒)", 1, 30, settings["audio"]["duration"])
        gain = st.slider("ゲイン", 0.1, 5.0, settings["audio"]["gain"], 0.1)
        
        settings["audio"]["duration"] = duration
        settings["audio"]["gain"] = gain
    
    with col2:
        st.write("**UI設定**")
        show_advanced = st.checkbox("詳細オプションを表示", settings["ui"]["show_advanced_options"])
        auto_save = st.checkbox("録音を自動保存", settings["ui"]["auto_save_recordings"])
        auto_transcribe = st.checkbox("自動文字起こし", settings["transcription"]["auto_transcribe"])
        save_transcriptions = st.checkbox("文字起こし結果を保存", settings["transcription"]["save_transcriptions"])
        
        settings["ui"]["show_advanced_options"] = show_advanced
        settings["ui"]["auto_save_recordings"] = auto_save
        settings["transcription"]["auto_transcribe"] = auto_transcribe
        settings["transcription"]["save_transcriptions"] = save_transcriptions
    
    if st.button("設定を保存"):
        settings_manager.save_settings(settings)
        st.success("✅ 設定を保存しました")
    
    return settings

def render_file_management_tab():
    """ファイル管理タブの表示"""
    st.subheader("📁 ファイル管理")
    
    # recordingsディレクトリの確認
    recordings_dir = "recordings"
    os.makedirs(recordings_dir, exist_ok=True)
    
    # 録音ファイルの一覧表示
    files = [f for f in os.listdir(recordings_dir) if f.endswith('.wav')]
    
    if not files:
        st.info("📁 録音ファイルがありません")
        return
    
    st.write(f"**録音ファイル ({len(files)}件)**")
    
    for file in files:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"🎵 {file}")
        
        with col2:
            file_path = os.path.join(recordings_dir, file)
            with open(file_path, "rb") as f:
                st.download_button(
                    label="📥 ダウンロード",
                    data=f.read(),
                    file_name=file,
                    mime="audio/wav"
                )
        
        with col3:
            if st.button(f"🗑️ 削除", key=f"delete_{file}"):
                try:
                    os.remove(file_path)
                    st.success(f"✅ {file} を削除しました")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 削除エラー: {e}")

def main():
    """メイン関数"""
    st.title("🎤 音声録音・文字起こしアプリ (streamlit-audiorec版)")
    st.write("Streamlit Cloud対応のブラウザベース音声録音・文字起こしアプリケーション")
    
    # 設定マネージャーの初期化
    settings_manager = SettingsManager()
    transcription_manager = AudioTranscriptionManager()
    
    # タブの作成
    tab1, tab2, tab3 = st.tabs(["🎤 録音・文字起こし", "⚙️ 設定", "📁 ファイル管理"])
    
    with tab1:
        st.subheader("🎤 音声録音・文字起こし")
        
        # 設定を読み込み
        settings = settings_manager.load_settings()
        
        st.write("**機能**: streamlit-audiorec + OpenAI Whisper API")
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
            
            ✅ **使用方法**:
            1. 録音を開始
            2. 録音完了後、自動または手動で文字起こし
            3. 結果をコピーまたは保存
            
            ⚠️ **注意**: OpenAI APIキーが必要です
            """)
        
        # 録音インターフェース
        st.write("### 🎤 録音")
        
        # 録音ボタン
        audio = audiorecorder("🎤 録音開始", "⏹️ 録音停止")
        
        if audio is not None:
            # 録音データの処理
            audio_data = audio.export()
            
            # 録音情報の表示
            st.write(f"**録音時間**: {len(audio)}秒")
            st.write(f"**サンプルレート**: {audio.sample_rate}Hz")
            
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
                        else:
                            st.error(f"❌ {error}")
            
            with col2:
                if st.button("💾 文字起こし結果を保存"):
                    if 'transcription' in st.session_state:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"transcription_{timestamp}.txt"
                        
                        try:
                            os.makedirs("transcriptions", exist_ok=True)
                            filepath = os.path.join("transcriptions", filename)
                            with open(filepath, "w", encoding="utf-8") as f:
                                f.write(st.session_state['transcription'])
                            st.success(f"✅ 文字起こし結果を保存しました: {filename}")
                        except Exception as e:
                            st.error(f"❌ 保存エラー: {e}")
                    else:
                        st.warning("文字起こし結果がありません")
            
            # 文字起こし結果の表示
            if 'transcription' in st.session_state:
                st.write("**文字起こし結果:**")
                st.text_area("", st.session_state['transcription'], height=200)
                
                # コピーボタン
                if st.button("📋 クリップボードにコピー"):
                    st.write("文字起こし結果をクリップボードにコピーしました")
                    st.code(st.session_state['transcription'])
    
    with tab2:
        settings = render_settings_tab(settings_manager)
    
    with tab3:
        render_file_management_tab()
    
    # フッター
    st.markdown("---")
    st.markdown("**Streamlit Cloud対応** - streamlit-audiorec + OpenAI Whisper APIを使用したブラウザベース録音・文字起こし")

if __name__ == "__main__":
    main() 