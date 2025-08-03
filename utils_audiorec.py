"""
app_audiorec.py用の統合ユーティリティクラス
設定管理、デバイス管理、ユーザー辞書、コマンド処理などの機能を統合
"""

import json
import os
import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import tempfile
import wave
import numpy as np
import uuid

class EnhancedSettingsManager:
    """拡張設定管理クラス"""
    
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
                "chunk_size": 1024,
                "format": "paInt16",
                "channels": 1,
                "sample_rate": 44100,
                "gain": 2.0,
                "duration": 5
            },
            "whisper": {
                "model_size": "base",
                "language": "ja",
                "temperature": 0.0,
                "compression_ratio_threshold": 2.4,
                "logprob_threshold": -1.0,
                "no_speech_threshold": 0.6,
                "condition_on_previous_text": True,
                "initial_prompt": "これは日本語の音声です。"
            },
            "device": {
                "selected_device_index": None,
                "selected_device_name": None,
                "auto_select_default": True,
                "test_device_on_select": True
            },
            "ui": {
                "show_advanced_options": False,
                "auto_save_recordings": True,
                "show_quality_analysis": True,
                "show_level_monitoring": True,
                "auto_start_recording": False,
                "auto_recording_threshold": 300,
                "auto_recording_delay": 1.0
            },
            "transcription": {
                "auto_transcribe": False,
                "save_transcriptions": True
            },
            "troubleshooting": {
                "retry_count": 3,
                "timeout_seconds": 10,
                "enable_error_recovery": True,
                "log_errors": True
            },
            "llm": {
                "api_key": "",
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_tokens": 1000,
                "enabled": False
            },
            "shortcuts": {
                "enabled": True,
                "global_hotkeys": True,
                "keys": {
                    "start_recording": "F9",
                    "stop_recording": "F10",
                    "transcribe": "F11",
                    "clear_text": "F12",
                    "save_recording": "Ctrl+Shift+S",
                    "open_settings": "Ctrl+Shift+O",
                    "open_dictionary": "Ctrl+Shift+D",
                    "open_commands": "Ctrl+Shift+C",
                    "voice_correction": "Ctrl+Shift+V"
                },
                "modifiers": {
                    "ctrl": True,
                    "shift": False,
                    "alt": False
                }
            }
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    return self._merge_settings(default_settings, loaded_settings)
            else:
                return default_settings
        except Exception as e:
            st.error(f"設定読み込みエラー: {e}")
            return default_settings
    
    def _merge_settings(self, default_settings, loaded_settings):
        """設定をマージして不足しているキーを補完"""
        merged = default_settings.copy()
        
        for key, value in loaded_settings.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_settings(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def save_settings(self, settings):
        """設定を保存"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"設定保存エラー: {e}")
            return False

class UserDictionaryManager:
    """ユーザー辞書管理クラス"""
    
    def __init__(self):
        self.dictionary_file = "settings/user_dictionary.json"
        self.dictionary = self.load_dictionary()
    
    def load_dictionary(self):
        """辞書を読み込み"""
        try:
            if os.path.exists(self.dictionary_file):
                with open(self.dictionary_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                default_dict = {
                    "categories": {
                        "技術用語": {
                            "description": "技術関連の用語",
                            "entries": {}
                        },
                        "略語": {
                            "description": "略語とその意味",
                            "entries": {}
                        },
                        "カスタム": {
                            "description": "ユーザー定義の用語",
                            "entries": {}
                        }
                    },
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "total_entries": 0
                    }
                }
                self.save_dictionary(default_dict)
                return default_dict
        except Exception as e:
            st.error(f"辞書読み込みエラー: {e}")
            return {"categories": {}, "metadata": {}}
    
    def save_dictionary(self, dictionary=None):
        """辞書を保存"""
        if dictionary is None:
            dictionary = self.dictionary
        
        try:
            os.makedirs(os.path.dirname(self.dictionary_file), exist_ok=True)
            with open(self.dictionary_file, 'w', encoding='utf-8') as f:
                json.dump(dictionary, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"辞書保存エラー: {e}")
            return False
    
    def add_entry(self, category, term, definition, pronunciation=""):
        """辞書にエントリを追加"""
        if category not in self.dictionary["categories"]:
            self.dictionary["categories"][category] = {
                "description": f"{category}の用語",
                "entries": {}
            }
        
        self.dictionary["categories"][category]["entries"][term] = {
            "definition": definition,
            "pronunciation": pronunciation,
            "added_at": datetime.now().isoformat()
        }
        
        self.dictionary["metadata"]["last_updated"] = datetime.now().isoformat()
        self.dictionary["metadata"]["total_entries"] += 1
        
        return self.save_dictionary()
    
    def get_entry(self, category, term):
        """辞書からエントリを取得"""
        return self.dictionary["categories"].get(category, {}).get("entries", {}).get(term)
    
    def remove_entry(self, category, term):
        """辞書からエントリを削除"""
        if category in self.dictionary["categories"]:
            if term in self.dictionary["categories"][category]["entries"]:
                del self.dictionary["categories"][category]["entries"][term]
                self.dictionary["metadata"]["last_updated"] = datetime.now().isoformat()
                self.dictionary["metadata"]["total_entries"] -= 1
                return self.save_dictionary()
        return False

class CommandManager:
    """コマンド管理クラス"""
    
    def __init__(self):
        self.commands_file = "settings/commands.json"
        self.commands = self.load_commands()
    
    def load_commands(self):
        """コマンドを読み込み"""
        try:
            if os.path.exists(self.commands_file):
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                default_commands = {
                    "commands": {
                        "箇条書き": {
                            "description": "文字起こし結果を箇条書きに変換",
                            "llm_prompt": "以下の文字起こし結果を箇条書きに変換してください：\n\n{text}",
                            "output_format": "bullet_points",
                            "enabled": True
                        },
                        "要約": {
                            "description": "文字起こし結果を要約",
                            "llm_prompt": "以下の文字起こし結果を簡潔に要約してください：\n\n{text}",
                            "output_format": "summary",
                            "enabled": True
                        },
                        "テキストファイル出力": {
                            "description": "文字起こし結果をテキストファイルとして保存",
                            "llm_prompt": "以下の文字起こし結果を整理してテキストファイル用にフォーマットしてください：\n\n{text}",
                            "output_format": "text_file",
                            "enabled": True
                        }
                    },
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "total_commands": 3
                    }
                }
                self.save_commands(default_commands)
                return default_commands
        except Exception as e:
            st.error(f"コマンド読み込みエラー: {e}")
            return {"commands": {}, "metadata": {}}
    
    def save_commands(self, commands=None):
        """コマンドを保存"""
        if commands is None:
            commands = self.commands
        
        try:
            os.makedirs(os.path.dirname(self.commands_file), exist_ok=True)
            with open(self.commands_file, 'w', encoding='utf-8') as f:
                json.dump(commands, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"コマンド保存エラー: {e}")
            return False
    
    def add_command(self, name, description, llm_prompt, output_format, enabled=True):
        """コマンドを追加"""
        self.commands["commands"][name] = {
            "description": description,
            "llm_prompt": llm_prompt,
            "output_format": output_format,
            "enabled": enabled
        }
        
        self.commands["metadata"]["last_updated"] = datetime.now().isoformat()
        self.commands["metadata"]["total_commands"] += 1
        
        return self.save_commands()
    
    def get_command(self, name):
        """コマンドを取得"""
        return self.commands["commands"].get(name)
    
    def remove_command(self, name):
        """コマンドを削除"""
        if name in self.commands["commands"]:
            del self.commands["commands"][name]
            self.commands["metadata"]["last_updated"] = datetime.now().isoformat()
            self.commands["metadata"]["total_commands"] -= 1
            return self.save_commands()
        return False

class DeviceManager:
    """デバイス管理クラス（簡易版）"""
    
    def __init__(self):
        self.devices = self.get_available_devices()
    
    def get_available_devices(self):
        """利用可能なデバイスを取得（簡易版）"""
        # 実際のデバイス検出は複雑なため、簡易版を提供
        return [
            {"index": 0, "name": "デフォルトマイク", "channels": 1, "sample_rate": 44100},
            {"index": 1, "name": "ヘッドセット マイク", "channels": 1, "sample_rate": 44100},
            {"index": 2, "name": "内蔵マイク", "channels": 1, "sample_rate": 44100}
        ]
    
    def get_device_by_index(self, index):
        """インデックスでデバイスを取得"""
        for device in self.devices:
            if device["index"] == index:
                return device
        return None
    
    def get_device_by_name(self, name):
        """名前でデバイスを取得"""
        for device in self.devices:
            if device["name"] == name:
                return device
        return None

class TaskManager:
    """タスク管理クラス"""
    
    def __init__(self):
        self.tasks_file = "settings/tasks.json"
        self.ensure_settings_directory()
    
    def ensure_settings_directory(self):
        """設定ディレクトリの作成"""
        os.makedirs("settings", exist_ok=True)
    
    def load_tasks(self):
        """タスクを読み込み"""
        default_tasks = {
            "tasks": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_tasks": 0
            }
        }
        
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    loaded_tasks = json.load(f)
                    return self._merge_tasks(default_tasks, loaded_tasks)
            else:
                return default_tasks
        except Exception as e:
            st.error(f"タスク読み込みエラー: {str(e)}")
            return default_tasks
    
    def _merge_tasks(self, default_tasks, loaded_tasks):
        """タスクの統合"""
        merged = default_tasks.copy()
        if "tasks" in loaded_tasks:
            merged["tasks"] = loaded_tasks["tasks"]
        if "metadata" in loaded_tasks:
            merged["metadata"].update(loaded_tasks["metadata"])
        return merged
    
    def save_tasks(self, tasks=None):
        """タスクを保存"""
        if tasks is None:
            tasks = self.load_tasks()
        
        try:
            tasks["metadata"]["last_updated"] = datetime.now().isoformat()
            tasks["metadata"]["total_tasks"] = len(tasks["tasks"])
            
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"タスク保存エラー: {str(e)}")
            return False
    
    def add_task(self, title, description="", priority="medium", due_date=None, category="general", status="pending"):
        """タスクを追加"""
        tasks = self.load_tasks()
        
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "category": category,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        tasks["tasks"][task_id] = task
        return self.save_tasks(tasks)
    
    def update_task(self, task_id, **kwargs):
        """タスクを更新"""
        tasks = self.load_tasks()
        
        if task_id in tasks["tasks"]:
            tasks["tasks"][task_id].update(kwargs)
            tasks["tasks"][task_id]["updated_at"] = datetime.now().isoformat()
            return self.save_tasks(tasks)
        return False
    
    def delete_task(self, task_id):
        """タスクを削除"""
        tasks = self.load_tasks()
        
        if task_id in tasks["tasks"]:
            del tasks["tasks"][task_id]
            return self.save_tasks(tasks)
        return False
    
    def get_task(self, task_id):
        """タスクを取得"""
        tasks = self.load_tasks()
        return tasks["tasks"].get(task_id)
    
    def get_tasks_by_status(self, status="pending"):
        """ステータス別にタスクを取得"""
        tasks = self.load_tasks()
        return {k: v for k, v in tasks["tasks"].items() if v["status"] == status}
    
    def get_tasks_by_category(self, category):
        """カテゴリ別にタスクを取得"""
        tasks = self.load_tasks()
        return {k: v for k, v in tasks["tasks"].items() if v["category"] == category}

class CalendarManager:
    """カレンダー管理クラス"""
    
    def __init__(self):
        self.events_file = "settings/calendar.json"
        self.ensure_settings_directory()
    
    def ensure_settings_directory(self):
        """設定ディレクトリの作成"""
        os.makedirs("settings", exist_ok=True)
    
    def load_events(self):
        """イベントを読み込み"""
        default_events = {
            "events": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_events": 0
            }
        }
        
        try:
            if os.path.exists(self.events_file):
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    loaded_events = json.load(f)
                    return self._merge_events(default_events, loaded_events)
            else:
                return default_events
        except Exception as e:
            st.error(f"イベント読み込みエラー: {str(e)}")
            return default_events
    
    def _merge_events(self, default_events, loaded_events):
        """イベントの統合"""
        merged = default_events.copy()
        if "events" in loaded_events:
            merged["events"] = loaded_events["events"]
        if "metadata" in loaded_events:
            merged["metadata"].update(loaded_events["metadata"])
        return merged
    
    def save_events(self, events=None):
        """イベントを保存"""
        if events is None:
            events = self.load_events()
        
        try:
            events["metadata"]["last_updated"] = datetime.now().isoformat()
            events["metadata"]["total_events"] = len(events["events"])
            
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(events, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"イベント保存エラー: {str(e)}")
            return False
    
    def add_event(self, title, description="", start_date=None, end_date=None, all_day=False, category="general"):
        """イベントを追加"""
        events = self.load_events()
        
        event_id = str(uuid.uuid4())
        event = {
            "id": event_id,
            "title": title,
            "description": description,
            "start_date": start_date,
            "end_date": end_date,
            "all_day": all_day,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        events["events"][event_id] = event
        return self.save_events(events)
    
    def update_event(self, event_id, **kwargs):
        """イベントを更新"""
        events = self.load_events()
        
        if event_id in events["events"]:
            events["events"][event_id].update(kwargs)
            events["events"][event_id]["updated_at"] = datetime.now().isoformat()
            return self.save_events(events)
        return False
    
    def delete_event(self, event_id):
        """イベントを削除"""
        events = self.load_events()
        
        if event_id in events["events"]:
            del events["events"][event_id]
            return self.save_events(events)
        return False
    
    def get_event(self, event_id):
        """イベントを取得"""
        events = self.load_events()
        return events["events"].get(event_id)
    
    def get_events_by_date(self, target_date):
        """日付別にイベントを取得"""
        events = self.load_events()
        target_date_str = target_date.isoformat() if isinstance(target_date, date) else str(target_date)
        
        result = {}
        for event_id, event in events["events"].items():
            if event["start_date"] and event["start_date"].startswith(target_date_str):
                result[event_id] = event
        return result
    
    def get_events_by_category(self, category):
        """カテゴリ別にイベントを取得"""
        events = self.load_events()
        return {k: v for k, v in events["events"].items() if v["category"] == category}

class ShortcutManager:
    """ショートカットキー管理クラス"""
    
    def __init__(self):
        self.shortcuts = {
            "add_task": "Ctrl+T",
            "add_event": "Ctrl+E",
            "open_tasks": "Ctrl+Shift+T",
            "open_calendar": "Ctrl+Shift+E",
            "quick_transcribe": "F11",
            "save_transcription": "Ctrl+S"
        }
    
    def get_shortcut(self, action):
        """ショートカットキーを取得"""
        return self.shortcuts.get(action, "")
    
    def register_shortcut(self, action, key):
        """ショートカットキーを登録"""
        self.shortcuts[action] = key
    
    def handle_shortcut(self, action, callback):
        """ショートカットキーの処理"""
        # Streamlitでは直接的なキーボードイベント処理が制限されるため、
        # ボタンクリックと組み合わせて使用
        pass

class TaskAnalyzer:
    """タスク分析クラス"""
    
    def __init__(self, openai_client=None):
        self.openai_client = openai_client
    
    def analyze_text_for_tasks(self, text):
        """テキストからタスクを分析"""
        if not self.openai_client:
            return [], "OpenAI APIキーが設定されていません"
        
        try:
            prompt = f"""
以下のテキストからタスク（やるべきこと）を抽出してください。
タスクの形式で返してください：

テキスト：
{text}

抽出されたタスク（JSON形式）：
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたはタスク抽出の専門家です。テキストからタスクを抽出し、JSON形式で返してください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            return self._parse_task_result(result), None
            
        except Exception as e:
            return [], f"タスク分析エラー: {str(e)}"
    
    def _parse_task_result(self, result):
        """タスク結果を解析"""
        try:
            # JSON形式の結果を解析
            import re
            tasks = []
            
            # タスクのパターンを検索
            task_patterns = [
                r'["「](.+?)[」"]',  # 引用符で囲まれたタスク
                r'^[-•*]\s*(.+?)$',  # 箇条書きのタスク
                r'タスク[：:]\s*(.+?)$',  # タスク: 形式
            ]
            
            lines = result.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                for pattern in task_patterns:
                    match = re.search(pattern, line)
                    if match:
                        task_text = match.group(1).strip()
                        if task_text and len(task_text) > 3:
                            tasks.append({
                                "title": task_text,
                                "description": task_text,
                                "priority": "medium",
                                "category": "音声文字起こし"
                            })
                        break
            
            return tasks
            
        except Exception as e:
            st.error(f"タスク解析エラー: {str(e)}")
            return []
    
    def is_task_related(self, text):
        """テキストがタスク関連かどうかを判定"""
        task_keywords = [
            "やる", "する", "完了", "終了", "開始", "準備", "確認", "チェック",
            "予定", "スケジュール", "締切", "期限", "期限", "提出", "報告",
            "会議", "打ち合わせ", "ミーティング", "面談", "訪問", "出張",
            "買い物", "購入", "注文", "予約", "申し込み", "申請",
            "作成", "制作", "編集", "修正", "更新", "変更", "改善",
            "調査", "研究", "分析", "検討", "検証", "テスト"
        ]
        
        text_lower = text.lower()
        for keyword in task_keywords:
            if keyword in text_lower:
                return True
        return False

class EventAnalyzer:
    """イベント分析クラス"""
    
    def __init__(self, openai_client=None):
        self.openai_client = openai_client
    
    def analyze_text_for_events(self, text):
        """テキストからイベントを分析"""
        if not self.openai_client:
            return [], "OpenAI APIキーが設定されていません"
        
        try:
            prompt = f"""
以下のテキストからイベント（予定、スケジュール）を抽出してください。
イベントの形式で返してください：

テキスト：
{text}

抽出されたイベント（JSON形式）：
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたはイベント抽出の専門家です。テキストからイベントを抽出し、JSON形式で返してください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            return self._parse_event_result(result), None
            
        except Exception as e:
            return [], f"イベント分析エラー: {str(e)}"
    
    def _parse_event_result(self, result):
        """イベント結果を解析"""
        try:
            import re
            events = []
            
            # イベントのパターンを検索
            event_patterns = [
                r'["「](.+?)[」"]',  # 引用符で囲まれたイベント
                r'^[-•*]\s*(.+?)$',  # 箇条書きのイベント
                r'予定[：:]\s*(.+?)$',  # 予定: 形式
                r'会議[：:]\s*(.+?)$',  # 会議: 形式
            ]
            
            lines = result.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                for pattern in event_patterns:
                    match = re.search(pattern, line)
                    if match:
                        event_text = match.group(1).strip()
                        if event_text and len(event_text) > 3:
                            events.append({
                                "title": event_text,
                                "description": event_text,
                                "category": "音声文字起こし"
                            })
                        break
            
            return events
            
        except Exception as e:
            st.error(f"イベント解析エラー: {str(e)}")
            return []
    
    def is_event_related(self, text):
        """テキストがイベント関連かどうかを判定"""
        event_keywords = [
            "会議", "ミーティング", "打ち合わせ", "面談", "訪問", "出張",
            "予定", "スケジュール", "アポイント", "約束", "約束",
            "イベント", "セミナー", "研修", "講習", "講座", "ワークショップ",
            "パーティー", "飲み会", "食事会", "ランチ", "ディナー",
            "誕生日", "記念日", "祝日", "休日", "祝賀", "お祝い"
        ]
        
        text_lower = text.lower()
        for keyword in event_keywords:
            if keyword in text_lower:
                return True
        return False

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

def save_transcription_file(transcription_text, filename):
    """文字起こしファイルを保存"""
    try:
        os.makedirs("transcriptions", exist_ok=True)
        filepath = os.path.join("transcriptions", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(transcription_text)
        return True
    except Exception as e:
        st.error(f"文字起こし保存エラー: {e}")
        return False 