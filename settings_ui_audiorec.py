"""
app_audiorec.py用の拡張設定UIコンポーネント
設定、ユーザー辞書、コマンド、デバイス管理などのUIを提供
"""

# 標準ライブラリ
import json
import os
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional

# サードパーティライブラリ
import streamlit as st

# ローカルインポート
from utils_audiorec import (
    EnhancedSettingsManager, CommandManager, UserDictionaryManager,
    TaskManager, CalendarManager, TaskAnalyzer, EventAnalyzer,
    GoogleCalendarManager, DeviceManager
)

def render_enhanced_settings_tab(settings_manager: EnhancedSettingsManager) -> Dict[str, Any]:
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

def render_audio_settings_tab(settings: Dict[str, Any], settings_manager: EnhancedSettingsManager) -> None:
    """音声設定タブ"""
    st.write("**🎵 音声設定**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**録音設定**")
        
        # 録音設定のキーを一意にする
        audio_sample_rate_key = f"audio_sample_rate_{uuid.uuid4().hex[:8]}"
        audio_gain_key = f"audio_gain_{uuid.uuid4().hex[:8]}"
        audio_duration_key = f"audio_duration_{uuid.uuid4().hex[:8]}"
        
        sample_rate = st.selectbox("サンプルレート", [8000, 16000, 22050, 44100, 48000],
                                 index=[8000, 16000, 22050, 44100, 48000].index(settings["audio"]["sample_rate"]),
                                 key=audio_sample_rate_key)
        gain = st.slider("ゲイン", 0.1, 5.0, settings["audio"]["gain"], 0.1, key=audio_gain_key)
        duration = st.slider("録音時間（秒）", 1, 60, settings["audio"]["duration"], key=audio_duration_key)
        
        settings["audio"]["sample_rate"] = sample_rate
        settings["audio"]["gain"] = gain
        settings["audio"]["duration"] = duration
    
    with col2:
        st.write("**詳細設定**")
        
        # 詳細設定のキーを一意にする
        audio_channels_key = f"audio_channels_{uuid.uuid4().hex[:8]}"
        audio_chunk_size_key = f"audio_chunk_size_{uuid.uuid4().hex[:8]}"
        audio_format_key = f"audio_format_{uuid.uuid4().hex[:8]}"
        
        channels = st.selectbox("チャンネル数", [1, 2], index=settings["audio"]["channels"] - 1, key=audio_channels_key)
        chunk_size = st.selectbox("チャンクサイズ", [512, 1024, 2048, 4096],
                                index=[512, 1024, 2048, 4096].index(settings["audio"]["chunk_size"]),
                                key=audio_chunk_size_key)
        format_type = st.selectbox("フォーマット", ["paInt16", "paFloat32"],
                                 index=["paInt16", "paFloat32"].index(settings["audio"]["format"]),
                                 key=audio_format_key)
        
        settings["audio"]["channels"] = channels
        settings["audio"]["chunk_size"] = chunk_size
        settings["audio"]["format"] = format_type

def render_device_settings_tab(settings, settings_manager):
    """デバイス設定タブ"""
    st.write("**🎙️ デバイス設定**")
    
    # デバイスマネージャーを初期化
    device_manager = DeviceManager()
    devices = device_manager.get_available_devices()
    
    if not devices:
        st.error("利用可能な録音デバイスが見つかりません。")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**マイク選択**")
        
        # デバイス一覧を表示
        device_names = [f"{d['name']} (Index: {d['index']})" for d in devices]
        
        # 関数呼び出しごとに一意のキーを生成
        device_selection_key = f"device_selection_{uuid.uuid4().hex[:8]}"
        
        selected_device_name = st.selectbox(
            "録音デバイスを選択",
            device_names,
            index=settings["device"]["selected_device_index"] or 0,
            key=device_selection_key
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
        
        # チェックボックスのキーを一意にする
        auto_select_key = f"auto_select_{uuid.uuid4().hex[:8]}"
        test_device_key = f"test_device_{uuid.uuid4().hex[:8]}"
        
        auto_select = st.checkbox("デフォルトデバイスを自動選択", settings["device"]["auto_select_default"], key=auto_select_key)
        test_device = st.checkbox("デバイス選択時にテスト実行", settings["device"]["test_device_on_select"], key=test_device_key)
        
        settings["device"]["auto_select_default"] = auto_select
        settings["device"]["test_device_on_select"] = test_device
        
        # テストボタンのキーも一意にする
        test_button_key = f"test_device_button_{uuid.uuid4().hex[:8]}"
        
        if st.button("🎤 デバイステスト", key=test_button_key):
            st.info("デバイステスト機能は現在開発中です")

def render_transcription_settings_tab(settings, settings_manager):
    """文字起こし設定タブ"""
    st.write("**📝 文字起こし設定**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Whisper設定**")
        
        # 各ウィジェットのキーを一意にする
        whisper_model_size_key = f"whisper_model_size_{uuid.uuid4().hex[:8]}"
        whisper_language_key = f"whisper_language_{uuid.uuid4().hex[:8]}"
        whisper_temperature_key = f"whisper_temperature_{uuid.uuid4().hex[:8]}"
        
        model_size = st.selectbox("モデルサイズ", ["tiny", "base", "small", "medium", "large"], 
                                index=["tiny", "base", "small", "medium", "large"].index(settings["whisper"]["model_size"]),
                                key=whisper_model_size_key)
        language = st.selectbox("言語", ["ja", "en", "auto"], 
                              index=["ja", "en", "auto"].index(settings["whisper"]["language"]),
                              key=whisper_language_key)
        temperature = st.slider("Temperature", 0.0, 1.0, settings["whisper"]["temperature"], 0.1, key=whisper_temperature_key)
        
        settings["whisper"]["model_size"] = model_size
        settings["whisper"]["language"] = language
        settings["whisper"]["temperature"] = temperature
    
    with col2:
        st.write("**文字起こし動作**")
        
        # チェックボックスのキーを一意にする
        auto_transcribe_key = f"auto_transcribe_{uuid.uuid4().hex[:8]}"
        save_transcriptions_key = f"save_transcriptions_{uuid.uuid4().hex[:8]}"
        
        auto_transcribe = st.checkbox("自動文字起こし", settings["transcription"]["auto_transcribe"], key=auto_transcribe_key)
        save_transcriptions = st.checkbox("文字起こし結果を自動保存", settings["transcription"]["save_transcriptions"], key=save_transcriptions_key)
        
        settings["transcription"]["auto_transcribe"] = auto_transcribe
        settings["transcription"]["save_transcriptions"] = save_transcriptions
        
        # 高度な設定
        with st.expander("🔧 高度なWhisper設定"):
            # 高度な設定のキーも一意にする
            compression_threshold_key = f"compression_threshold_{uuid.uuid4().hex[:8]}"
            logprob_threshold_key = f"logprob_threshold_{uuid.uuid4().hex[:8]}"
            no_speech_threshold_key = f"no_speech_threshold_{uuid.uuid4().hex[:8]}"
            condition_previous_key = f"condition_previous_{uuid.uuid4().hex[:8]}"
            
            compression_threshold = st.slider("圧縮比閾値", 0.0, 5.0, settings["whisper"]["compression_ratio_threshold"], 0.1, key=compression_threshold_key)
            logprob_threshold = st.slider("Logprob閾値", -5.0, 0.0, settings["whisper"]["logprob_threshold"], 0.1, key=logprob_threshold_key)
            no_speech_threshold = st.slider("無音閾値", 0.0, 1.0, settings["whisper"]["no_speech_threshold"], 0.1, key=no_speech_threshold_key)
            condition_previous = st.checkbox("前のテキストを条件とする", settings["whisper"]["condition_on_previous_text"], key=condition_previous_key)
            
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
        
        # チェックボックスのキーを一意にする
        show_advanced_key = f"show_advanced_{uuid.uuid4().hex[:8]}"
        auto_save_key = f"auto_save_{uuid.uuid4().hex[:8]}"
        show_quality_key = f"show_quality_{uuid.uuid4().hex[:8]}"
        show_level_key = f"show_level_{uuid.uuid4().hex[:8]}"
        
        show_advanced = st.checkbox("詳細オプションを表示", settings["ui"]["show_advanced_options"], key=show_advanced_key)
        auto_save = st.checkbox("録音を自動保存", settings["ui"]["auto_save_recordings"], key=auto_save_key)
        show_quality = st.checkbox("音質分析を表示", settings["ui"]["show_quality_analysis"], key=show_quality_key)
        show_level = st.checkbox("レベル監視を表示", settings["ui"]["show_level_monitoring"], key=show_level_key)
        
        settings["ui"]["show_advanced_options"] = show_advanced
        settings["ui"]["auto_save_recordings"] = auto_save
        settings["ui"]["show_quality_analysis"] = show_quality
        settings["ui"]["show_level_monitoring"] = show_level
    
    with col2:
        st.write("**自動録音設定**")
        
        # 自動録音設定のキーも一意にする
        auto_start_key = f"auto_start_{uuid.uuid4().hex[:8]}"
        auto_threshold_key = f"auto_threshold_{uuid.uuid4().hex[:8]}"
        auto_delay_key = f"auto_delay_{uuid.uuid4().hex[:8]}"
        
        auto_start = st.checkbox("自動録音開始", settings["ui"]["auto_start_recording"], key=auto_start_key)
        auto_threshold = st.slider("自動録音閾値", 100, 1000, settings["ui"]["auto_recording_threshold"], 50, key=auto_threshold_key)
        auto_delay = st.slider("自動録音遅延 (秒)", 0.1, 5.0, settings["ui"]["auto_recording_delay"], 0.1, key=auto_delay_key)
        
        settings["ui"]["auto_start_recording"] = auto_start
        settings["ui"]["auto_recording_threshold"] = auto_threshold
        settings["ui"]["auto_recording_delay"] = auto_delay

def render_shortcut_settings_tab(settings, settings_manager):
    """ショートカット設定タブ"""
    st.write("**⚡ ショートカット設定**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**ショートカット有効化**")
        
        # チェックボックスのキーを一意にする
        shortcuts_enabled_key = f"shortcuts_enabled_{uuid.uuid4().hex[:8]}"
        global_hotkeys_key = f"global_hotkeys_{uuid.uuid4().hex[:8]}"
        
        shortcuts_enabled = st.checkbox("ショートカットを有効化", settings["shortcuts"]["enabled"], key=shortcuts_enabled_key)
        global_hotkeys = st.checkbox("グローバルホットキー", settings["shortcuts"]["global_hotkeys"], key=global_hotkeys_key)
        
        settings["shortcuts"]["enabled"] = shortcuts_enabled
        settings["shortcuts"]["global_hotkeys"] = global_hotkeys
    
    with col2:
        st.write("**修飾キー設定**")
        
        # 修飾キーのチェックボックスのキーを一意にする
        ctrl_mod_key = f"ctrl_mod_{uuid.uuid4().hex[:8]}"
        shift_mod_key = f"shift_mod_{uuid.uuid4().hex[:8]}"
        alt_mod_key = f"alt_mod_{uuid.uuid4().hex[:8]}"
        
        ctrl_mod = st.checkbox("Ctrlキー", settings["shortcuts"]["modifiers"]["ctrl"], key=ctrl_mod_key)
        shift_mod = st.checkbox("Shiftキー", settings["shortcuts"]["modifiers"]["shift"], key=shift_mod_key)
        alt_mod = st.checkbox("Altキー", settings["shortcuts"]["modifiers"]["alt"], key=alt_mod_key)
        
        settings["shortcuts"]["modifiers"]["ctrl"] = ctrl_mod
        settings["shortcuts"]["modifiers"]["shift"] = shift_mod
        settings["shortcuts"]["modifiers"]["alt"] = alt_mod
    
    # ショートカットキー設定
    st.write("**🎹 ショートカットキー設定**")
    
    shortcut_keys = settings["shortcuts"]["keys"]
    new_keys = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        # text_inputのキーを一意にする
        start_recording_key = f"start_recording_{uuid.uuid4().hex[:8]}"
        stop_recording_key = f"stop_recording_{uuid.uuid4().hex[:8]}"
        transcribe_key = f"transcribe_{uuid.uuid4().hex[:8]}"
        clear_text_key = f"clear_text_{uuid.uuid4().hex[:8]}"
        
        new_keys["start_recording"] = st.text_input("録音開始", shortcut_keys["start_recording"], key=start_recording_key)
        new_keys["stop_recording"] = st.text_input("録音停止", shortcut_keys["stop_recording"], key=stop_recording_key)
        new_keys["transcribe"] = st.text_input("文字起こし", shortcut_keys["transcribe"], key=transcribe_key)
        new_keys["clear_text"] = st.text_input("テキストクリア", shortcut_keys["clear_text"], key=clear_text_key)
    
    with col2:
        # text_inputのキーを一意にする
        save_recording_key = f"save_recording_{uuid.uuid4().hex[:8]}"
        open_settings_key = f"open_settings_{uuid.uuid4().hex[:8]}"
        open_dictionary_key = f"open_dictionary_{uuid.uuid4().hex[:8]}"
        open_commands_key = f"open_commands_{uuid.uuid4().hex[:8]}"
        
        new_keys["save_recording"] = st.text_input("録音保存", shortcut_keys["save_recording"], key=save_recording_key)
        new_keys["open_settings"] = st.text_input("設定を開く", shortcut_keys["open_settings"], key=open_settings_key)
        new_keys["open_dictionary"] = st.text_input("辞書を開く", shortcut_keys["open_dictionary"], key=open_dictionary_key)
        new_keys["open_commands"] = st.text_input("コマンドを開く", shortcut_keys["open_commands"], key=open_commands_key)
    
    settings["shortcuts"]["keys"] = new_keys

def render_user_dictionary_tab() -> None:
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
            # text_inputのキーを一意にする
            category_key = f"category_{uuid.uuid4().hex[:8]}"
            term_key = f"term_{uuid.uuid4().hex[:8]}"
            
            category = st.text_input("カテゴリ", "カスタム", key=category_key)
            term = st.text_input("用語", key=term_key)
        
        with col2:
            # text_areaとtext_inputのキーを一意にする
            definition_key = f"definition_{uuid.uuid4().hex[:8]}"
            pronunciation_key = f"pronunciation_{uuid.uuid4().hex[:8]}"
            
            definition = st.text_area("定義", key=definition_key)
            pronunciation = st.text_input("発音（オプション）", key=pronunciation_key)
        
        # 追加ボタンのキーを一意にする
        add_dictionary_entry_key = f"add_dictionary_entry_{uuid.uuid4().hex[:8]}"
        
        if st.button("追加", key=add_dictionary_entry_key):
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
                        # 編集ボタンのキーを一意にする
                        edit_key = f"edit_{category_name}_{term}_{uuid.uuid4().hex[:8]}"
                        if st.button(f"編集", key=edit_key):
                            st.info("編集機能は現在開発中です")
                    
                    with col3:
                        # 削除ボタンのキーを一意にする
                        delete_key = f"delete_{category_name}_{term}_{uuid.uuid4().hex[:8]}"
                        if st.button(f"削除", key=delete_key):
                            if dictionary_manager.remove_entry(category_name, term):
                                st.success(f"✅ '{term}' を削除しました")
                                st.rerun()
                            else:
                                st.error("❌ 削除に失敗しました")
            else:
                st.info("このカテゴリにはエントリがありません")

def render_commands_tab() -> None:
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
            # text_inputのキーを一意にする
            name_key = f"name_{uuid.uuid4().hex[:8]}"
            description_key = f"description_{uuid.uuid4().hex[:8]}"
            
            name = st.text_input("コマンド名", key=name_key)
            description = st.text_input("説明", key=description_key)
        
        with col2:
            # 出力形式のキーを一意にする
            command_output_format_key = f"command_output_format_{uuid.uuid4().hex[:8]}"
            enabled_key = f"enabled_{uuid.uuid4().hex[:8]}"
            
            output_format = st.selectbox("出力形式", ["text", "bullet_points", "summary", "text_file"], key=command_output_format_key)
            enabled = st.checkbox("有効化", True, key=enabled_key)
        
        # text_areaのキーを一意にする
        llm_prompt_key = f"llm_prompt_{uuid.uuid4().hex[:8]}"
        llm_prompt = st.text_area("LLMプロンプト", placeholder="以下の文字起こし結果を処理してください：\n\n{text}", key=llm_prompt_key)
        
        # 追加ボタンのキーを一意にする
        add_command_key = f"add_command_{uuid.uuid4().hex[:8]}"
        
        if st.button("追加", key=add_command_key):
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
                st.write(f"**プロンプト**: {cmd_data['llm_prompt'][:100]}...")
            
            with col2:
                # 編集ボタンのキーを一意にする
                edit_key = f"edit_cmd_{cmd_name}_{uuid.uuid4().hex[:8]}"
                if st.button("編集", key=edit_key):
                    st.info("編集機能は現在開発中です")
            
            with col3:
                # 削除ボタンのキーを一意にする
                delete_key = f"delete_cmd_{cmd_name}_{uuid.uuid4().hex[:8]}"
                if st.button("削除", key=delete_key):
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
            # 削除ボタンのキーを一意にする
            delete_key = f"delete_{file}_{uuid.uuid4().hex[:8]}"
            if st.button(f"🗑️ 削除", key=delete_key):
                try:
                    os.remove(file_path)
                    st.success(f"✅ {file} を削除しました")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 削除エラー: {e}")

def render_task_management_tab():
    """タスク管理タブのレンダリング"""
    st.subheader("📋 タスク管理")
    
    # タスクマネージャーの初期化
    task_manager = TaskManager()
    google_calendar = GoogleCalendarManager()
    
    # Googleカレンダー認証状態の確認
    google_auth_status = "❌ 未認証"
    if google_calendar.authenticate():
        google_auth_status = "✅ 認証済み"
    
    st.info(f"Googleカレンダー連携: {google_auth_status}")
    
    # タブの作成
    task_tab1, task_tab2, task_tab3, task_tab4 = st.tabs(["📝 タスク一覧", "➕ タスク追加", "📅 カレンダー連携", "⚙️ タスク設定"])
    
    with task_tab1:
        st.write("### 📝 タスク一覧")
        
        # フィルターのキーを一意にする
        task_status_filter_key = f"task_status_filter_{uuid.uuid4().hex[:8]}"
        task_priority_filter_key = f"task_priority_filter_{uuid.uuid4().hex[:8]}"
        task_category_filter_key = f"task_category_filter_{uuid.uuid4().hex[:8]}"
        
        status_filter = st.selectbox(
            "ステータス",
            ["all", "pending", "in_progress", "completed"],
            format_func=lambda x: {"all": "すべて", "pending": "未完了", "in_progress": "進行中", "completed": "完了"}[x],
            key=f"task_status_filter_{task_status_filter_key}"
        )
        
        priority_filter = st.selectbox(
            "優先度",
            ["all", "low", "medium", "high"],
            format_func=lambda x: {"all": "すべて", "low": "低", "medium": "中", "high": "高"}[x],
            key=f"task_priority_filter_{task_priority_filter_key}"
        )
        
        category_filter = st.selectbox(
            "カテゴリ",
            ["all", "general", "work", "personal", "音声文字起こし"],
            format_func=lambda x: {"all": "すべて", "general": "一般", "work": "仕事", "personal": "個人", "音声文字起こし": "音声文字起こし"}[x],
            key=f"task_category_filter_{task_category_filter_key}"
        )
        
        # タスクの読み込みとフィルター
        tasks = task_manager.load_tasks()
        filtered_tasks = {}
        
        for task_id, task in tasks["tasks"].items():
            # ステータスフィルター
            if status_filter != "all" and task["status"] != status_filter:
                continue
            
            # 優先度フィルター
            if priority_filter != "all" and task["priority"] != priority_filter:
                continue
            
            # カテゴリフィルター
            if category_filter != "all" and task["category"] != category_filter:
                continue
            
            filtered_tasks[task_id] = task
        
        # タスクの表示
        if filtered_tasks:
            for task_id, task in filtered_tasks.items():
                with st.expander(f"📋 {task['title']}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**説明**: {task['description']}")
                        st.write(f"**優先度**: {task['priority']}")
                        st.write(f"**カテゴリ**: {task['category']}")
                        if task['due_date']:
                            st.write(f"**期限**: {task['due_date']}")
                        st.write(f"**作成日**: {task['created_at'][:10]}")
                        
                        # Googleカレンダー連携状態
                        if task.get('google_event_id'):
                            st.success("✅ Googleカレンダーに同期済み")
                        else:
                            st.info("📅 Googleカレンダー未同期")
                    
                    with col2:
                        # ステータス変更のキーを一意にする
                        status_key = f"status_{task_id}_{uuid.uuid4().hex[:8]}"
                        new_status = st.selectbox(
                            "ステータス",
                            ["pending", "in_progress", "completed"],
                            index=["pending", "in_progress", "completed"].index(task["status"]),
                            key=status_key
                        )
                        
                        if new_status != task["status"]:
                            task_manager.update_task(task_id, status=new_status)
                            st.success("ステータスを更新しました")
                        
                        # Googleカレンダー同期ボタン
                        if not task.get('google_event_id') and google_calendar.authenticate():
                            sync_key = f"sync_{task_id}_{uuid.uuid4().hex[:8]}"
                            if st.button("📅 カレンダー同期", key=sync_key):
                                # タスクをGoogleカレンダーイベントとして追加
                                event_data = {
                                    'title': task['title'],
                                    'description': task['description'],
                                    'start_date': task['due_date'] or datetime.now().isoformat(),
                                    'end_date': task['due_date'] or (datetime.now() + timedelta(hours=1)).isoformat(),
                                    'all_day': False,
                                    'category': task['category']
                                }
                                
                                google_event = google_calendar.create_event(event_data)
                                if google_event:
                                    task_manager.update_task(task_id, google_event_id=google_event['id'])
                                    st.success("Googleカレンダーに同期しました")
                                    st.rerun()
                        
                        # 削除ボタンのキーを一意にする
                        delete_key = f"delete_{task_id}_{uuid.uuid4().hex[:8]}"
                        if st.button("🗑️ 削除", key=delete_key):
                            if task_manager.delete_task(task_id):
                                st.success("タスクを削除しました")
                                st.rerun()
        else:
            st.info("タスクがありません")
    
    with task_tab2:
        st.write("### ➕ タスク追加")
        
        # フォーム内のキーを一意にする
        add_task_priority_key = f"add_task_priority_{uuid.uuid4().hex[:8]}"
        add_task_category_key = f"add_task_category_{uuid.uuid4().hex[:8]}"
        add_task_due_date_key = f"add_task_due_date_{uuid.uuid4().hex[:8]}"
        add_task_sync_key = f"add_task_sync_{uuid.uuid4().hex[:8]}"
        
        with st.form("add_task_form"):
            # text_inputとtext_areaのキーを一意にする
            title_key = f"title_{uuid.uuid4().hex[:8]}"
            description_key = f"description_{uuid.uuid4().hex[:8]}"
            
            title = st.text_input("タイトル *", key=title_key)
            description = st.text_area("説明", key=description_key)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                priority = st.selectbox("優先度", ["low", "medium", "high"], key=f"add_task_priority_{add_task_priority_key}")
            with col2:
                category = st.selectbox("カテゴリ", ["general", "work", "personal", "音声文字起こし"], key=f"add_task_category_{add_task_category_key}")
            with col3:
                due_date = st.date_input("期限", key=f"add_task_due_date_{add_task_due_date_key}")
            
            # Googleカレンダー同期オプション
            sync_to_calendar = st.checkbox("Googleカレンダーに同期", value=True, key=f"add_task_sync_{add_task_sync_key}")
            
            submitted = st.form_submit_button("タスクを追加")
            
            if submitted and title:
                # タスクを追加
                task_added = task_manager.add_task(
                    title=title,
                    description=description,
                    priority=priority,
                    due_date=due_date.isoformat() if due_date else None,
                    category=category
                )
                
                if task_added:
                    st.success("✅ タスクを追加しました")
                    
                    # Googleカレンダーに同期
                    if sync_to_calendar and google_calendar.authenticate():
                        # 最新のタスクを取得
                        tasks = task_manager.load_tasks()
                        latest_task_id = None
                        latest_task = None
                        
                        for task_id, task in tasks["tasks"].items():
                            if task["title"] == title and task["description"] == description:
                                latest_task_id = task_id
                                latest_task = task
                                break
                        
                        if latest_task:
                            # Googleカレンダーイベントとして追加
                            event_data = {
                                'title': title,
                                'description': description,
                                'start_date': due_date.isoformat() if due_date else datetime.now().isoformat(),
                                'end_date': due_date.isoformat() if due_date else (datetime.now() + timedelta(hours=1)).isoformat(),
                                'all_day': False,
                                'category': category
                            }
                            
                            google_event = google_calendar.create_event(event_data)
                            if google_event:
                                task_manager.update_task(latest_task_id, google_event_id=google_event['id'])
                                st.success("✅ Googleカレンダーにも同期しました")
                            else:
                                st.warning("⚠️ Googleカレンダーへの同期に失敗しました")
                        else:
                            st.warning("⚠️ タスクの取得に失敗しました")
                    elif sync_to_calendar:
                        st.warning("⚠️ Googleカレンダーが認証されていません")
                    
                    # タスク一覧を更新
                    st.rerun()
                else:
                    st.error("❌ タスクの追加に失敗しました")
    
    with task_tab3:
        st.write("### 📅 カレンダー連携")
        
        if not google_calendar.authenticate():
            st.warning("⚠️ Googleカレンダーに接続されていません")
            st.info("📝 設定タブでGoogleカレンダーの認証を行ってください")
        else:
            st.success("✅ Googleカレンダーに接続されています")
            
            # 同期オプション
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📅 未同期タスクをカレンダーに同期"):
                    tasks = task_manager.load_tasks()
                    synced_count = 0
                    
                    for task_id, task in tasks["tasks"].items():
                        if not task.get('google_event_id') and task['status'] != 'completed':
                            event_data = {
                                'title': task['title'],
                                'description': task['description'],
                                'start_date': task['due_date'] or datetime.now().isoformat(),
                                'end_date': task['due_date'] or (datetime.now() + timedelta(hours=1)).isoformat(),
                                'all_day': False,
                                'category': task['category']
                            }
                            
                            google_event = google_calendar.create_event(event_data)
                            if google_event:
                                task_manager.update_task(task_id, google_event_id=google_event['id'])
                                synced_count += 1
                    
                    if synced_count > 0:
                        st.success(f"✅ {synced_count}件のタスクをGoogleカレンダーに同期しました")
                    else:
                        st.info("📝 同期するタスクがありません")
            
            with col2:
                if st.button("🔄 Googleカレンダーからタスクを取得"):
                    google_events = google_calendar.get_events(max_results=20)
                    imported_count = 0
                    
                    for event in google_events:
                        # 既存のタスクと重複しないかチェック
                        tasks = task_manager.load_tasks()
                        event_exists = False
                        
                        for task in tasks["tasks"].values():
                            if task.get('google_event_id') == event['id']:
                                event_exists = True
                                break
                        
                        if not event_exists:
                            # 新しいタスクとして追加
                            task_added = task_manager.add_task(
                                title=event.get('summary', '無題'),
                                description=event.get('description', ''),
                                priority='medium',
                                due_date=event['start'].get('dateTime', event['start'].get('date')),
                                category='Google同期',
                                google_event_id=event['id']
                            )
                            if task_added:
                                imported_count += 1
                    
                    if imported_count > 0:
                        st.success(f"✅ {imported_count}件のイベントをタスクとしてインポートしました")
                    else:
                        st.info("📝 インポートするイベントがありません")
    
    with task_tab4:
        st.write("### ⚙️ タスク設定")
        
        # 統計情報
        tasks = task_manager.load_tasks()
        total_tasks = len(tasks["tasks"])
        pending_tasks = len([t for t in tasks["tasks"].values() if t["status"] == "pending"])
        completed_tasks = len([t for t in tasks["tasks"].values() if t["status"] == "completed"])
        synced_tasks = len([t for t in tasks["tasks"].values() if t.get('google_event_id')])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("総タスク数", total_tasks)
        with col2:
            st.metric("未完了タスク", pending_tasks)
        with col3:
            st.metric("完了タスク", completed_tasks)
        with col4:
            st.metric("カレンダー同期", synced_tasks)
        
        # デバッグ情報
        with st.expander("🔍 デバッグ情報"):
            st.write("### タスクファイル情報")
            st.write(f"**ファイルパス**: {task_manager.tasks_file}")
            st.write(f"**ファイル存在**: {'✅ 存在' if os.path.exists(task_manager.tasks_file) else '❌ 存在しない'}")
            
            if os.path.exists(task_manager.tasks_file):
                file_size = os.path.getsize(task_manager.tasks_file)
                st.write(f"**ファイルサイズ**: {file_size} bytes")
                
                # ファイル内容の確認
                try:
                    with open(task_manager.tasks_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    st.write(f"**ファイル内容**:")
                    st.code(content, language='json')
                except Exception as e:
                    st.error(f"ファイル読み込みエラー: {e}")
            
            st.write("### 現在のタスク一覧")
            if tasks["tasks"]:
                for task_id, task in tasks["tasks"].items():
                    st.write(f"- **{task['title']}** (ID: {task_id})")
                    st.write(f"  - ステータス: {task['status']}")
                    st.write(f"  - カテゴリ: {task['category']}")
                    st.write(f"  - 作成日: {task['created_at']}")
                    if task.get('google_event_id'):
                        st.write(f"  - Google Event ID: {task['google_event_id']}")
            else:
                st.info("タスクがありません")
        
        # 一括操作
        st.write("### 一括操作")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ 完了タスクを削除"):
                for task_id, task in tasks["tasks"].items():
                    if task["status"] == "completed":
                        task_manager.delete_task(task_id)
                st.success("完了タスクを削除しました")
                st.rerun()
        
        with col2:
            if st.button("📅 未同期タスクを同期"):
                if google_calendar.authenticate():
                    synced_count = 0
                    for task_id, task in tasks["tasks"].items():
                        if not task.get('google_event_id') and task['status'] != 'completed':
                            event_data = {
                                'title': task['title'],
                                'description': task['description'],
                                'start_date': task['due_date'] or datetime.now().isoformat(),
                                'end_date': task['due_date'] or (datetime.now() + timedelta(hours=1)).isoformat(),
                                'all_day': False,
                                'category': task['category']
                            }
                            
                            google_event = google_calendar.create_event(event_data)
                            if google_event:
                                task_manager.update_task(task_id, google_event_id=google_event['id'])
                                synced_count += 1
                    
                    if synced_count > 0:
                        st.success(f"{synced_count}件のタスクを同期しました")
                    else:
                        st.info("同期するタスクがありません")
                else:
                    st.warning("Googleカレンダーが認証されていません")
                st.rerun()
        
        with col3:
            if st.button("📊 統計をリセット"):
                st.info("統計情報をリセットしました")

def render_calendar_management_tab():
    """カレンダー管理タブのレンダリング"""
    st.subheader("📅 カレンダー管理")
    
    # カレンダーマネージャーの初期化
    calendar_manager = CalendarManager()
    google_calendar = GoogleCalendarManager()
    
    # Googleカレンダー認証状態の確認
    google_auth_status = "❌ 未認証"
    if google_calendar.authenticate():
        google_auth_status = "✅ 認証済み"
    
    st.info(f"Googleカレンダー連携: {google_auth_status}")
    
    # タブの作成
    cal_tab1, cal_tab2, cal_tab3, cal_tab4 = st.tabs(["📅 カレンダー", "➕ イベント追加", "📊 イベント一覧", "🔄 同期管理"])
    
    with cal_tab1:
        st.write("### 📅 カレンダー")
        
        # 日付選択
        selected_date = st.date_input("日付を選択", value=date.today())
        
        # 選択された日付のイベントを取得
        events = calendar_manager.get_events_by_date(selected_date)
        
        if events:
            st.write(f"**{selected_date} のイベント**")
            for event_id, event in events.items():
                with st.expander(f"📅 {event['title']}"):
                    st.write(f"**説明**: {event['description']}")
                    st.write(f"**カテゴリ**: {event['category']}")
                    if event['start_date']:
                        st.write(f"**開始**: {event['start_date']}")
                    if event['end_date']:
                        st.write(f"**終了**: {event['end_date']}")
                    
                    # Googleカレンダー連携状態
                    if event.get('google_event_id'):
                        st.success("✅ Googleカレンダーに同期済み")
                    else:
                        st.info("📅 Googleカレンダー未同期")
                    
                    # 削除ボタンのキーを一意にする
                    delete_key = f"delete_event_{event_id}_{uuid.uuid4().hex[:8]}"
                    if st.button("🗑️ 削除", key=delete_key):
                        if calendar_manager.delete_event(event_id):
                            st.success("イベントを削除しました")
                            st.rerun()
        else:
            st.info(f"{selected_date} のイベントはありません")
    
    with cal_tab2:
        st.write("### ➕ イベント追加")
        
        # フォーム内のキーを一意にする
        add_event_category_key = f"add_event_category_{uuid.uuid4().hex[:8]}"
        add_event_all_day_key = f"add_event_all_day_{uuid.uuid4().hex[:8]}"
        add_event_sync_key = f"add_event_sync_{uuid.uuid4().hex[:8]}"
        
        with st.form("add_event_form"):
            # text_inputとtext_areaのキーを一意にする
            title_key = f"title_{uuid.uuid4().hex[:8]}"
            description_key = f"description_{uuid.uuid4().hex[:8]}"
            
            title = st.text_input("タイトル *", key=title_key)
            description = st.text_area("説明", key=description_key)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                start_date = st.date_input("開始日")
            with col2:
                end_date = st.date_input("終了日")
            with col3:
                category = st.selectbox("カテゴリ", ["general", "work", "personal", "音声文字起こし"], key=f"add_event_category_{add_event_category_key}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                all_day = st.checkbox("終日", key=f"add_event_all_day_{add_event_all_day_key}")
            with col2:
                # Googleカレンダー同期オプション
                sync_to_calendar = st.checkbox("Googleカレンダーに同期", value=True, key=f"add_event_sync_{add_event_sync_key}")
            with col3:
                pass
            
            submitted = st.form_submit_button("イベントを追加")
            
            if submitted and title:
                # イベントを追加
                event_added = calendar_manager.add_event(
                    title=title,
                    description=description,
                    start_date=start_date.isoformat() if start_date else None,
                    end_date=end_date.isoformat() if end_date else None,
                    all_day=all_day,
                    category=category
                )
                
                if event_added:
                    st.success("✅ イベントを追加しました")
                    
                    # Googleカレンダーに同期
                    if sync_to_calendar and google_calendar.authenticate():
                        # 最新のイベントを取得
                        all_events = calendar_manager.load_events()
                        latest_event_id = None
                        latest_event = None
                        
                        for event_id, event in all_events["events"].items():
                            if event["title"] == title and event["description"] == description:
                                latest_event_id = event_id
                                latest_event = event
                                break
                        
                        if latest_event:
                            # Googleカレンダーイベントとして追加
                            event_data = {
                                'title': title,
                                'description': description,
                                'start_date': start_date.isoformat() if start_date else datetime.now().isoformat(),
                                'end_date': end_date.isoformat() if end_date else (datetime.now() + timedelta(hours=1)).isoformat(),
                                'all_day': all_day,
                                'category': category
                            }
                            
                            google_event = google_calendar.create_event(event_data)
                            if google_event:
                                calendar_manager.update_event(latest_event_id, google_event_id=google_event['id'])
                                st.success("✅ Googleカレンダーにも同期しました")
                            else:
                                st.warning("⚠️ Googleカレンダーへの同期に失敗しました")
                        else:
                            st.warning("⚠️ イベントの取得に失敗しました")
                    elif sync_to_calendar:
                        st.warning("⚠️ Googleカレンダーが認証されていません")
                    
                    # イベント一覧を更新
                    st.rerun()
                else:
                    st.error("❌ イベントの追加に失敗しました")
    
    with cal_tab3:
        st.write("### 📊 イベント一覧")
        
        # カテゴリフィルターのキーを一意にする
        calendar_category_filter_key = f"calendar_category_filter_{uuid.uuid4().hex[:8]}"
        
        category_filter = st.selectbox(
            "カテゴリ",
            ["all", "general", "work", "personal", "音声文字起こし"],
            format_func=lambda x: {"all": "すべて", "general": "一般", "work": "仕事", "personal": "個人", "音声文字起こし": "音声文字起こし"}[x],
            key=f"calendar_category_filter_{calendar_category_filter_key}"
        )
        
        # イベントの読み込みとフィルター
        all_events = calendar_manager.load_events()
        filtered_events = {}
        
        for event_id, event in all_events["events"].items():
            if category_filter != "all" and event["category"] != category_filter:
                continue
            filtered_events[event_id] = event
        
        # イベントの表示
        if filtered_events:
            for event_id, event in filtered_events.items():
                with st.expander(f"📅 {event['title']}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**説明**: {event['description']}")
                        st.write(f"**カテゴリ**: {event['category']}")
                        if event['start_date']:
                            st.write(f"**開始**: {event['start_date']}")
                        if event['end_date']:
                            st.write(f"**終了**: {event['end_date']}")
                        
                        # Googleカレンダー連携状態
                        if event.get('google_event_id'):
                            st.success("✅ Googleカレンダーに同期済み")
                        else:
                            st.info("📅 Googleカレンダー未同期")
                    
                    with col2:
                        # Googleカレンダー同期ボタン
                        if not event.get('google_event_id') and google_calendar.authenticate():
                            sync_key = f"sync_event_{event_id}_{uuid.uuid4().hex[:8]}"
                            if st.button("📅 カレンダー同期", key=sync_key):
                                # イベントをGoogleカレンダーイベントとして追加
                                event_data = {
                                    'title': event['title'],
                                    'description': event['description'],
                                    'start_date': event['start_date'] or datetime.now().isoformat(),
                                    'end_date': event['end_date'] or (datetime.now() + timedelta(hours=1)).isoformat(),
                                    'all_day': event.get('all_day', False),
                                    'category': event['category']
                                }
                                
                                google_event = google_calendar.create_event(event_data)
                                if google_event:
                                    calendar_manager.update_event(event_id, google_event_id=google_event['id'])
                                    st.success("Googleカレンダーに同期しました")
                                    st.rerun()
                        
                        # 削除ボタンのキーを一意にする
                        delete_key = f"delete_event_list_{event_id}_{uuid.uuid4().hex[:8]}"
                        if st.button("🗑️ 削除", key=delete_key):
                            if calendar_manager.delete_event(event_id):
                                st.success("イベントを削除しました")
                                st.rerun()
        else:
            st.info("イベントがありません")
    
    with cal_tab4:
        st.write("### 🔄 同期管理")
        
        if not google_calendar.authenticate():
            st.warning("⚠️ Googleカレンダーに接続されていません")
            st.info("📝 設定タブでGoogleカレンダーの認証を行ってください")
        else:
            st.success("✅ Googleカレンダーに接続されています")
            
            # 同期オプション
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📅 未同期イベントをカレンダーに同期"):
                    all_events = calendar_manager.load_events()
                    synced_count = 0
                    
                    for event_id, event in all_events["events"].items():
                        if not event.get('google_event_id'):
                            event_data = {
                                'title': event['title'],
                                'description': event['description'],
                                'start_date': event['start_date'] or datetime.now().isoformat(),
                                'end_date': event['end_date'] or (datetime.now() + timedelta(hours=1)).isoformat(),
                                'all_day': event.get('all_day', False),
                                'category': event['category']
                            }
                            
                            google_event = google_calendar.create_event(event_data)
                            if google_event:
                                calendar_manager.update_event(event_id, google_event_id=google_event['id'])
                                synced_count += 1
                    
                    if synced_count > 0:
                        st.success(f"✅ {synced_count}件のイベントをGoogleカレンダーに同期しました")
                    else:
                        st.info("📝 同期するイベントがありません")
            
            with col2:
                if st.button("🔄 Googleカレンダーからイベントを取得"):
                    google_events = google_calendar.get_events(max_results=20)
                    imported_count = 0
                    
                    for event in google_events:
                        # 既存のイベントと重複しないかチェック
                        all_events = calendar_manager.load_events()
                        event_exists = False
                        
                        for local_event in all_events["events"].values():
                            if local_event.get('google_event_id') == event['id']:
                                event_exists = True
                                break
                        
                        if not event_exists:
                            # 新しいイベントとして追加
                            event_added = calendar_manager.add_event(
                                title=event.get('summary', '無題'),
                                description=event.get('description', ''),
                                start_date=event['start'].get('dateTime', event['start'].get('date')),
                                end_date=event['end'].get('dateTime', event['end'].get('date')),
                                all_day='date' in event['start'],
                                category='Google同期',
                                google_event_id=event['id']
                            )
                            if event_added:
                                imported_count += 1
                    
                    if imported_count > 0:
                        st.success(f"✅ {imported_count}件のイベントをインポートしました")
                    else:
                        st.info("📝 インポートするイベントがありません")
            
            # 統計情報
            st.write("### 📊 同期統計")
            all_events = calendar_manager.load_events()
            total_events = len(all_events["events"])
            synced_events = len([e for e in all_events["events"].values() if e.get('google_event_id')])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("総イベント数", total_events)
            with col2:
                st.metric("カレンダー同期", synced_events)


class SettingsUI:
    """設定UI統合クラス"""
    
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
    
    def display_settings_page(self):
        """設定ページ表示"""
        render_enhanced_settings_tab(self.settings_manager)
    
    def display_user_dictionary_page(self):
        """ユーザー辞書ページ表示"""
        render_user_dictionary_tab()
    
    def display_command_management_page(self):
        """コマンド管理ページ表示"""
        render_commands_tab()
    
    def display_device_management_page(self):
        """デバイス管理ページ表示"""
        settings = self.settings_manager.load_settings()
        render_device_settings_tab(settings, self.settings_manager)
    
    def display_task_management_page(self):
        """タスク管理ページ表示"""
        render_task_management_tab()
    
    def display_calendar_page(self):
        """カレンダーページ表示"""
        render_calendar_management_tab()
    
    def display_history_page(self):
        """履歴ページ表示"""
        st.write("文字起こし履歴機能は開発中です。")
        
        # 履歴ファイル一覧
        transcriptions_dir = "transcriptions"
        if os.path.exists(transcriptions_dir):
            files = [f for f in os.listdir(transcriptions_dir) if f.endswith('.txt')]
            if files:
                st.subheader("📝 文字起こし履歴")
                for file in sorted(files, reverse=True):
                    with st.expander(f"📄 {file}"):
                        filepath = os.path.join(transcriptions_dir, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                            # text_areaのキーを一意にする
                            text_area_key = f"history_{file}_{uuid.uuid4().hex[:8]}"
                            st.text_area("内容", content, height=200, key=text_area_key)
                        except Exception as e:
                            st.error(f"ファイル読み込みエラー: {e}")
            else:
                st.info("まだ文字起こし履歴がありません。")
        else:
            st.info("履歴フォルダが見つかりません。")
    
    def display_statistics_page(self):
        """統計ページ表示"""
        st.write("統計機能は開発中です。")
        
        # 基本的な統計情報
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📝 文字起こし回数", self._get_transcription_count())
        
        with col2:
            st.metric("🎵 録音ファイル数", self._get_recording_count())
        
        with col3:
            st.metric("📋 タスク数", self._get_task_count())
    
    def _get_transcription_count(self) -> int:
        """文字起こし回数を取得"""
        transcriptions_dir = "transcriptions"
        if os.path.exists(transcriptions_dir):
            return len([f for f in os.listdir(transcriptions_dir) if f.endswith('.txt')])
        return 0
    
    def _get_recording_count(self) -> int:
        """録音ファイル数を取得"""
        recordings_dir = "recordings"
        if os.path.exists(recordings_dir):
            return len([f for f in os.listdir(recordings_dir) if f.endswith(('.wav', '.mp3', '.m4a'))])
        return 0
    
    def _get_task_count(self) -> int:
        """タスク数を取得"""
        try:
            tasks = self.task_manager.get_all_tasks()
            return len(tasks)
        except:
            return 0 