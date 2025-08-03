"""
app_audiorec.py用の拡張設定UIコンポーネント
設定、ユーザー辞書、コマンド、デバイス管理などのUIを提供
"""

import streamlit as st
import json
import os
from datetime import datetime, date
from utils_audiorec import (
    EnhancedSettingsManager, CommandManager, UserDictionaryManager,
    TaskManager, CalendarManager, TaskAnalyzer, EventAnalyzer,
    GoogleCalendarManager
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

def render_task_management_tab():
    """タスク管理タブのレンダリング"""
    st.subheader("📋 タスク管理")
    
    # タスクマネージャーの初期化
    task_manager = TaskManager()
    
    # タブの作成
    task_tab1, task_tab2, task_tab3 = st.tabs(["📝 タスク一覧", "➕ タスク追加", "⚙️ タスク設定"])
    
    with task_tab1:
        st.write("### 📝 タスク一覧")
        
        # フィルター
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox(
                "ステータス",
                ["all", "pending", "in_progress", "completed"],
                format_func=lambda x: {"all": "すべて", "pending": "未完了", "in_progress": "進行中", "completed": "完了"}[x]
            )
        
        with col2:
            priority_filter = st.selectbox(
                "優先度",
                ["all", "high", "medium", "low"],
                format_func=lambda x: {"all": "すべて", "high": "高", "medium": "中", "low": "低"}[x]
            )
        
        with col3:
            category_filter = st.selectbox(
                "カテゴリ",
                ["all", "general", "work", "personal", "音声文字起こし"],
                format_func=lambda x: {"all": "すべて", "general": "一般", "work": "仕事", "personal": "個人", "音声文字起こし": "音声文字起こし"}[x]
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
                    
                    with col2:
                        # ステータス変更
                        new_status = st.selectbox(
                            "ステータス",
                            ["pending", "in_progress", "completed"],
                            index=["pending", "in_progress", "completed"].index(task["status"]),
                            key=f"status_{task_id}"
                        )
                        
                        if new_status != task["status"]:
                            task_manager.update_task(task_id, status=new_status)
                            st.success("ステータスを更新しました")
                        
                        # 削除ボタン
                        if st.button("🗑️ 削除", key=f"delete_{task_id}"):
                            if task_manager.delete_task(task_id):
                                st.success("タスクを削除しました")
                                st.rerun()
        else:
            st.info("タスクがありません")
    
    with task_tab2:
        st.write("### ➕ タスク追加")
        
        with st.form("add_task_form"):
            title = st.text_input("タイトル *")
            description = st.text_area("説明")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                priority = st.selectbox("優先度", ["low", "medium", "high"])
            with col2:
                category = st.selectbox("カテゴリ", ["general", "work", "personal", "音声文字起こし"])
            with col3:
                due_date = st.date_input("期限")
            
            submitted = st.form_submit_button("タスクを追加")
            
            if submitted and title:
                if task_manager.add_task(
                    title=title,
                    description=description,
                    priority=priority,
                    due_date=due_date.isoformat() if due_date else None,
                    category=category
                ):
                    st.success("タスクを追加しました")
                else:
                    st.error("タスクの追加に失敗しました")
    
    with task_tab3:
        st.write("### ⚙️ タスク設定")
        
        # 統計情報
        tasks = task_manager.load_tasks()
        total_tasks = len(tasks["tasks"])
        pending_tasks = len([t for t in tasks["tasks"].values() if t["status"] == "pending"])
        completed_tasks = len([t for t in tasks["tasks"].values() if t["status"] == "completed"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("総タスク数", total_tasks)
        with col2:
            st.metric("未完了タスク", pending_tasks)
        with col3:
            st.metric("完了タスク", completed_tasks)
        
        # 一括操作
        st.write("### 一括操作")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ 完了タスクを削除"):
                for task_id, task in tasks["tasks"].items():
                    if task["status"] == "completed":
                        task_manager.delete_task(task_id)
                st.success("完了タスクを削除しました")
        
        with col2:
            if st.button("📊 統計をリセット"):
                st.info("統計情報をリセットしました")

def render_calendar_management_tab():
    """カレンダー管理タブのレンダリング"""
    st.subheader("📅 カレンダー管理")
    
    # カレンダーマネージャーの初期化
    calendar_manager = CalendarManager()
    
    # タブの作成
    cal_tab1, cal_tab2, cal_tab3 = st.tabs(["📅 カレンダー", "➕ イベント追加", "📊 イベント一覧"])
    
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
                    
                    # 削除ボタン
                    if st.button("🗑️ 削除", key=f"delete_event_{event_id}"):
                        if calendar_manager.delete_event(event_id):
                            st.success("イベントを削除しました")
                            st.rerun()
        else:
            st.info(f"{selected_date} のイベントはありません")
    
    with cal_tab2:
        st.write("### ➕ イベント追加")
        
        with st.form("add_event_form"):
            title = st.text_input("タイトル *")
            description = st.text_area("説明")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                start_date = st.date_input("開始日")
            with col2:
                end_date = st.date_input("終了日")
            with col3:
                category = st.selectbox("カテゴリ", ["general", "work", "personal", "音声文字起こし"])
            
            all_day = st.checkbox("終日")
            
            submitted = st.form_submit_button("イベントを追加")
            
            if submitted and title:
                if calendar_manager.add_event(
                    title=title,
                    description=description,
                    start_date=start_date.isoformat() if start_date else None,
                    end_date=end_date.isoformat() if end_date else None,
                    all_day=all_day,
                    category=category
                ):
                    st.success("イベントを追加しました")
                else:
                    st.error("イベントの追加に失敗しました")
    
    with cal_tab3:
        st.write("### 📊 イベント一覧")
        
        # カテゴリフィルター
        category_filter = st.selectbox(
            "カテゴリ",
            ["all", "general", "work", "personal", "音声文字起こし"],
            format_func=lambda x: {"all": "すべて", "general": "一般", "work": "仕事", "personal": "個人", "音声文字起こし": "音声文字起こし"}[x]
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
                    st.write(f"**説明**: {event['description']}")
                    st.write(f"**カテゴリ**: {event['category']}")
                    if event['start_date']:
                        st.write(f"**開始**: {event['start_date']}")
                    if event['end_date']:
                        st.write(f"**終了**: {event['end_date']}")
                    st.write(f"**終日**: {'はい' if event['all_day'] else 'いいえ'}")
                    st.write(f"**作成日**: {event['created_at'][:10]}")
        else:
            st.info("イベントがありません") 

def render_google_calendar_tab():
    """Googleカレンダー連携タブをレンダリング"""
    st.header("📅 Googleカレンダー連携")
    
    # Googleカレンダーマネージャーを初期化
    google_calendar = GoogleCalendarManager()
    
    # タブを作成
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔐 認証設定", 
        "📋 カレンダー一覧", 
        "🔄 同期", 
        "📝 イベント管理"
    ])
    
    with tab1:
        st.subheader("Google認証設定")
        
        # 認証ファイルの確認
        if os.path.exists('credentials.json'):
            st.success("✅ credentials.jsonファイルが見つかりました")
            
            # 認証ボタン
            if st.button("🔐 Google認証を実行"):
                with st.spinner("Google認証を実行中..."):
                    if google_calendar.authenticate():
                        st.success("✅ Google認証が完了しました")
                    else:
                        st.error("❌ Google認証に失敗しました")
        else:
            st.error("❌ credentials.jsonファイルが見つかりません")
            st.info("""
            **Google認証ファイルの設定手順:**
            
            1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
            2. 新しいプロジェクトを作成
            3. Google Calendar APIを有効化
            4. 認証情報を作成（OAuth 2.0クライアントID）
            5. credentials.jsonファイルをダウンロード
            6. このファイルをプロジェクトのルートディレクトリに配置
            """)
    
    with tab2:
        st.subheader("利用可能なカレンダー")
        
        if st.button("📋 カレンダー一覧を取得"):
            with st.spinner("カレンダー一覧を取得中..."):
                calendars = google_calendar.get_calendars()
                
                if calendars:
                    st.success(f"✅ {len(calendars)}個のカレンダーが見つかりました")
                    
                    for calendar in calendars:
                        with st.expander(f"📅 {calendar.get('summary', '無題')}"):
                            st.write(f"**ID:** {calendar.get('id', 'N/A')}")
                            st.write(f"**説明:** {calendar.get('description', '説明なし')}")
                            st.write(f"**アクセス権限:** {calendar.get('accessRole', 'N/A')}")
                            st.write(f"**プライマリ:** {'はい' if calendar.get('primary') else 'いいえ'}")
                else:
                    st.warning("⚠️ カレンダーが見つかりませんでした")
    
    with tab3:
        st.subheader("カレンダー同期")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📤 ローカル → Google")
            if st.button("🔄 ローカルイベントをGoogleカレンダーに同期"):
                # ローカルイベントを取得
                calendar_manager = CalendarManager()
                local_events = calendar_manager.get_all_events()
                
                if local_events:
                    with st.spinner("Googleカレンダーに同期中..."):
                        if google_calendar.sync_local_to_google(local_events):
                            st.success("✅ 同期が完了しました")
                        else:
                            st.error("❌ 同期に失敗しました")
                else:
                    st.warning("⚠️ 同期するローカルイベントがありません")
        
        with col2:
            st.subheader("📥 Google → ローカル")
            if st.button("🔄 Googleカレンダーからローカルに同期"):
                with st.spinner("Googleカレンダーから同期中..."):
                    google_events = google_calendar.sync_google_to_local()
                    
                    if google_events:
                        # ローカルカレンダーに追加
                        calendar_manager = CalendarManager()
                        for event in google_events:
                            calendar_manager.add_event(event)
                        
                        st.success(f"✅ {len(google_events)}件のイベントを同期しました")
                    else:
                        st.warning("⚠️ 同期するGoogleカレンダーのイベントがありません")
    
    with tab4:
        st.subheader("Googleカレンダーイベント管理")
        
        # イベント取得
        if st.button("📋 Googleカレンダーのイベントを取得"):
            with st.spinner("イベントを取得中..."):
                events = google_calendar.get_events(max_results=20)
                
                if events:
                    st.success(f"✅ {len(events)}件のイベントが見つかりました")
                    
                    for event in events:
                        with st.expander(f"📅 {event.get('summary', '無題')}"):
                            st.write(f"**開始:** {event['start'].get('dateTime', event['start'].get('date'))}")
                            st.write(f"**終了:** {event['end'].get('dateTime', event['end'].get('date'))}")
                            st.write(f"**説明:** {event.get('description', '説明なし')}")
                            
                            # 削除ボタン
                            if st.button(f"🗑️ 削除", key=f"delete_{event['id']}"):
                                if google_calendar.delete_event(event['id']):
                                    st.success("✅ イベントを削除しました")
                                    st.rerun()
                                else:
                                    st.error("❌ 削除に失敗しました")
                else:
                    st.warning("⚠️ イベントが見つかりませんでした") 