"""
app_audiorec.py用の拡張設定UIコンポーネント
設定、ユーザー辞書、コマンド、デバイス管理などのUIを提供
"""

# 標準ライブラリ
import json
import os
import sys
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional

# サードパーティライブラリ
import streamlit as st

# ローカルインポート
try:
    from src.utils_audiorec import (
        EnhancedSettingsManager, CommandManager, UserDictionaryManager,
        TaskManager, CalendarManager, TaskAnalyzer, EventAnalyzer,
        GoogleCalendarManager, DeviceManager, get_google_auth_manager
    )
    UTILS_AUDIOREC_AVAILABLE = True
except ImportError as e:
    # Streamlit Cloud環境でのフォールバック
    UTILS_AUDIOREC_AVAILABLE = False
    st.warning(f"utils_audiorec のインポートに失敗しました: {e}")
    
    # ダミークラスを定義
    class EnhancedSettingsManager:
        def __init__(self):
            pass
        def load_settings(self):
            return {}
        def save_settings(self, settings):
            pass
    
    class CommandManager:
        def __init__(self):
            pass
    
    class UserDictionaryManager:
        def __init__(self):
            pass
    
    class TaskManager:
        def __init__(self):
            pass
        
        def get_all_tasks(self):
            return []
    
    class CalendarManager:
        def __init__(self):
            pass
    
    class TaskAnalyzer:
        def __init__(self):
            pass
    
    class EventAnalyzer:
        def __init__(self):
            pass
    
    class GoogleCalendarManager:
        def __init__(self):
            pass
    
    class DeviceManager:
        def __init__(self):
            pass
    
    def get_google_auth_manager():
        return None

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
    
    # タスク追加コマンドの説明
    with st.expander("📋 タスク追加コマンドについて", expanded=True):
        st.info("""
        **タスク追加コマンド**は、音声録音の文字起こし結果から自動的にタスクを検出・作成する機能です。
        
        **使用方法:**
        - 音声で「タスク 明日の会議の準備」と言うと、自動的にタスクとして認識されます
        - キーワード: `タスク`, `task`, `やること`, `todo`, `TODO`, `ToDo`
        
        **自動検出される情報:**
        - **タイトル**: キーワードの後の部分が自動的にタイトルになります
        - **優先度**: `緊急`, `高`, `中`, `低` のキーワードで自動設定
        - **カテゴリ**: `仕事`, `プライベート`, `勉強`, `健康` のキーワードで自動設定
        - **説明**: タイトル以外の部分が説明として保存されます
        
        **例:**
        - "タスク 明日の会議の準備 高優先度" → タイトル: "明日の会議の準備", 優先度: 高
        - "やること 買い物 プライベート" → タイトル: "買い物", カテゴリ: プライベート
        """)
    
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
    """タスク管理タブ"""
    st.subheader("📋 タスク管理")
    
    # 統合認証マネージャーを取得
    auth_manager = get_google_auth_manager()
    
    # タブを作成
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 タスク一覧", 
        "➕ タスク追加", 
        "📅 カレンダー連携", 
        "⚙️ タスク設定"
    ])
    
    with tab1:
        render_task_list_tab()
    
    with tab2:
        render_task_add_tab(auth_manager)
    
    with tab3:
        render_task_calendar_sync_tab(auth_manager)
    
    with tab4:
        render_task_settings_tab()


def render_task_list_tab():
    """タスク一覧タブ"""
    st.write("**📝 タスク一覧**")
    
    # TaskManagerをインスタンス化
    task_manager = TaskManager()
    
    # タスクを読み込み
    tasks = task_manager.load_tasks()
    
    if not tasks["tasks"]:
        st.info("📝 タスクがありません。新しいタスクを追加してください。")
        return
    
    # フィルター
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("ステータス", ["全て", "pending", "completed"], key="task_status_filter")
    with col2:
        # prioritiesキーの存在チェック
        priorities = tasks.get("priorities", ["低", "中", "高", "緊急"])
        priority_filter = st.selectbox("優先度", ["全て"] + priorities, key="task_priority_filter")
    with col3:
        # categoriesキーの存在チェック
        categories = tasks.get("categories", ["仕事", "プライベート", "勉強", "健康", "その他"])
        category_filter = st.selectbox("カテゴリ", ["全て"] + categories, key="task_category_filter")
    
    # タスクを表示
    for task_id, task in tasks["tasks"].items():
        # フィルター適用
        if status_filter != "全て" and task["status"] != status_filter:
            continue
        if priority_filter != "全て" and task.get("priority", "中") != priority_filter:
            continue
        if category_filter != "全て" and task.get("category", "未分類") != category_filter:
            continue
        
        with st.expander(f"📋 {task.get('title', 'タイトルなし')} ({task.get('priority', '中')})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**説明**: {task.get('description', '説明なし')}")
                st.write(f"**カテゴリ**: {task.get('category', '未分類')}")
                st.write(f"**ステータス**: {task['status']}")
                if task.get('due_date'):
                    st.write(f"**期限**: {task['due_date']}")
                if task.get('google_event_id'):
                    st.write("✅ Googleカレンダーに同期済み")
            
            with col2:
                # ステータス変更
                new_status = st.selectbox(
                    "ステータス変更", 
                    ["pending", "completed"], 
                    index=0 if task["status"] == "pending" else 1,
                    key=f"status_{task_id}"
                )
                
                if new_status != task["status"]:
                    if st.button("更新", key=f"update_status_{task_id}"):
                        task_manager.update_task(task_id, status=new_status)
                        st.success("ステータスを更新しました")
                        st.rerun()
                
                # 削除ボタン
                if st.button("🗑️ 削除", key=f"delete_task_{task_id}"):
                    if task_manager.delete_task(task_id):
                        st.success("タスクを削除しました")
                        st.rerun()
                    else:
                        st.error("タスクの削除に失敗しました")


def render_task_add_tab(auth_manager):
    """タスク追加タブ"""
    st.write("**➕ タスク追加**")
    
    # TaskManagerをインスタンス化
    task_manager = TaskManager()
    
    # 設定マネージャーをインスタンス化
    settings_manager = EnhancedSettingsManager()
    settings = settings_manager.load_settings()
    
    # タスク管理設定の初期化
    if "task_management" not in settings:
        settings["task_management"] = {
            "auto_sync_to_calendar": False,
            "default_sync_to_calendar": True,
            "sync_completed_tasks": False,
            "calendar_timezone": "Asia/Tokyo",
            "default_event_duration": 60
        }
    
    with st.form("add_task_form"):
        title = st.text_input("タスク名", key="task_title")
        description = st.text_area("説明", key="task_description")
        
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("優先度", ["低", "中", "高", "緊急"], key="task_priority")
            category = st.selectbox("カテゴリ", ["仕事", "プライベート", "勉強", "健康", "その他"], key="task_category")
        
        with col2:
            due_date = st.date_input("期限", key="task_due_date")
            # 設定に基づいてデフォルト値を設定
            default_sync = settings["task_management"]["default_sync_to_calendar"]
            sync_to_calendar = st.checkbox("Googleカレンダーに同期", value=default_sync, key="task_sync_calendar")
        
        submitted = st.form_submit_button("タスクを追加")
        
        if submitted and title:
            # 認証状態を確認
            if sync_to_calendar and (not auth_manager or not auth_manager.is_authenticated()):
                st.error("Googleカレンダーに同期するには認証が必要です")
                st.info("カレンダー連携タブでGoogleカレンダー認証を実行してください")
                return
            
            # タスクを追加
            task_added = task_manager.add_task(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date.isoformat() if due_date else None,
                category=category,
                auto_sync=settings["task_management"]["auto_sync_to_calendar"]
            )
            
            if task_added:
                st.success("✅ タスクを追加しました")
                
                # 自動同期設定が有効な場合、または手動で同期が選択された場合
                auto_sync_enabled = settings["task_management"]["auto_sync_to_calendar"]
                should_sync = auto_sync_enabled or sync_to_calendar
                
                if should_sync and auth_manager and auth_manager.authenticate():
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
                        # 設定からタイムゾーンとデフォルト時間を取得
                        timezone = settings["task_management"]["calendar_timezone"]
                        default_duration = settings["task_management"]["default_event_duration"]
                        
                        # 開始時間と終了時間を設定
                        start_time = due_date if due_date else datetime.now()
                        if isinstance(start_time, date):
                            start_time = datetime.combine(start_time, datetime.min.time())
                        
                        end_time = start_time + timedelta(minutes=default_duration)
                        
                        service = auth_manager.get_service()
                        if service:
                            google_event = {
                                'summary': title,
                                'description': description,
                                'start': {
                                    'dateTime': start_time.isoformat(),
                                    'timeZone': timezone,
                                },
                                'end': {
                                    'dateTime': end_time.isoformat(),
                                    'timeZone': timezone,
                                }
                            }
                            
                            created_event = service.events().insert(
                                calendarId='primary', body=google_event
                            ).execute()
                            
                            task_manager.update_task(latest_task_id, google_event_id=created_event['id'])
                            
                            if auto_sync_enabled:
                                st.success("✅ 自動同期によりGoogleカレンダーに同期しました")
                            else:
                                st.success("✅ Googleカレンダーにも同期しました")
                        else:
                            st.warning("⚠️ Googleカレンダーへの同期に失敗しました")
                    else:
                        st.warning("⚠️ タスクの取得に失敗しました")
                elif should_sync:
                    st.warning("⚠️ Googleカレンダーの認証に失敗しました")
                elif auto_sync_enabled:
                    st.info("💡 自動同期が有効ですが、Googleカレンダーの認証が必要です")


def render_task_calendar_sync_tab(auth_manager):
    """タスクカレンダー連携タブ"""
    st.write("**📅 カレンダー連携**")
    
    # TaskManagerをインスタンス化
    task_manager = TaskManager()
    
    # 認証状態の表示
    if not auth_manager:
        st.error("❌ Google認証マネージャーが利用できません")
        st.info("Google認証ライブラリが正しくインストールされているか確認してください")
    elif auth_manager.is_authenticated():
        st.success("✅ Googleカレンダー認証済み")
    else:
        st.warning("⚠️ Googleカレンダーが認証されていません")
        
        # 認証情報の設定状況を表示
        try:
            from config.config_manager import check_google_credentials
            credentials_status = check_google_credentials()
            
            st.info("🔍 認証情報の設定状況:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if credentials_status['client_id']['exists']:
                    st.success("✅ Client ID")
                else:
                    st.error("❌ Client ID")
            
            with col2:
                if credentials_status['client_secret']['exists']:
                    st.success("✅ Client Secret")
                else:
                    st.error("❌ Client Secret")
            
            with col3:
                if credentials_status['refresh_token']['exists']:
                    st.success("✅ Refresh Token")
                else:
                    st.warning("⚠️ Refresh Token")
        except Exception as e:
            st.warning(f"認証情報の確認に失敗しました: {e}")
        
        # Google認証ボタン
        if st.button("🔐 Googleカレンダー認証", key="google_auth_button"):
            try:
                if not auth_manager:
                    st.error("❌ 認証マネージャーが利用できません")
                    st.info("Google認証ライブラリが正しくインストールされているか確認してください")
                    return
                
                st.info("🔄 認証を開始しています...")
                auth_result = auth_manager.authenticate()
                if auth_result:
                    st.success("✅ 認証が完了しました")
                    st.info("ページを再読み込みして認証状態を確認してください")
                    st.rerun()
                else:
                    st.error("❌ 認証に失敗しました")
                    st.info("認証情報が正しく設定されているか確認してください")
                    st.info("初回認証の場合は、認証URLをクリックしてGoogle認証画面を開いてください")
            except Exception as e:
                st.error(f"❌ 認証エラー: {e}")
                st.info("認証情報の設定を確認してください")
                st.exception(e)
        return
    
    # タスク一覧表示
    tasks = task_manager.load_tasks()
    
    if tasks["tasks"]:
        st.write("**未同期タスク**")
        unsynced_tasks = {k: v for k, v in tasks["tasks"].items() 
                         if not v.get('google_event_id') and v['status'] != 'completed'}
        
        if unsynced_tasks:
            for task_id, task in unsynced_tasks.items():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"📋 {task['title']}")
                    if task['description']:
                        st.caption(task['description'])
                
                with col2:
                    st.write(f"📅 {task.get('due_date', '期限なし')}")
                
                with col3:
                    sync_key = f"sync_task_{task_id}_{uuid.uuid4().hex[:8]}"
                    if st.button("📅 同期", key=sync_key):
                        if task_manager.sync_to_google_calendar(task_id):
                            st.rerun()
        else:
            st.info("✅ すべてのタスクが同期済みです")
        
        # 一括同期
        st.write("### 一括操作")
        if st.button("📅 未同期タスクを一括同期"):
            service = auth_manager.get_service()
            if service:
                synced_count = 0
                for task_id, task in tasks["tasks"].items():
                    if not task.get('google_event_id') and task['status'] != 'completed':
                        if task_manager.sync_to_google_calendar(task_id):
                            synced_count += 1
                
                st.success(f"✅ {synced_count}件のタスクを同期しました")
                st.rerun()
            else:
                st.error("❌ Googleカレンダーサービスに接続できません")
    else:
        st.info("タスクがありません")


def render_task_settings_tab():
    """タスク設定タブ"""
    st.write("**⚙️ タスク設定**")
    
    # TaskManagerをインスタンス化
    task_manager = TaskManager()
    
    # 設定マネージャーをインスタンス化
    settings_manager = EnhancedSettingsManager()
    settings = settings_manager.load_settings()
    
    # タスク統計
    tasks = task_manager.load_tasks()
    total_tasks = len(tasks["tasks"])
    pending_tasks = len([t for t in tasks["tasks"].values() if t["status"] == "pending"])
    completed_tasks = len([t for t in tasks["tasks"].values() if t["status"] == "completed"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("総タスク数", total_tasks)
    with col2:
        st.metric("未完了", pending_tasks)
    with col3:
        st.metric("完了", completed_tasks)
    
    # カテゴリ別統計
    st.write("### カテゴリ別統計")
    category_stats = {}
    for task in tasks["tasks"].values():
        category = task.get("category", "未分類")
        if category not in category_stats:
            category_stats[category] = {"pending": 0, "completed": 0}
        category_stats[category][task["status"]] += 1
    
    for category, stats in category_stats.items():
        st.write(f"**{category}**: 未完了 {stats['pending']}件, 完了 {stats['completed']}件")
    
    # 優先度別統計
    st.write("### 優先度別統計")
    priority_stats = {}
    for task in tasks["tasks"].values():
        priority = task.get("priority", "中")
        if priority not in priority_stats:
            priority_stats[priority] = {"pending": 0, "completed": 0}
        priority_stats[priority][task["status"]] += 1
    
    for priority, stats in priority_stats.items():
        st.write(f"**{priority}**: 未完了 {stats['pending']}件, 完了 {stats['completed']}件")
    
    # 設定オプション
    st.write("### 設定オプション")
    
    # タスク管理設定の初期化
    if "task_management" not in settings:
        settings["task_management"] = {
            "auto_sync_to_calendar": False,
            "default_sync_to_calendar": True,
            "sync_completed_tasks": False,
            "calendar_timezone": "Asia/Tokyo",
            "default_event_duration": 60
        }
    
    # 自動同期設定
    auto_sync_key = f"task_auto_sync_{uuid.uuid4().hex[:8]}"
    default_sync_key = f"task_default_sync_{uuid.uuid4().hex[:8]}"
    sync_completed_key = f"task_sync_completed_{uuid.uuid4().hex[:8]}"
    timezone_key = f"task_timezone_{uuid.uuid4().hex[:8]}"
    duration_key = f"task_duration_{uuid.uuid4().hex[:8]}"
    
    auto_sync = st.checkbox(
        "Googleカレンダーに自動同期", 
        value=settings["task_management"]["auto_sync_to_calendar"], 
        key=auto_sync_key
    )
    if auto_sync:
        st.info("💡 新しいタスクが追加された際に自動的にGoogleカレンダーに同期されます")
    
    default_sync = st.checkbox(
        "新規タスクのデフォルト同期", 
        value=settings["task_management"]["default_sync_to_calendar"], 
        key=default_sync_key
    )
    if default_sync:
        st.info("💡 新規タスク追加時にGoogleカレンダー同期をデフォルトで有効にします")
    
    sync_completed = st.checkbox(
        "完了タスクも同期", 
        value=settings["task_management"]["sync_completed_tasks"], 
        key=sync_completed_key
    )
    if sync_completed:
        st.info("💡 完了したタスクもGoogleカレンダーに同期します")
    
    # カレンダー設定
    st.write("#### カレンダー設定")
    timezone = st.selectbox(
        "タイムゾーン",
        ["Asia/Tokyo", "UTC", "America/New_York", "Europe/London"],
        index=["Asia/Tokyo", "UTC", "America/New_York", "Europe/London"].index(
            settings["task_management"]["calendar_timezone"]
        ),
        key=timezone_key
    )
    
    duration = st.number_input(
        "デフォルトイベント時間（分）",
        min_value=15,
        max_value=480,
        value=settings["task_management"]["default_event_duration"],
        step=15,
        key=duration_key
    )
    
    # 設定保存
    if st.button("💾 設定を保存", key=f"save_task_settings_{uuid.uuid4().hex[:8]}"):
        settings["task_management"]["auto_sync_to_calendar"] = auto_sync
        settings["task_management"]["default_sync_to_calendar"] = default_sync
        settings["task_management"]["sync_completed_tasks"] = sync_completed
        settings["task_management"]["calendar_timezone"] = timezone
        settings["task_management"]["default_event_duration"] = duration
        
        if settings_manager.save_settings(settings):
            st.success("✅ 設定を保存しました")
        else:
            st.error("❌ 設定の保存に失敗しました")


def render_calendar_management_tab():
    """カレンダー管理タブ"""
    st.subheader("📅 カレンダー管理")
    
    # 統合認証マネージャーを取得
    auth_manager = get_google_auth_manager()
    
    # タブを作成
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 カレンダー", 
        "➕ イベント追加", 
        "✏️ イベント編集",
        "📊 イベント一覧", 
        "🔄 同期管理"
    ])
    
    with tab1:
        render_calendar_view_tab()
    
    with tab2:
        render_event_add_tab(auth_manager)
    
    with tab3:
        render_event_edit_tab(auth_manager)
    
    with tab4:
        render_event_list_tab()
    
    with tab5:
        render_calendar_sync_tab(auth_manager)


def render_calendar_view_tab():
    """カレンダー表示タブ"""
    st.write("**📅 カレンダー表示**")
    
    # CalendarManagerをインスタンス化
    calendar_manager = CalendarManager()
    
    # 現在の月のカレンダーを表示
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    st.write(f"**{year}年{month}月**")
    
    # イベントを読み込み
    events = calendar_manager.load_events()
    
    if events["events"]:
        # 今月のイベントをフィルター
        current_month_events = {}
        for event_id, event in events["events"].items():
            event_date = datetime.fromisoformat(event["start_date"])
            if event_date.year == year and event_date.month == month:
                current_month_events[event_id] = event
        
        if current_month_events:
            st.write("**今月のイベント**")
            for event_id, event in current_month_events.items():
                event_date = datetime.fromisoformat(event["start_date"])
                with st.expander(f"📅 {event_date.strftime('%m/%d')} - {event['title']}"):
                    st.write(f"**説明**: {event.get('description', '説明なし')}")
                    st.write(f"**開始**: {event['start_date']}")
                    st.write(f"**終了**: {event['end_date']}")
                    st.write(f"**カテゴリ**: {event.get('category', '未分類')}")
                    if event.get('google_event_id'):
                        st.write("✅ Googleカレンダーに同期済み")
        else:
            st.info("今月のイベントはありません")
    else:
        st.info("イベントがありません")
    
    # カレンダー表示の設定
    st.write("### カレンダー設定")
    col1, col2 = st.columns(2)
    
    with col1:
        show_past_events = st.checkbox("過去のイベントを表示", value=False, key="show_past_events")
        show_completed_tasks = st.checkbox("完了したタスクを表示", value=False, key="show_completed_tasks")
    
    with col2:
        default_view = st.selectbox("デフォルト表示", ["月", "週", "日"], key="default_calendar_view")
        auto_refresh = st.checkbox("自動更新", value=True, key="auto_refresh_calendar")


def render_event_list_tab():
    """イベント一覧タブ"""
    st.write("**📊 イベント一覧**")
    
    # CalendarManagerをインスタンス化
    calendar_manager = CalendarManager()
    
    # イベントを読み込み
    events = calendar_manager.load_events()
    
    if not events["events"]:
        st.info("📅 イベントがありません。新しいイベントを追加してください。")
        return
    
    # 一括編集モードの管理
    if 'bulk_edit_mode' not in st.session_state:
        st.session_state.bulk_edit_mode = False
    if 'selected_events' not in st.session_state:
        st.session_state.selected_events = set()
    
    # 一括編集モード切り替え
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("📋 一括編集", key="bulk_edit_toggle"):
            st.session_state.bulk_edit_mode = not st.session_state.bulk_edit_mode
            st.session_state.selected_events.clear()
            st.rerun()
    
    with col2:
        if st.session_state.bulk_edit_mode:
            st.info("一括編集モード: 複数のイベントを選択して一括で編集できます")
    
    # 一括編集フォーム
    if st.session_state.bulk_edit_mode and st.session_state.selected_events:
        render_bulk_edit_form(calendar_manager)
    
    # フィルター
    col1, col2, col3 = st.columns(3)
    with col1:
        date_filter = st.selectbox("日付", ["全て", "今日", "今週", "今月"], key="list_date_filter")
    with col2:
        category_filter = st.selectbox("カテゴリ", ["全て"] + list(set([e.get("category", "未分類") for e in events["events"].values()])), key="list_category_filter")
    with col3:
        sync_filter = st.selectbox("同期状態", ["全て", "同期済み", "未同期"], key="list_sync_filter")
    
    # イベントを表示
    for event_id, event in events["events"].items():
        # フィルター適用
        event_date = datetime.fromisoformat(event["start_date"])
        
        if date_filter == "今日" and event_date.date() != datetime.now().date():
            continue
        elif date_filter == "今週":
            week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
            week_end = week_start + timedelta(days=6)
            if not (week_start <= event_date.date() <= week_end):
                continue
        elif date_filter == "今月":
            if event_date.month != datetime.now().month or event_date.year != datetime.now().year:
                continue
        
        if category_filter != "全て" and event.get("category", "未分類") != category_filter:
            continue
        
        if sync_filter == "同期済み" and not event.get("google_event_id"):
            continue
        elif sync_filter == "未同期" and event.get("google_event_id"):
            continue
        
        # 一括編集モードの場合
        if st.session_state.bulk_edit_mode:
            checkbox_key = f"select_event_{event_id}_{uuid.uuid4().hex[:8]}"
            is_selected = st.checkbox(
                f"📅 {event_date.strftime('%m/%d %H:%M')} - {event.get('title', 'タイトルなし')}", 
                value=event_id in st.session_state.selected_events,
                key=checkbox_key
            )
            
            if is_selected:
                st.session_state.selected_events.add(event_id)
            else:
                st.session_state.selected_events.discard(event_id)
            
            # イベント詳細を展開可能に表示
            with st.expander("詳細", expanded=False):
                st.write(f"**説明**: {event.get('description', '説明なし')}")
                st.write(f"**開始**: {event['start_date']}")
                st.write(f"**終了**: {event['end_date']}")
                st.write(f"**カテゴリ**: {event.get('category', '未分類')}")
                if event.get('google_event_id'):
                    st.write("✅ Googleカレンダーに同期済み")
        
        else:
            # 通常表示モード
            with st.expander(f"📅 {event_date.strftime('%m/%d %H:%M')} - {event.get('title', 'タイトルなし')}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**説明**: {event.get('description', '説明なし')}")
                    st.write(f"**開始**: {event['start_date']}")
                    st.write(f"**終了**: {event['end_date']}")
                    st.write(f"**カテゴリ**: {event.get('category', '未分類')}")
                    if event.get('google_event_id'):
                        st.write("✅ Googleカレンダーに同期済み")
                
                with col2:
                    # 編集ボタン
                    edit_key = f"list_edit_event_{event_id}_{uuid.uuid4().hex[:8]}"
                    if st.button("✏️ 編集", key=edit_key):
                        st.session_state.editing_event_id = event_id
                        st.rerun()
                    
                    # 削除ボタン
                    delete_key = f"list_delete_event_{event_id}_{uuid.uuid4().hex[:8]}"
                    if st.button("🗑️ 削除", key=delete_key):
                        if calendar_manager.delete_event(event_id):
                            st.success("イベントを削除しました")
                            st.rerun()
                        else:
                            st.error("イベントの削除に失敗しました")


def render_bulk_edit_form(calendar_manager):
    """一括編集フォーム"""
    st.write("**📋 一括編集**")
    st.info(f"選択されたイベント数: {len(st.session_state.selected_events)}")
    
    with st.form("bulk_edit_form"):
        st.write("**変更する項目のみチェックしてください**")
        
        # 変更項目の選択
        col1, col2 = st.columns(2)
        with col1:
            update_category = st.checkbox("カテゴリを変更", key="bulk_update_category")
            update_sync = st.checkbox("同期状態を変更", key="bulk_update_sync")
        
        with col2:
            update_all_day = st.checkbox("終日設定を変更", key="bulk_update_all_day")
            update_description = st.checkbox("説明を変更", key="bulk_update_description")
        
        # 変更内容の入力
        update_data = {}
        
        if update_category:
            new_category = st.selectbox("新しいカテゴリ", ["会議", "予定", "イベント", "その他"], key="bulk_new_category")
            update_data["category"] = new_category
        
        if update_sync:
            new_sync = st.checkbox("Googleカレンダーに同期", key="bulk_new_sync")
            # 同期状態の変更は個別に処理する必要があるため、後で実装
        
        if update_all_day:
            new_all_day = st.checkbox("終日", key="bulk_new_all_day")
            update_data["all_day"] = new_all_day
        
        if update_description:
            new_description = st.text_area("新しい説明", key="bulk_new_description")
            if new_description.strip():
                update_data["description"] = new_description
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 一括更新")
        with col2:
            cancel = st.form_submit_button("❌ キャンセル")
        
        if submitted and update_data:
            # 一括更新を実行
            if calendar_manager.bulk_update_events(list(st.session_state.selected_events), **update_data):
                st.success(f"✅ {len(st.session_state.selected_events)}個のイベントを更新しました")
                st.session_state.selected_events.clear()
                st.session_state.bulk_edit_mode = False
                st.rerun()
            else:
                st.error("❌ 一括更新に失敗しました")
        
        elif cancel:
            st.session_state.selected_events.clear()
            st.session_state.bulk_edit_mode = False
            st.rerun()


def render_event_add_tab(auth_manager):
    """イベント追加タブ"""
    st.write("**➕ イベント追加**")
    
    # CalendarManagerをインスタンス化
    calendar_manager = CalendarManager()
    
    with st.form("add_event_form"):
        title = st.text_input("イベント名", key="event_title")
        description = st.text_area("説明", key="event_description")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日", key="event_start_date")
            start_time = st.time_input("開始時刻", key="event_start_time")
            category = st.selectbox("カテゴリ", ["会議", "予定", "イベント", "その他"], key="event_category")
        
        with col2:
            end_date = st.date_input("終了日", key="event_end_date")
            end_time = st.time_input("終了時刻", key="event_end_time")
            all_day = st.checkbox("終日", key="event_all_day")
        
        sync_to_calendar = st.checkbox("Googleカレンダーに同期", key="event_sync_calendar")
        
        submitted = st.form_submit_button("イベントを追加")
        
        if submitted and title:
            # 認証状態を確認
            if sync_to_calendar and (not auth_manager or not auth_manager.is_authenticated()):
                st.error("Googleカレンダーに同期するには認証が必要です")
                st.info("カレンダー連携タブでGoogleカレンダー認証を実行してください")
                return
            
            # 日時を結合
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
            
            # イベントを追加
            event_added = calendar_manager.add_event(
                title=title,
                description=description,
                start_date=start_datetime.isoformat(),
                end_date=end_datetime.isoformat(),
                all_day=all_day,
                category=category
            )
            
            if event_added:
                st.success("✅ イベントを追加しました")
                
                # Googleカレンダーに同期
                if sync_to_calendar and auth_manager.authenticate():
                    # 最新のイベントを取得
                    events = calendar_manager.load_events()
                    latest_event_id = None
                    latest_event = None
                    
                    for event_id, event in events["events"].items():
                        if event["title"] == title and event["description"] == description:
                            latest_event_id = event_id
                            latest_event = event
                            break
                    
                    if latest_event:
                        service = auth_manager.get_service()
                        if service:
                            google_event = {
                                'summary': title,
                                'description': description,
                                'start': {
                                    'dateTime': start_datetime.isoformat(),
                                    'timeZone': 'Asia/Tokyo',
                                },
                                'end': {
                                    'dateTime': end_datetime.isoformat(),
                                    'timeZone': 'Asia/Tokyo',
                                }
                            }
                            
                            if all_day:
                                google_event['start'] = {'date': start_date.isoformat()}
                                google_event['end'] = {'date': end_date.isoformat()}
                            
                            created_event = service.events().insert(
                                calendarId='primary', body=google_event
                            ).execute()
                            
                            calendar_manager.update_event(latest_event_id, google_event_id=created_event['id'])
                            st.success("✅ Googleカレンダーにも同期しました")
                        else:
                            st.warning("⚠️ Googleカレンダーへの同期に失敗しました")
                    else:
                        st.warning("⚠️ イベントの取得に失敗しました")
                elif sync_to_calendar:
                    st.warning("⚠️ Googleカレンダーの認証に失敗しました")


def render_event_edit_tab(auth_manager):
    """イベント編集タブ"""
    st.write("**✏️ イベント編集**")
    
    # CalendarManagerをインスタンス化
    calendar_manager = CalendarManager()
    
    # イベント一覧表示
    events = calendar_manager.load_events()
    
    if not events["events"]:
        st.info("📅 イベントがありません。新しいイベントを追加してください。")
        return
    
    # 編集モードの管理
    if 'editing_event_id' not in st.session_state:
        st.session_state.editing_event_id = None
    
    # フィルター
    col1, col2, col3 = st.columns(3)
    with col1:
        date_filter = st.selectbox("日付", ["全て", "今日", "今週", "今月"], key="edit_date_filter")
    with col2:
        category_filter = st.selectbox("カテゴリ", ["全て"] + list(set([e.get("category", "未分類") for e in events["events"].values()])), key="edit_category_filter")
    with col3:
        sync_filter = st.selectbox("同期状態", ["全て", "同期済み", "未同期"], key="edit_sync_filter")
    
    # イベントを表示
    for event_id, event in events["events"].items():
        # フィルター適用
        event_date = datetime.fromisoformat(event["start_date"])
        
        if date_filter == "今日" and event_date.date() != datetime.now().date():
            continue
        elif date_filter == "今週":
            week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
            week_end = week_start + timedelta(days=6)
            if not (week_start <= event_date.date() <= week_end):
                continue
        elif date_filter == "今月":
            if event_date.month != datetime.now().month or event_date.year != datetime.now().year:
                continue
        
        if category_filter != "全て" and event.get("category", "未分類") != category_filter:
            continue
        
        if sync_filter == "同期済み" and not event.get("google_event_id"):
            continue
        elif sync_filter == "未同期" and event.get("google_event_id"):
            continue
        
        # 編集モードかどうかチェック
        is_editing = st.session_state.editing_event_id == event_id
        
        with st.expander(f"📅 {event_date.strftime('%m/%d %H:%M')} - {event.get('title', 'タイトルなし')}", expanded=is_editing):
            if is_editing:
                # 編集フォーム
                render_event_edit_form(calendar_manager, event_id, event, auth_manager)
            else:
                # 表示モード
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**説明**: {event.get('description', '説明なし')}")
                    st.write(f"**開始**: {event['start_date']}")
                    st.write(f"**終了**: {event['end_date']}")
                    st.write(f"**カテゴリ**: {event.get('category', '未分類')}")
                    if event.get('google_event_id'):
                        st.write("✅ Googleカレンダーに同期済み")
                
                with col2:
                    # 編集ボタン
                    edit_key = f"edit_event_{event_id}_{uuid.uuid4().hex[:8]}"
                    if st.button("✏️ 編集", key=edit_key):
                        st.session_state.editing_event_id = event_id
                        st.rerun()
                    
                    # 削除ボタン
                    delete_key = f"delete_event_{event_id}_{uuid.uuid4().hex[:8]}"
                    if st.button("🗑️ 削除", key=delete_key):
                        if calendar_manager.delete_event(event_id):
                            st.success("イベントを削除しました")
                            st.rerun()
                        else:
                            st.error("イベントの削除に失敗しました")


def render_event_edit_form(calendar_manager, event_id, event, auth_manager):
    """イベント編集フォーム"""
    st.write("**イベント編集**")
    
    with st.form(f"edit_event_form_{event_id}"):
        # 現在の値をデフォルトとして設定
        current_start = datetime.fromisoformat(event["start_date"])
        current_end = datetime.fromisoformat(event["end_date"])
        
        title = st.text_input("イベント名", value=event.get("title", ""), key=f"edit_title_{event_id}")
        description = st.text_area("説明", value=event.get("description", ""), key=f"edit_description_{event_id}")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日", value=current_start.date(), key=f"edit_start_date_{event_id}")
            start_time = st.time_input("開始時刻", value=current_start.time(), key=f"edit_start_time_{event_id}")
            category = st.selectbox("カテゴリ", ["会議", "予定", "イベント", "その他"], 
                                  index=["会議", "予定", "イベント", "その他"].index(event.get("category", "その他")), 
                                  key=f"edit_category_{event_id}")
        
        with col2:
            end_date = st.date_input("終了日", value=current_end.date(), key=f"edit_end_date_{event_id}")
            end_time = st.time_input("終了時刻", value=current_end.time(), key=f"edit_end_time_{event_id}")
            all_day = st.checkbox("終日", value=event.get("all_day", False), key=f"edit_all_day_{event_id}")
        
        # Googleカレンダー同期オプション
        sync_to_calendar = st.checkbox("Googleカレンダーに同期", 
                                     value=bool(event.get("google_event_id")), 
                                     key=f"edit_sync_calendar_{event_id}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            submitted = st.form_submit_button("💾 保存")
        with col2:
            cancel = st.form_submit_button("❌ キャンセル")
        with col3:
            duplicate = st.form_submit_button("📋 複製")
        
        if submitted and title:
            # 認証状態を確認
            if sync_to_calendar and (not auth_manager or not auth_manager.is_authenticated()):
                st.error("Googleカレンダーに同期するには認証が必要です")
                st.info("カレンダー連携タブでGoogleカレンダー認証を実行してください")
                return
            
            # 日時を結合
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
            
            # イベントを更新
            update_data = {
                "title": title,
                "description": description,
                "start_date": start_datetime.isoformat(),
                "end_date": end_datetime.isoformat(),
                "all_day": all_day,
                "category": category
            }
            
            if calendar_manager.update_event(event_id, **update_data):
                st.success("✅ イベントを更新しました")
                st.session_state.editing_event_id = None
                st.rerun()
            else:
                st.error("❌ イベントの更新に失敗しました")
        
        elif cancel:
            st.session_state.editing_event_id = None
            st.rerun()
        
        elif duplicate:
            # イベントを複製
            new_event_id = str(uuid.uuid4())
            new_event = event.copy()
            new_event["id"] = new_event_id
            new_event["title"] = f"{title} (コピー)"
            new_event["created_at"] = datetime.now().isoformat()
            new_event["google_event_id"] = None  # 複製時はGoogle同期をリセット
            
            events = calendar_manager.load_events()
            events["events"][new_event_id] = new_event
            
            if calendar_manager.save_events(events):
                st.success("✅ イベントを複製しました")
                st.session_state.editing_event_id = None
                st.rerun()
            else:
                st.error("❌ イベントの複製に失敗しました")


def render_calendar_sync_tab(auth_manager):
    """カレンダー同期管理タブ"""
    st.write("**🔄 同期管理**")
    
    # CalendarManagerをインスタンス化
    calendar_manager = CalendarManager()
    
    # 認証状態の表示
    if not auth_manager:
        st.error("❌ Google認証マネージャーが利用できません")
        st.info("Google認証ライブラリが正しくインストールされているか確認してください")
        return
    
    # 認証状態の詳細表示
    st.subheader("🔐 認証状態")
    
    if auth_manager.is_authenticated():
        st.success("✅ Googleカレンダー認証済み")
        
        # サービス接続テスト
        service = auth_manager.get_service()
        if service:
            try:
                # カレンダー情報を取得して接続をテスト
                calendar_list = service.calendarList().list().execute()
                st.success(f"✅ Googleカレンダーに接続済み（利用可能カレンダー: {len(calendar_list.get('items', []))}個）")
            except Exception as e:
                error_msg = str(e)
                if "invalid_grant" in error_msg or "Token has been expired" in error_msg:
                    st.error("❌ トークンが期限切れまたは無効化されています")
                    st.info("🔑 認証情報の更新が必要です")
                    
                    # 認証情報更新ボタン
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 認証情報を更新", key="refresh_credentials_fixed"):
                            try:
                                if hasattr(auth_manager, 'refresh_credentials'):
                                    if auth_manager.refresh_credentials():
                                        st.success("✅ 認証情報の更新が完了しました")
                                        st.rerun()
                                    else:
                                        st.error("❌ 認証情報の更新に失敗しました")
                                        st.info("新しいリフレッシュトークンが必要です")
                                        st.info("以下の手順を実行してください：")
                                        st.info("1. 認証フローをリセット")
                                        st.info("2. 新しい認証を実行")
                                        st.info("3. 新しいリフレッシュトークンを取得")
                                        
                                        # 詳細診断情報
                                        with st.expander("🔍 詳細診断情報", expanded=False):
                                            st.write("**現在の認証情報状況:**")
                                            try:
                                                from config.config_manager import check_google_credentials
                                                credentials_status = check_google_credentials()
                                                
                                                col1, col2, col3 = st.columns(3)
                                                with col1:
                                                    if credentials_status['client_id']['exists']:
                                                        st.success("✅ Client ID")
                                                    else:
                                                        st.error("❌ Client ID")
                                                
                                                with col2:
                                                    if credentials_status['client_secret']['exists']:
                                                        st.success("✅ Client Secret")
                                                    else:
                                                        st.error("❌ Client Secret")
                                                
                                                with col3:
                                                    if credentials_status['refresh_token']['exists']:
                                                        st.warning("⚠️ Refresh Token（無効）")
                                                    else:
                                                        st.error("❌ Refresh Token")
                                                
                                                st.write("**推奨される対処法:**")
                                                if not credentials_status['client_id']['exists'] or not credentials_status['client_secret']['exists']:
                                                    st.error("1. Google Cloud ConsoleでOAuth 2.0クライアントIDを確認")
                                                    st.error("2. Streamlit Secretsに正しい認証情報を設定")
                                                elif not credentials_status['refresh_token']['exists']:
                                                    st.error("1. 初回認証を実行してリフレッシュトークンを取得")
                                                    st.error("2. 取得したトークンをStreamlit Secretsに設定")
                                                else:
                                                    st.warning("1. リフレッシュトークンが無効化されている可能性があります")
                                                    st.warning("2. 新しい認証を実行してください")
                                                    
                                            except Exception as diag_error:
                                                st.error(f"診断情報の取得に失敗: {diag_error}")
                            except Exception as refresh_error:
                                st.error(f"❌ 認証情報更新エラー: {refresh_error}")
                    
                    with col2:
                        if st.button("🔄 認証フローをリセット", key="reset_auth_flow_fixed"):
                            try:
                                # セッション状態をクリア
                                if 'google_auth_flow' in st.session_state:
                                    del st.session_state.google_auth_flow
                                if 'google_auth_url' in st.session_state:
                                    del st.session_state.google_auth_url
                                if 'google_auth_key' in st.session_state:
                                    del st.session_state.google_auth_key
                                if 'google_credentials' in st.session_state:
                                    del st.session_state.google_credentials
                                if 'google_auth_status' in st.session_state:
                                    st.session_state.google_auth_status = False
                                
                                st.success("✅ 認証フローがリセットされました")
                                st.info("ページを再読み込みして認証状態を確認してください")
                                
                                # ページ再読み込みボタン
                                if st.button("🔄 ページを再読み込み", key="reload_page_after_reset"):
                                    st.rerun()
                                
                            except Exception as reset_error:
                                st.error(f"❌ 認証フローリセットエラー: {reset_error}")
                else:
                    st.warning(f"⚠️ カレンダー接続テストに失敗: {e}")
        else:
            st.warning("⚠️ カレンダーサービスに接続できません")
    else:
        st.warning("⚠️ Googleカレンダーが認証されていません")
        
        # 認証情報の設定状況を表示
        try:
            from config.config_manager import check_google_credentials
            credentials_status = check_google_credentials()
            
            st.info("🔍 認証情報の設定状況:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if credentials_status['client_id']['exists']:
                    st.success("✅ Client ID")
                else:
                    st.error("❌ Client ID")
            
            with col2:
                if credentials_status['client_secret']['exists']:
                    st.success("✅ Client Secret")
                else:
                    st.error("❌ Client Secret")
            
            with col3:
                if credentials_status['refresh_token']['exists']:
                    st.success("✅ Refresh Token")
                else:
                    st.warning("⚠️ Refresh Token")
            
            # 全体状況の表示
            if credentials_status['all_required']:
                if credentials_status['ready_for_auth']:
                    st.success("🎉 すべての認証情報が設定されています！")
                    st.info("認証ボタンをクリックしてGoogleカレンダーに接続してください")
                else:
                    st.warning("⚠️ 基本認証情報は設定済みですが、リフレッシュトークンが無効です")
                    st.info("初回認証を再実行してリフレッシュトークンを更新してください")
            else:
                st.error("❌ 必要な認証情報が不足しています")
                st.info("Streamlit Secretsまたは環境変数に認証情報を設定してください")
                
        except Exception as e:
            st.warning(f"認証情報の確認に失敗しました: {e}")
        
        # Google認証ボタン
        st.subheader("🔐 Google認証")
        if st.button("🔐 Googleカレンダー認証", key="google_auth_button_fixed"):
            try:
                st.info("🔄 認証を開始しています...")
                auth_result = auth_manager.authenticate()
                if auth_result:
                    st.success("✅ 認証が完了しました")
                    st.info("ページを再読み込みして認証状態を確認してください")
                    st.rerun()
                else:
                    st.error("❌ 認証に失敗しました")
                    st.info("認証情報が正しく設定されているか確認してください")
                    st.info("初回認証の場合は、認証URLをクリックしてGoogle認証画面を開いてください")
            except Exception as e:
                st.error(f"❌ 認証エラー: {e}")
                st.info("認証情報の設定を確認してください")
                st.exception(e)
        return
    
    # イベント一覧表示
    st.subheader("📅 イベント同期状況")
    events = calendar_manager.load_events()
    
    if events["events"]:
        # 同期状況の統計
        total_events = len(events["events"])
        synced_events = len([e for e in events["events"].values() if e.get('google_event_id')])
        unsynced_events = total_events - synced_events
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("総イベント数", total_events)
        with col2:
            st.metric("同期済み", synced_events)
        with col3:
            st.metric("未同期", unsynced_events)
        
        # 未同期イベントの表示
        if unsynced_events > 0:
            st.write("**未同期イベント**")
            unsynced_events_dict = {k: v for k, v in events["events"].items() 
                                  if not v.get('google_event_id')}
            
            for event_id, event in unsynced_events_dict.items():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"📅 {event['title']}")
                    if event.get('description'):
                        st.caption(event['description'])
                
                with col2:
                    st.write(f"📅 {event['start_date'][:10]}")
                
                with col3:
                    sync_key = f"sync_event_{event_id}"
                    if st.button("📅 同期", key=sync_key):
                        if calendar_manager.sync_to_google_calendar(event_id):
                            st.success("✅ 同期完了")
                            st.rerun()
                        else:
                            st.error("❌ 同期失敗")
            
            # 一括同期
            st.write("### 一括操作")
            if st.button("📅 未同期イベントを一括同期", key="bulk_sync_events_fixed"):
                service = auth_manager.get_service()
                if service:
                    synced_count = 0
                    for event_id, event in events["events"].items():
                        if not event.get('google_event_id'):
                            if calendar_manager.sync_to_google_calendar(event_id):
                                synced_count += 1
                    
                    st.success(f"✅ {synced_count}件のイベントを同期しました")
                    st.rerun()
                else:
                    st.error("❌ Googleカレンダーサービスに接続できません")
        else:
            st.success("✅ すべてのイベントが同期済みです")
    else:
        st.info("イベントがありません")
    
    # 認証解除
    st.subheader("🔓 認証管理")
    if st.button("🚪 ログアウト", key="logout_google_fixed"):
        if hasattr(auth_manager, 'logout'):
            auth_manager.logout()
        else:
            # セッション状態をクリア
            if 'google_credentials' in st.session_state:
                del st.session_state.google_credentials
            if 'google_auth_status' in st.session_state:
                st.session_state.google_auth_status = False
        
        st.success("ログアウトしました")
        st.rerun()

def render_history_tab():
    """履歴タブ"""
    st.subheader("📜 履歴")
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

def render_statistics_tab():
    """統計タブ"""
    st.subheader("📊 統計")
    st.write("統計機能は開発中です。")
    
    # 基本的な統計情報
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📝 文字起こし回数", _get_transcription_count())
    
    with col2:
        st.metric("�� 録音ファイル数", _get_recording_count())
    
    with col3:
        st.metric("📋 タスク数", _get_task_count())

def _get_transcription_count() -> int:
    """文字起こし回数を取得"""
    transcriptions_dir = "transcriptions"
    if os.path.exists(transcriptions_dir):
        return len([f for f in os.listdir(transcriptions_dir) if f.endswith('.txt')])
    return 0

def _get_recording_count() -> int:
    """録音ファイル数を取得"""
    recordings_dir = "recordings"
    if os.path.exists(recordings_dir):
        return len([f for f in os.listdir(recordings_dir) if f.endswith(('.wav', '.mp3', '.m4a'))])
    return 0

def _get_task_count() -> int:
    """タスク数を取得"""
    try:
        if UTILS_AUDIOREC_AVAILABLE:
            task_manager = TaskManager()
            tasks = task_manager.get_all_tasks()
            return len(tasks)
    except:
        pass
    return 0

class SettingsUI:
    """設定UI統合クラス"""
    
    def __init__(self):
        if UTILS_AUDIOREC_AVAILABLE:
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
            # フォールバック用のダミーインスタンス
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
        st.title("⚙️ 設定")
        
        # 環境情報とGoogle認証情報の表示
        self._display_environment_and_auth_info()
        
        # 設定タブの表示
        if UTILS_AUDIOREC_AVAILABLE:
            render_enhanced_settings_tab(self.settings_manager)
        else:
            st.warning("設定機能は現在利用できません")
    
    def _display_environment_and_auth_info(self):
        """環境情報とGoogle認証情報の設定状況を表示"""
        st.subheader("🌍 環境情報")
        
        # 基本環境情報
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Python**: {sys.version}")
            st.write(f"**Streamlit**: {st.__version__}")
        
        with col2:
            st.write(f"**OS**: {os.name}")
            st.write(f"**作業ディレクトリ**: {os.getcwd()}")
        
        # Google認証情報の設定状況
        st.subheader("🔐 Google認証情報の設定状況")
        
        try:
            # config_managerから認証情報を取得
            from config.config_manager import get_secret, check_google_credentials
            
            # 認証情報の確認
            client_id = get_secret('GOOGLE_CLIENT_ID')
            client_secret = get_secret('GOOGLE_CLIENT_SECRET')
            refresh_token = get_secret('GOOGLE_REFRESH_TOKEN')
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if client_id:
                    st.success("✅ GOOGLE_CLIENT_ID: 設定済み")
                else:
                    st.error("❌ GOOGLE_CLIENT_ID: 未設定")
            
            with col2:
                if client_secret:
                    st.success("✅ GOOGLE_CLIENT_SECRET: 設定済み")
                else:
                    st.error("❌ GOOGLE_CLIENT_SECRET: 未設定")
            
            with col3:
                if refresh_token:
                    st.success("✅ GOOGLE_REFRESH_TOKEN: 設定済み")
                else:
                    st.warning("⚠️ GOOGLE_REFRESH_TOKEN: 未設定")
            
            # 詳細な認証情報チェック
            if hasattr(check_google_credentials, '__call__'):
                try:
                    auth_status = check_google_credentials()
                    if auth_status:
                        st.success("✅ Google認証情報の検証: 成功")
                    else:
                        st.error("❌ Google認証情報の検証: 失敗")
                except Exception as e:
                    st.warning(f"⚠️ Google認証情報の検証エラー: {e}")
            
        except ImportError:
            st.warning("⚠️ config_managerが利用できません")
        except Exception as e:
            st.error(f"❌ 認証情報の確認エラー: {e}")
        
        st.divider()
    
    def display_user_dictionary_page(self):
        """ユーザー辞書ページ表示"""
        if UTILS_AUDIOREC_AVAILABLE:
            render_user_dictionary_tab()
        else:
            st.warning("ユーザー辞書機能は現在利用できません")
    
    def display_command_management_page(self):
        """コマンド管理ページ表示"""
        if UTILS_AUDIOREC_AVAILABLE:
            render_commands_tab()
        else:
            st.warning("コマンド管理機能は現在利用できません")
    
    def display_device_management_page(self):
        """デバイス管理ページ表示"""
        if UTILS_AUDIOREC_AVAILABLE:
            settings = self.settings_manager.load_settings()
            render_device_settings_tab(settings, self.settings_manager)
        else:
            st.warning("デバイス管理機能は現在利用できません")
    
    def display_task_management_page(self):
        """タスク管理ページ表示"""
        if UTILS_AUDIOREC_AVAILABLE:
            render_task_management_tab()
        else:
            st.warning("タスク管理機能は現在利用できません")
    
    def display_calendar_page(self):
        """カレンダーページ表示"""
        if UTILS_AUDIOREC_AVAILABLE:
            render_calendar_management_tab()
        else:
            st.warning("カレンダー機能は現在利用できません")
    
    def display_history_page(self):
        """履歴ページ表示"""
        if UTILS_AUDIOREC_AVAILABLE:
            render_history_tab()
        else:
            st.warning("履歴機能は現在利用できません")
    
    def display_statistics_page(self):
        """統計ページ表示"""
        if UTILS_AUDIOREC_AVAILABLE:
            render_statistics_tab()
        else:
            st.warning("統計機能は現在利用できません") 