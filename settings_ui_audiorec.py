"""
app_audiorec.py用の拡張設定UIコンポーネント
設定、ユーザー辞書、コマンド、デバイス管理などのUIを提供
"""

import streamlit as st
import os
from utils_audiorec import (
    EnhancedSettingsManager, 
    UserDictionaryManager, 
    CommandManager, 
    DeviceManager
)

def render_enhanced_settings_tab(settings_manager):
    """拡張設定タブの表示"""
    st.subheader("⚙️ 拡張設定")
    
    settings = settings_manager.load_settings()
    
    # タブを作成
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎵 音声設定", 
        "🎙️ デバイス設定", 
        "📝 文字起こし設定", 
        "🔧 UI設定", 
        "⚡ ショートカット設定"
    ])
    
    with tab1:
        render_audio_settings_tab(settings, settings_manager)
    
    with tab2:
        render_device_settings_tab(settings, settings_manager)
    
    with tab3:
        render_transcription_settings_tab(settings, settings_manager)
    
    with tab4:
        render_ui_settings_tab(settings, settings_manager)
    
    with tab5:
        render_shortcut_settings_tab(settings, settings_manager)
    
    return settings

def render_audio_settings_tab(settings, settings_manager):
    """音声設定タブ"""
    st.write("**🎵 音声設定**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**基本設定**")
        duration = st.slider("録音時間 (秒)", 1, 30, settings["audio"]["duration"])
        gain = st.slider("ゲイン", 0.1, 5.0, settings["audio"]["gain"], 0.1)
        sample_rate = st.selectbox("サンプルレート", [8000, 16000, 22050, 44100, 48000], 
                                 index=[8000, 16000, 22050, 44100, 48000].index(settings["audio"]["sample_rate"]))
        channels = st.selectbox("チャンネル数", [1, 2], index=settings["audio"]["channels"] - 1)
        
        settings["audio"]["duration"] = duration
        settings["audio"]["gain"] = gain
        settings["audio"]["sample_rate"] = sample_rate
        settings["audio"]["channels"] = channels
    
    with col2:
        st.write("**詳細設定**")
        chunk_size = st.selectbox("チャンクサイズ", [512, 1024, 2048, 4096], 
                                index=[512, 1024, 2048, 4096].index(settings["audio"]["chunk_size"]))
        format_type = st.selectbox("フォーマット", ["paInt16", "paFloat32"], 
                                 index=0 if settings["audio"]["format"] == "paInt16" else 1)
        
        settings["audio"]["chunk_size"] = chunk_size
        settings["audio"]["format"] = format_type

def render_device_settings_tab(settings, settings_manager):
    """デバイス設定タブ"""
    st.write("**🎙️ デバイス設定**")
    
    device_manager = DeviceManager()
    devices = device_manager.get_available_devices()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**マイク選択**")
        
        # デバイス一覧を表示
        device_names = [f"{d['name']} (Index: {d['index']})" for d in devices]
        selected_device_name = st.selectbox(
            "録音デバイスを選択",
            device_names,
            index=settings["device"]["selected_device_index"] or 0
        )
        
        # 選択されたデバイスのインデックスを取得
        selected_index = int(selected_device_name.split("Index: ")[1].split(")")[0])
        settings["device"]["selected_device_index"] = selected_index
        settings["device"]["selected_device_name"] = selected_device_name.split(" (Index:")[0]
        
        # デバイス情報を表示
        if selected_device_name:
            device_info = device_manager.get_device_by_index(selected_index)
            if device_info:
                st.write(f"**選択デバイス**: {device_info['name']}")
                st.write(f"**チャンネル数**: {device_info['channels']}")
                st.write(f"**サンプルレート**: {device_info['sample_rate']}Hz")
    
    with col2:
        st.write("**デバイス設定**")
        auto_select = st.checkbox("デフォルトデバイスを自動選択", settings["device"]["auto_select_default"])
        test_device = st.checkbox("デバイス選択時にテスト実行", settings["device"]["test_device_on_select"])
        
        settings["device"]["auto_select_default"] = auto_select
        settings["device"]["test_device_on_select"] = test_device
        
        if st.button("🎤 デバイステスト", key="test_device_button"):
            st.info("デバイステスト機能は現在開発中です")

def render_transcription_settings_tab(settings, settings_manager):
    """文字起こし設定タブ"""
    st.write("**📝 文字起こし設定**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Whisper設定**")
        model_size = st.selectbox("モデルサイズ", ["tiny", "base", "small", "medium", "large"], 
                                index=["tiny", "base", "small", "medium", "large"].index(settings["whisper"]["model_size"]))
        language = st.selectbox("言語", ["ja", "en", "auto"], 
                              index=["ja", "en", "auto"].index(settings["whisper"]["language"]))
        temperature = st.slider("Temperature", 0.0, 1.0, settings["whisper"]["temperature"], 0.1)
        
        settings["whisper"]["model_size"] = model_size
        settings["whisper"]["language"] = language
        settings["whisper"]["temperature"] = temperature
    
    with col2:
        st.write("**文字起こし動作**")
        auto_transcribe = st.checkbox("自動文字起こし", settings["transcription"]["auto_transcribe"])
        save_transcriptions = st.checkbox("文字起こし結果を自動保存", settings["transcription"]["save_transcriptions"])
        
        settings["transcription"]["auto_transcribe"] = auto_transcribe
        settings["transcription"]["save_transcriptions"] = save_transcriptions
        
        # 高度な設定
        with st.expander("🔧 高度なWhisper設定"):
            compression_threshold = st.slider("圧縮比閾値", 0.0, 5.0, settings["whisper"]["compression_ratio_threshold"], 0.1)
            logprob_threshold = st.slider("Logprob閾値", -5.0, 0.0, settings["whisper"]["logprob_threshold"], 0.1)
            no_speech_threshold = st.slider("無音閾値", 0.0, 1.0, settings["whisper"]["no_speech_threshold"], 0.1)
            condition_previous = st.checkbox("前のテキストを条件とする", settings["whisper"]["condition_on_previous_text"])
            
            settings["whisper"]["compression_ratio_threshold"] = compression_threshold
            settings["whisper"]["logprob_threshold"] = logprob_threshold
            settings["whisper"]["no_speech_threshold"] = no_speech_threshold
            settings["whisper"]["condition_on_previous_text"] = condition_previous

def render_ui_settings_tab(settings, settings_manager):
    """UI設定タブ"""
    st.write("**🔧 UI設定**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**基本UI設定**")
        show_advanced = st.checkbox("詳細オプションを表示", settings["ui"]["show_advanced_options"])
        auto_save = st.checkbox("録音を自動保存", settings["ui"]["auto_save_recordings"])
        show_quality = st.checkbox("音質分析を表示", settings["ui"]["show_quality_analysis"])
        show_level = st.checkbox("レベル監視を表示", settings["ui"]["show_level_monitoring"])
        
        settings["ui"]["show_advanced_options"] = show_advanced
        settings["ui"]["auto_save_recordings"] = auto_save
        settings["ui"]["show_quality_analysis"] = show_quality
        settings["ui"]["show_level_monitoring"] = show_level
    
    with col2:
        st.write("**自動録音設定**")
        auto_start = st.checkbox("自動録音開始", settings["ui"]["auto_start_recording"])
        auto_threshold = st.slider("自動録音閾値", 100, 1000, settings["ui"]["auto_recording_threshold"], 50)
        auto_delay = st.slider("自動録音遅延 (秒)", 0.1, 5.0, settings["ui"]["auto_recording_delay"], 0.1)
        
        settings["ui"]["auto_start_recording"] = auto_start
        settings["ui"]["auto_recording_threshold"] = auto_threshold
        settings["ui"]["auto_recording_delay"] = auto_delay

def render_shortcut_settings_tab(settings, settings_manager):
    """ショートカット設定タブ"""
    st.write("**⚡ ショートカット設定**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**ショートカット有効化**")
        shortcuts_enabled = st.checkbox("ショートカットを有効化", settings["shortcuts"]["enabled"])
        global_hotkeys = st.checkbox("グローバルホットキー", settings["shortcuts"]["global_hotkeys"])
        
        settings["shortcuts"]["enabled"] = shortcuts_enabled
        settings["shortcuts"]["global_hotkeys"] = global_hotkeys
    
    with col2:
        st.write("**修飾キー設定**")
        ctrl_mod = st.checkbox("Ctrlキー", settings["shortcuts"]["modifiers"]["ctrl"])
        shift_mod = st.checkbox("Shiftキー", settings["shortcuts"]["modifiers"]["shift"])
        alt_mod = st.checkbox("Altキー", settings["shortcuts"]["modifiers"]["alt"])
        
        settings["shortcuts"]["modifiers"]["ctrl"] = ctrl_mod
        settings["shortcuts"]["modifiers"]["shift"] = shift_mod
        settings["shortcuts"]["modifiers"]["alt"] = alt_mod
    
    # ショートカットキー設定
    st.write("**🎹 ショートカットキー設定**")
    
    shortcut_keys = settings["shortcuts"]["keys"]
    new_keys = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_keys["start_recording"] = st.text_input("録音開始", shortcut_keys["start_recording"])
        new_keys["stop_recording"] = st.text_input("録音停止", shortcut_keys["stop_recording"])
        new_keys["transcribe"] = st.text_input("文字起こし", shortcut_keys["transcribe"])
        new_keys["clear_text"] = st.text_input("テキストクリア", shortcut_keys["clear_text"])
    
    with col2:
        new_keys["save_recording"] = st.text_input("録音保存", shortcut_keys["save_recording"])
        new_keys["open_settings"] = st.text_input("設定を開く", shortcut_keys["open_settings"])
        new_keys["open_dictionary"] = st.text_input("辞書を開く", shortcut_keys["open_dictionary"])
        new_keys["open_commands"] = st.text_input("コマンドを開く", shortcut_keys["open_commands"])
    
    settings["shortcuts"]["keys"] = new_keys

def render_user_dictionary_tab():
    """ユーザー辞書タブ"""
    st.subheader("📚 ユーザー辞書")
    
    dictionary_manager = UserDictionaryManager()
    dictionary = dictionary_manager.dictionary
    
    # 辞書統計
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("総カテゴリ数", len(dictionary["categories"]))
    with col2:
        st.metric("総エントリ数", dictionary["metadata"]["total_entries"])
    with col3:
        st.metric("最終更新", dictionary["metadata"]["last_updated"][:10])
    
    # 新しいエントリの追加
    with st.expander("➕ 新しいエントリを追加"):
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.text_input("カテゴリ", "カスタム")
            term = st.text_input("用語")
        
        with col2:
            definition = st.text_area("定義")
            pronunciation = st.text_input("発音（オプション）")
        
        if st.button("追加", key="add_dictionary_entry"):
            if term and definition:
                if dictionary_manager.add_entry(category, term, definition, pronunciation):
                    st.success(f"✅ '{term}' を辞書に追加しました")
                    st.rerun()
                else:
                    st.error("❌ 辞書への追加に失敗しました")
            else:
                st.warning("⚠️ 用語と定義を入力してください")
    
    # 辞書の表示
    for category_name, category_data in dictionary["categories"].items():
        with st.expander(f"📁 {category_name} ({len(category_data['entries'])}件)"):
            st.write(f"**説明**: {category_data['description']}")
            
            if category_data['entries']:
                for term, entry_data in category_data['entries'].items():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{term}**")
                        st.write(f"定義: {entry_data['definition']}")
                        if entry_data['pronunciation']:
                            st.write(f"発音: {entry_data['pronunciation']}")
                    
                    with col2:
                        if st.button(f"編集", key=f"edit_{category_name}_{term}"):
                            st.info("編集機能は現在開発中です")
                    
                    with col3:
                        if st.button(f"削除", key=f"delete_{category_name}_{term}"):
                            if dictionary_manager.remove_entry(category_name, term):
                                st.success(f"✅ '{term}' を削除しました")
                                st.rerun()
                            else:
                                st.error("❌ 削除に失敗しました")
            else:
                st.info("このカテゴリにはエントリがありません")

def render_commands_tab():
    """コマンドタブ"""
    st.subheader("⚡ コマンド管理")
    
    command_manager = CommandManager()
    commands = command_manager.commands
    
    # コマンド統計
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("総コマンド数", commands["metadata"]["total_commands"])
    with col2:
        st.metric("有効コマンド数", sum(1 for cmd in commands["commands"].values() if cmd["enabled"]))
    with col3:
        st.metric("最終更新", commands["metadata"]["last_updated"][:10])
    
    # 新しいコマンドの追加
    with st.expander("➕ 新しいコマンドを追加"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("コマンド名")
            description = st.text_input("説明")
        
        with col2:
            output_format = st.selectbox("出力形式", ["text", "bullet_points", "summary", "text_file"])
            enabled = st.checkbox("有効化", True)
        
        llm_prompt = st.text_area("LLMプロンプト", placeholder="以下の文字起こし結果を処理してください：\n\n{text}")
        
        if st.button("追加", key="add_command"):
            if name and description and llm_prompt:
                if command_manager.add_command(name, description, llm_prompt, output_format, enabled):
                    st.success(f"✅ '{name}' コマンドを追加しました")
                    st.rerun()
                else:
                    st.error("❌ コマンドの追加に失敗しました")
            else:
                st.warning("⚠️ 必要な情報を入力してください")
    
    # コマンドの表示
    for cmd_name, cmd_data in commands["commands"].items():
        with st.expander(f"⚡ {cmd_name}"):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**説明**: {cmd_data['description']}")
                st.write(f"**出力形式**: {cmd_data['output_format']}")
                st.write(f"**有効**: {'✅' if cmd_data['enabled'] else '❌'}")
            
            with col2:
                if st.button(f"編集", key=f"edit_cmd_{cmd_name}"):
                    st.info("編集機能は現在開発中です")
            
            with col3:
                if st.button(f"削除", key=f"delete_cmd_{cmd_name}"):
                    if command_manager.remove_command(cmd_name):
                        st.success(f"✅ '{cmd_name}' コマンドを削除しました")
                        st.rerun()
                    else:
                        st.error("❌ 削除に失敗しました")

def render_file_management_tab():
    """ファイル管理タブ"""
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