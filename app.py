"""
Streamlit Cloud対応音声録音アプリ
HTML5 Audio API + Web Speech APIを使用したブラウザベース録音・文字起こし
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

# 環境変数を読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="音声録音・文字起こしアプリ (HTML5版)",
    page_icon="🎤",
    layout="wide"
)

class HTML5AudioRecorder:
    """HTML5 Audio API + Web Speech APIを使用した音声録音・文字起こしクラス"""
    
    def __init__(self):
        self.sample_rate = 44100
        self.channels = 1
        
    def create_recording_interface(self, duration=5):
        """HTML5 Audio API + Web Speech APIを使用した録音・文字起こしインターフェースを作成"""
        
        # HTMLとJavaScriptコード
        html_code = f"""
        <div id="recording-container">
            <div style="margin-bottom: 20px;">
                <button id="startRecording" onclick="startRecording()" style="background-color: #ff4b4b; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px;">
                    🎤 録音開始 ({duration}秒)
                </button>
                <button id="stopRecording" onclick="stopRecording()" style="background-color: #666; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; display: none;">
                    ⏹️ 録音停止
                </button>
                <button id="startTranscription" onclick="startTranscription()" style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; display: none;">
                    🎙️ リアルタイム文字起こし開始
                </button>
                <button id="stopTranscription" onclick="stopTranscription()" style="background-color: #ff9800; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; display: none;">
                    ⏹️ 文字起こし停止
                </button>
            </div>
            
            <div id="recordingStatus" style="margin: 10px 0; font-weight: bold;"></div>
            <div id="transcriptionStatus" style="margin: 10px 0; font-weight: bold; color: #4CAF50;"></div>
            
            <div id="audioSection" style="margin: 10px 0; display: none;">
                <h4>🎵 録音結果</h4>
                <audio id="audioPlayback" controls style="margin: 10px 0;"></audio>
                <div id="downloadSection" style="margin: 10px 0;">
                    <button id="downloadBtn" onclick="downloadAudio()" style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                        💾 ダウンロード
                    </button>
                </div>
            </div>
            
            <div id="transcriptionSection" style="margin: 10px 0; display: none;">
                <h4>📝 文字起こし結果</h4>
                <div id="transcriptionResult" style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; min-height: 100px; border: 1px solid #ddd;"></div>
                <div id="transcriptionActions" style="margin: 10px 0;">
                    <button id="copyTranscription" onclick="copyTranscription()" style="background-color: #2196F3; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px;">
                        📋 コピー
                    </button>
                    <button id="saveTranscription" onclick="saveTranscription()" style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px;">
                        💾 保存
                    </button>
                </div>
            </div>
        </div>

        <script>
        let mediaRecorder;
        let audioChunks = [];
        let audioBlob;
        let recordingStartTime;
        let recordingTimer;
        let recognition;
        let isTranscribing = false;
        let transcriptionText = "";
        const recordingDuration = {duration * 1000}; // ミリ秒

        // Web Speech APIの初期化
        function initSpeechRecognition() {{
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'ja-JP';
                
                recognition.onstart = () => {{
                    isTranscribing = true;
                    document.getElementById('transcriptionStatus').innerHTML = '🎙️ 文字起こし中...';
                }};
                
                recognition.onresult = (event) => {{
                    let finalTranscript = '';
                    let interimTranscript = '';
                    
                    for (let i = event.resultIndex; i < event.results.length; i++) {{
                        const transcript = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {{
                            finalTranscript += transcript;
                        }} else {{
                            interimTranscript += transcript;
                        }}
                    }}
                    
                    transcriptionText = finalTranscript;
                    document.getElementById('transcriptionResult').innerHTML = 
                        '<strong>確定:</strong> ' + finalTranscript + '<br><em>仮説:</em> ' + interimTranscript;
                }};
                
                recognition.onerror = (event) => {{
                    console.error('文字起こしエラー:', event.error);
                    document.getElementById('transcriptionStatus').innerHTML = '❌ 文字起こしエラー: ' + event.error;
                }};
                
                recognition.onend = () => {{
                    isTranscribing = false;
                    document.getElementById('transcriptionStatus').innerHTML = '✅ 文字起こし完了';
                }};
                
                return true;
            }} else {{
                alert('このブラウザはWeb Speech APIをサポートしていません');
                return false;
            }}
        }}

        async function startRecording() {{
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = (event) => {{
                    audioChunks.push(event.data);
                }};
                
                mediaRecorder.onstop = () => {{
                    audioBlob = new Blob(audioChunks, {{ type: 'audio/wav' }});
                    const audioUrl = URL.createObjectURL(audioBlob);
                    document.getElementById('audioPlayback').src = audioUrl;
                    document.getElementById('audioSection').style.display = 'block';
                    document.getElementById('startTranscription').style.display = 'inline-block';
                    
                    // Streamlitに録音完了を通知
                    window.parent.postMessage({{
                        type: 'recording_complete',
                        audioUrl: audioUrl,
                        duration: recordingDuration
                    }}, '*');
                }};
                
                mediaRecorder.start();
                recordingStartTime = Date.now();
                
                document.getElementById('startRecording').style.display = 'none';
                document.getElementById('stopRecording').style.display = 'inline-block';
                document.getElementById('recordingStatus').innerHTML = '🎤 録音中...';
                
                // 自動停止タイマー
                recordingTimer = setTimeout(() => {{
                    stopRecording();
                }}, recordingDuration);
                
            }} catch (error) {{
                console.error('録音エラー:', error);
                document.getElementById('recordingStatus').innerHTML = '❌ 録音エラー: ' + error.message;
            }}
        }}
        
        function stopRecording() {{
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {{
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                
                clearTimeout(recordingTimer);
                
                document.getElementById('startRecording').style.display = 'inline-block';
                document.getElementById('stopRecording').style.display = 'none';
                document.getElementById('recordingStatus').innerHTML = '✅ 録音完了';
            }}
        }}
        
        function startTranscription() {{
            if (initSpeechRecognition()) {{
                recognition.start();
                document.getElementById('startTranscription').style.display = 'none';
                document.getElementById('stopTranscription').style.display = 'inline-block';
                document.getElementById('transcriptionSection').style.display = 'block';
            }}
        }}
        
        function stopTranscription() {{
            if (recognition && isTranscribing) {{
                recognition.stop();
                document.getElementById('startTranscription').style.display = 'inline-block';
                document.getElementById('stopTranscription').style.display = 'none';
            }}
        }}
        
        function downloadAudio() {{
            if (audioBlob) {{
                const url = URL.createObjectURL(audioBlob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'recording_' + new Date().toISOString().slice(0, 19).replace(/:/g, '-') + '.wav';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }}
        }}
        
        function copyTranscription() {{
            if (transcriptionText) {{
                navigator.clipboard.writeText(transcriptionText).then(() => {{
                    alert('文字起こし結果をクリップボードにコピーしました');
                }});
            }}
        }}
        
        function saveTranscription() {{
            if (transcriptionText) {{
                const blob = new Blob([transcriptionText], {{ type: 'text/plain' }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'transcription_' + new Date().toISOString().slice(0, 19).replace(/:/g, '-') + '.txt';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }}
        }}
        </script>
        """
        
        return html_code

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
        
        settings["ui"]["show_advanced_options"] = show_advanced
        settings["ui"]["auto_save_recordings"] = auto_save
    
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
    st.title("🎤 音声録音・文字起こしアプリ (HTML5版)")
    st.write("Streamlit Cloud対応のブラウザベース音声録音・文字起こしアプリケーション")
    
    # 設定マネージャーの初期化
    settings_manager = SettingsManager()
    audio_recorder = HTML5AudioRecorder()
    
    # タブの作成
    tab1, tab2, tab3 = st.tabs(["🎤 録音・文字起こし", "⚙️ 設定", "📁 ファイル管理"])
    
    with tab1:
        st.subheader("🎤 音声録音・文字起こし")
        
        # 設定を読み込み
        settings = settings_manager.load_settings()
        duration = settings["audio"]["duration"]
        
        st.write(f"**録音時間**: {duration}秒")
        st.write("**機能**: 録音 + リアルタイム文字起こし")
        st.write("**注意**: このアプリはブラウザのマイク権限とWeb Speech APIを使用します")
        
        # 文字起こし機能の説明
        with st.expander("📝 文字起こし機能について"):
            st.write("""
            **Web Speech APIを使用したリアルタイム文字起こし**
            
            ✅ **特徴**:
            - ブラウザネイティブの音声認識
            - リアルタイム文字起こし
            - サーバーサイド処理不要
            - 無料で使用可能
            
            ✅ **対応ブラウザ**:
            - Chrome (推奨)
            - Edge
            - Safari (一部制限あり)
            
            ✅ **使用方法**:
            1. 録音を開始
            2. 録音完了後、「リアルタイム文字起こし開始」をクリック
            3. マイクに向かって話す
            4. リアルタイムで文字起こし結果が表示されます
            """)
        
        # HTML5録音・文字起こしインターフェースの表示
        html_code = audio_recorder.create_recording_interface(duration)
        st.components.v1.html(html_code, height=400)
        
        # 録音完了時の処理
        if st.button("録音データを確認"):
            st.info("録音データはブラウザ上で再生・ダウンロードできます")
    
    with tab2:
        settings = render_settings_tab(settings_manager)
    
    with tab3:
        render_file_management_tab()
    
    # フッター
    st.markdown("---")
    st.markdown("**Streamlit Cloud対応** - HTML5 Audio API + Web Speech APIを使用したブラウザベース録音・文字起こし")

if __name__ == "__main__":
    main() 