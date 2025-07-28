"""
Streamlit Cloud環境用音声録音アプリ
PyAudioの代わりにsounddeviceを使用
"""

import streamlit as st
import sounddevice as sd
import numpy as np
import wave
import io
import base64
from datetime import datetime
import os
import tempfile

# ページ設定
st.set_page_config(
    page_title="音声録音アプリ",
    page_icon="🎤",
    layout="wide"
)

class StreamlitAudioRecorder:
    """Streamlit Cloud環境での音声録音クラス"""
    
    def __init__(self):
        self.sample_rate = 44100
        self.channels = 1
        self.dtype = np.int16
        
    def record_audio(self, duration=5):
        """音声を録音する"""
        try:
            st.info(f"🎤 {duration}秒間録音を開始します...")
            
            # 録音実行
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype
            )
            
            # 録音完了まで待機
            sd.wait()
            
            st.success("✅ 録音が完了しました！")
            return recording
            
        except Exception as e:
            st.error(f"❌ 録音エラー: {e}")
            return None
    
    def play_audio(self, audio_data):
        """音声を再生する"""
        try:
            st.info("🔊 音声を再生中...")
            sd.play(audio_data, self.sample_rate)
            sd.wait()
            st.success("✅ 再生が完了しました")
        except Exception as e:
            st.error(f"❌ 再生エラー: {e}")
    
    def save_audio_file(self, audio_data, filename):
        """音声データをWAVファイルとして保存"""
        try:
            # 一時ファイルとして保存
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                with wave.open(tmp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(self.channels)
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(audio_data.tobytes())
                
                return tmp_file.name
        except Exception as e:
            st.error(f"❌ ファイル保存エラー: {e}")
            return None
    
    def create_download_link(self, audio_data, filename):
        """音声ファイルのダウンロードリンクを生成"""
        try:
            # 音声データをWAVファイルとしてエンコード
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            # Base64エンコード
            b64_audio = base64.b64encode(buffer.getvalue()).decode()
            
            # ダウンロードリンクを生成
            download_link = f"""
            <a href="data:audio/wav;base64,{b64_audio}" 
               download="{filename}" 
               style="display: inline-block; padding: 10px 20px; 
                      background-color: #4CAF50; color: white; 
                      text-decoration: none; border-radius: 5px;">
               📥 {filename} をダウンロード
            </a>
            """
            
            return download_link
            
        except Exception as e:
            st.error(f"❌ ダウンロードリンク生成エラー: {e}")
            return None

def main():
    """メインアプリケーション"""
    st.title("🎤 Streamlit Cloud音声録音アプリ")
    st.markdown("---")
    
    # 音声録音クラスの初期化
    recorder = StreamlitAudioRecorder()
    
    # サイドバー設定
    with st.sidebar:
        st.header("⚙️ 設定")
        duration = st.slider("録音時間（秒）", 1, 30, 5)
        st.markdown("---")
        st.info("💡 **注意**: Streamlit Cloud環境では、ブラウザの音声アクセス許可が必要です。")
    
    # メインコンテンツ
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("🎙️ 録音")
        
        if st.button("🎤 録音開始", type="primary", use_container_width=True):
            # 録音実行
            audio_data = recorder.record_audio(duration)
            
            if audio_data is not None:
                # 音声データをセッション状態に保存
                st.session_state.audio_data = audio_data
                st.session_state.filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                
                # 録音情報を表示
                st.metric("録音時間", f"{duration}秒")
                st.metric("サンプルレート", f"{recorder.sample_rate}Hz")
                st.metric("チャンネル数", recorder.channels)
    
    with col2:
        st.header("🔊 再生・ダウンロード")
        
        if 'audio_data' in st.session_state:
            # 再生ボタン
            if st.button("🔊 録音を再生", use_container_width=True):
                recorder.play_audio(st.session_state.audio_data)
            
            st.markdown("---")
            
            # ダウンロードリンク
            download_link = recorder.create_download_link(
                st.session_state.audio_data, 
                st.session_state.filename
            )
            
            if download_link:
                st.markdown("📥 **ダウンロード**:")
                st.markdown(download_link, unsafe_allow_html=True)
        else:
            st.info("📝 録音を開始してください")
    
    # 録音履歴
    st.markdown("---")
    st.header("📁 録音履歴")
    
    # セッション状態の録音データを表示
    if 'audio_data' in st.session_state:
        st.success(f"最新の録音: {st.session_state.filename}")
        
        # 音声波形の表示（簡易版）
        audio_data = st.session_state.audio_data
        if len(audio_data.shape) > 1:
            audio_data = audio_data.flatten()
        
        # 波形プロット
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(audio_data[:10000])  # 最初の10000サンプルのみ表示
        ax.set_title("音声波形")
        ax.set_xlabel("サンプル")
        ax.set_ylabel("振幅")
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
    else:
        st.info("📝 録音データがありません")

if __name__ == "__main__":
    main() 