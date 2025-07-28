"""
Streamlit Cloud対応音声録音＆文字起こしアプリ
sounddeviceを使用してPyAudioの代替実装
"""

import streamlit as st
import sounddevice as sd
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
    page_title="音声録音＆文字起こし (sounddevice版)",
    page_icon="🎤",
    layout="wide"
)

class SoundDeviceAudioProcessor:
    """sounddeviceを使用した音声処理クラス"""
    
    def __init__(self):
        self.sample_rate = 44100
        self.channels = 1
        self.dtype = np.int16
        self.chunk = 1024
        
    def get_audio_devices(self):
        """利用可能な音声デバイスを取得"""
        try:
            devices = sd.query_devices()
            input_devices = []
            
            for i, device in enumerate(devices):
                if device['max_inputs'] > 0:
                    input_devices.append({
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_inputs'],
                        'sample_rate': device['default_samplerate']
                    })
            
            return input_devices
        except Exception as e:
            st.error(f"デバイス取得エラー: {e}")
            return []
    
    def record_audio(self, duration, device_index=None, gain=1.0):
        """音声を録音する"""
        try:
            st.info(f"🎤 {duration}秒間録音を開始します...")
            
            # 録音パラメータ設定
            frames = int(duration * self.sample_rate)
            
            # 録音実行
            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                device=device_index
            )
            
            # 録音完了まで待機
            sd.wait()
            
            # ゲイン調整
            if gain != 1.0:
                recording = (recording * gain).astype(self.dtype)
            
            st.success("✅ 録音が完了しました！")
            return recording, self.sample_rate
            
        except Exception as e:
            st.error(f"❌ 録音エラー: {e}")
            return None, None
    
    def monitor_audio_level(self, device_index=None, duration=3):
        """音声レベルを監視"""
        try:
            st.info("🔍 音声レベルを監視中...")
            
            # 短時間録音でレベル測定
            frames = int(duration * self.sample_rate)
            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                device=device_index
            )
            
            sd.wait()
            
            # レベル計算
            levels = np.abs(recording)
            avg_level = np.mean(levels)
            max_level = np.max(levels)
            
            return avg_level, max_level, levels
            
        except Exception as e:
            st.error(f"❌ レベル監視エラー: {e}")
            return 0, 0, []
    
    def save_audio_file(self, audio_data, sample_rate, filename):
        """音声データをWAVファイルとして保存"""
        try:
            # recordingsディレクトリの作成
            os.makedirs('recordings', exist_ok=True)
            
            # WAVファイルとして保存
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            return True
            
        except Exception as e:
            st.error(f"❌ ファイル保存エラー: {e}")
            return False
    
    def create_download_link(self, audio_data, sample_rate, filename):
        """音声ファイルのダウンロードリンクを生成"""
        try:
            # 音声データをWAVファイルとしてエンコード
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
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

class SettingsManager:
    """設定管理クラス"""
    
    def __init__(self):
        self.settings_file = "settings/app_settings.json"
        self.default_settings = {
            "audio": {
                "duration": 10,
                "gain": 1.0,
                "sample_rate": 44100,
                "channels": 1
            },
            "ui": {
                "auto_save_recordings": True,
                "show_advanced_options": False,
                "theme": "light"
            },
            "device": {
                "auto_select": True,
                "default_device": None
            }
        }
    
    def load_settings(self):
        """設定を読み込み"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.default_settings.copy()
        except Exception as e:
            st.error(f"設定読み込みエラー: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings):
        """設定を保存"""
        try:
            os.makedirs('settings', exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"設定保存エラー: {e}")
            return False

def render_settings_tab(settings_manager, audio_processor):
    """設定タブをレンダリング"""
    st.subheader("⚙️ 設定")
    
    settings = settings_manager.load_settings()
    
    # 音声設定
    st.markdown("#### 🎤 音声設定")
    col1, col2 = st.columns(2)
    
    with col1:
        duration = st.number_input(
            "録音時間（秒）",
            min_value=1,
            max_value=300,
            value=settings['audio']['duration'],
            help="録音する時間を秒単位で設定"
        )
        settings['audio']['duration'] = duration
    
    with col2:
        gain = st.slider(
            "音声ゲイン",
            min_value=0.1,
            max_value=5.0,
            value=settings['audio']['gain'],
            step=0.1,
            help="音声の音量を調整"
        )
        settings['audio']['gain'] = gain
    
    # デバイス設定
    st.markdown("#### 🔧 デバイス設定")
    devices = audio_processor.get_audio_devices()
    
    if devices:
        device_names = [f"{d['name']} (ID: {d['index']})" for d in devices]
        selected_device_name = st.selectbox(
            "録音デバイスを選択",
            device_names,
            index=0,
            help="録音に使用するマイクデバイスを選択"
        )
        
        # 選択されたデバイスのインデックスを取得
        selected_device_index = None
        for device in devices:
            if f"{device['name']} (ID: {device['index']})" == selected_device_name:
                selected_device_index = device['index']
                break
        
        settings['device']['selected_device'] = selected_device_index
        settings['device']['selected_device_name'] = selected_device_name
        
        # デバイステスト
        if st.button("🎤 デバイステスト", type="secondary"):
            if selected_device_index is not None:
                avg_level, max_level, levels = audio_processor.monitor_audio_level(
                    selected_device_index, duration=3
                )
                
                st.write(f"**平均音声レベル**: {avg_level:.1f}")
                st.write(f"**最大音声レベル**: {max_level:.1f}")
                
                # レベルバー表示
                st.progress(min(avg_level / 1000, 1.0))
                
                if avg_level < 100:
                    st.warning("⚠️ 音声レベルが低いです。マイクの音量を上げてください。")
                elif avg_level < 500:
                    st.info("ℹ️ 音声レベルは正常です。")
                else:
                    st.success("✅ 音声レベルが良好です。")
    else:
        st.warning("⚠️ 音声デバイスが見つかりません")
    
    # UI設定
    st.markdown("#### 🎨 UI設定")
    auto_save = st.checkbox(
        "録音を自動保存",
        value=settings['ui']['auto_save_recordings'],
        help="録音完了時に自動的にファイルを保存"
    )
    settings['ui']['auto_save_recordings'] = auto_save
    
    show_advanced = st.checkbox(
        "高度なオプションを表示",
        value=settings['ui']['show_advanced_options'],
        help="高度な機能を表示"
    )
    settings['ui']['show_advanced_options'] = show_advanced
    
    # 設定保存ボタン
    if st.button("💾 設定を保存", type="primary"):
        if settings_manager.save_settings(settings):
            st.success("✅ 設定を保存しました")
        else:
            st.error("❌ 設定の保存に失敗しました")
    
    return settings

def render_file_management_tab():
    """ファイル管理タブをレンダリング"""
    st.subheader("📁 ファイル管理")
    
    # recordingsディレクトリの確認
    if os.path.exists('recordings'):
        files = [f for f in os.listdir('recordings') if f.endswith('.wav')]
        
        if files:
            st.markdown("#### 📂 録音ファイル一覧")
            
            for file in files:
                file_path = os.path.join('recordings', file)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"📄 {file}")
                
                with col2:
                    st.write(f"{file_size / 1024:.1f} KB")
                
                with col3:
                    st.write(file_time.strftime("%Y-%m-%d %H:%M"))
                
                with col4:
                    if st.button("🗑️", key=f"delete_{file}"):
                        try:
                            os.remove(file_path)
                            st.success(f"✅ {file} を削除しました")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 削除エラー: {e}")
        else:
            st.info("📝 録音ファイルがありません")
    else:
        st.info("📝 recordingsディレクトリがありません")

def main():
    """メインアプリケーション"""
    st.title("🎤 音声録音＆文字起こし (sounddevice版)")
    st.markdown("---")
    
    # クラスの初期化
    audio_processor = SoundDeviceAudioProcessor()
    settings_manager = SettingsManager()
    
    # 設定を読み込み
    settings = settings_manager.load_settings()
    
    # セッション状態の初期化
    if 'current_transcription' not in st.session_state:
        st.session_state['current_transcription'] = ""
    if 'recorded_audio' not in st.session_state:
        st.session_state['recorded_audio'] = None
    if 'recorded_rate' not in st.session_state:
        st.session_state['recorded_rate'] = None
    
    # ヘッダー部分
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 🎤 録音・文字起こし")
    with col2:
        if st.button("⚙️ 設定", help="詳細設定を開く", type="secondary"):
            st.session_state['show_settings'] = True
    
    # 設定画面の表示
    if st.session_state.get('show_settings', False):
        st.markdown("---")
        settings = render_settings_tab(settings_manager, audio_processor)
        
        # ファイル管理タブ
        st.markdown("---")
        render_file_management_tab()
    
    # 録音セクション
    st.markdown("---")
    st.subheader("🎤 録音")
    
    # 録音時間設定
    col1, col2 = st.columns(2)
    with col1:
        recording_duration = st.number_input(
            "録音時間（秒）",
            min_value=1,
            max_value=300,
            value=settings['audio']['duration'],
            help="録音する時間を秒単位で設定"
        )
    
    with col2:
        st.markdown(f"**現在の設定**: {recording_duration}秒")
        if recording_duration < 5:
            st.warning("⚠️ 短い録音時間は音声認識の精度に影響する可能性があります")
        elif recording_duration > 60:
            st.info("ℹ️ 長い録音時間は処理に時間がかかります")
    
    # デバイス選択
    devices = audio_processor.get_audio_devices()
    selected_device_index = None
    
    if devices:
        device_names = [f"{d['name']} (ID: {d['index']})" for d in devices]
        selected_device_name = st.selectbox(
            "録音デバイスを選択",
            device_names,
            index=0,
            help="録音に使用するマイクデバイスを選択"
        )
        
        # 選択されたデバイスのインデックスを取得
        for device in devices:
            if f"{device['name']} (ID: {device['index']})" == selected_device_name:
                selected_device_index = device['index']
                break
    else:
        st.warning("⚠️ 音声デバイスが見つかりません")
    
    # 録音ボタン
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎤 録音開始", type="primary", disabled=selected_device_index is None):
            if selected_device_index is not None:
                with st.spinner("録音中..."):
                    audio_data, sample_rate = audio_processor.record_audio(
                        recording_duration,
                        selected_device_index,
                        settings['audio']['gain']
                    )
                    
                    if audio_data is not None:
                        st.session_state['recorded_audio'] = audio_data
                        st.session_state['recorded_rate'] = sample_rate
                        st.session_state['recorded_device'] = selected_device_name
                        
                        # 自動保存
                        if settings['ui']['auto_save_recordings']:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            device_name = selected_device_name.replace(" ", "_").replace("(", "").replace(")", "")
                            filename = f"recordings/recording_{device_name}_{timestamp}.wav"
                            
                            if audio_processor.save_audio_file(audio_data, sample_rate, filename):
                                st.session_state['saved_audio_file'] = filename
                                st.success(f"✅ 録音を保存しました: {filename}")
                            else:
                                st.error("❌ 録音の保存に失敗しました")
                        
                        st.success("✅ 録音が完了しました！")
                        st.rerun()
                    else:
                        st.error("❌ 録音に失敗しました")
    
    with col2:
        if st.button("🔍 マイクレベルテスト", type="secondary", disabled=selected_device_index is None):
            if selected_device_index is not None:
                avg_level, max_level, levels = audio_processor.monitor_audio_level(
                    selected_device_index, duration=3
                )
                
                st.write(f"**平均音声レベル**: {avg_level:.1f}")
                st.write(f"**最大音声レベル**: {max_level:.1f}")
                
                # レベルバー表示
                st.progress(min(avg_level / 1000, 1.0))
                
                if avg_level < 100:
                    st.warning("⚠️ 音声レベルが低いです。マイクの音量を上げてください。")
                elif avg_level < 500:
                    st.info("ℹ️ 音声レベルは正常です。")
                else:
                    st.success("✅ 音声レベルが良好です。")
    
    # 録音結果の表示
    if st.session_state.get('recorded_audio') is not None:
        st.markdown("---")
        st.subheader("📊 録音結果")
        
        audio_data = st.session_state['recorded_audio']
        sample_rate = st.session_state['recorded_rate']
        
        # 録音情報
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("録音時間", f"{len(audio_data) / sample_rate:.1f}秒")
        with col2:
            st.metric("サンプルレート", f"{sample_rate}Hz")
        with col3:
            st.metric("データサイズ", f"{len(audio_data)} サンプル")
        
        # 音声波形の表示
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(12, 4))
        time_axis = np.linspace(0, len(audio_data) / sample_rate, len(audio_data))
        ax.plot(time_axis, audio_data)
        ax.set_title("音声波形")
        ax.set_xlabel("時間 (秒)")
        ax.set_ylabel("振幅")
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
        
        # ダウンロードリンク
        if st.button("📥 録音をダウンロード", type="secondary"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"
            
            download_link = audio_processor.create_download_link(
                audio_data, sample_rate, filename
            )
            
            if download_link:
                st.markdown(download_link, unsafe_allow_html=True)
    
    # 文字起こしセクション（簡易版）
    st.markdown("---")
    st.subheader("📝 文字起こし")
    
    st.info("💡 **注意**: Streamlit Cloud環境では、音声認識機能は別途実装が必要です。")
    st.info("📝 現在は録音機能のみ実装されています。")
    
    # 高度なオプション
    if settings['ui']['show_advanced_options']:
        st.markdown("---")
        st.subheader("🔧 高度なオプション")
        
        # 音声分析
        if st.session_state.get('recorded_audio') is not None:
            st.markdown("#### 📊 音声分析")
            
            audio_data = st.session_state['recorded_audio']
            
            # 基本統計
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("平均値", f"{np.mean(audio_data):.2f}")
            with col2:
                st.metric("標準偏差", f"{np.std(audio_data):.2f}")
            with col3:
                st.metric("最大値", f"{np.max(audio_data):.0f}")
            with col4:
                st.metric("最小値", f"{np.min(audio_data):.0f}")
            
            # スペクトログラム（簡易版）
            if st.button("📈 スペクトログラムを表示"):
                try:
                    from scipy import signal
                    
                    # FFT計算
                    f, t, Sxx = signal.spectrogram(audio_data, sample_rate)
                    
                    fig, ax = plt.subplots(figsize=(12, 6))
                    im = ax.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
                    ax.set_ylabel('周波数 [Hz]')
                    ax.set_xlabel('時間 [秒]')
                    ax.set_title('スペクトログラム')
                    fig.colorbar(im, ax=ax, label='パワー [dB]')
                    
                    st.pyplot(fig)
                except ImportError:
                    st.error("❌ scipyライブラリが必要です")
                except Exception as e:
                    st.error(f"❌ スペクトログラム生成エラー: {e}")

if __name__ == "__main__":
    main() 