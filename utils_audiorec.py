"""
app_audiorec.py用の統合ユーティリティクラス
設定管理、デバイス管理、ユーザー辞書、コマンド処理などの機能を統合
"""

# 標準ライブラリ
import json
import os
import pickle
import tempfile
import uuid
import wave
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Union

# サードパーティライブラリ
import numpy as np
import openai
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ローカルインポート
from config_manager import get_secret, get_google_credentials, is_streamlit_cloud


class EnhancedSettingsManager:
    """拡張設定管理クラス"""
    
    def __init__(self) -> None:
        self.settings_file = "settings/app_settings.json"
        self.ensure_settings_directory()
    
    def ensure_settings_directory(self) -> None:
        """設定ディレクトリの作成"""
        os.makedirs("settings", exist_ok=True)
    
    def load_settings(self) -> Dict[str, Any]:
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
    
    def _merge_settings(self, default_settings: Dict[str, Any], loaded_settings: Dict[str, Any]) -> Dict[str, Any]:
        """設定をマージして不足しているキーを補完"""
        merged = default_settings.copy()
        
        for key, value in loaded_settings.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_settings(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
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
    
    def __init__(self) -> None:
        self.dictionary_file = "settings/user_dictionary.json"
        self.dictionary = self.load_dictionary()
    
    def load_dictionary(self) -> Dict[str, Any]:
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
    
    def save_dictionary(self, dictionary: Optional[Dict[str, Any]] = None) -> bool:
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
    
    def add_entry(self, category: str, term: str, definition: str, pronunciation: str = "") -> bool:
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
    
    def get_entry(self, category: str, term: str) -> Optional[Dict[str, Any]]:
        """辞書からエントリを取得"""
        return self.dictionary["categories"].get(category, {}).get("entries", {}).get(term)
    
    def remove_entry(self, category: str, term: str) -> bool:
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
    
    def __init__(self) -> None:
        self.commands_file = "settings/commands.json"
        self.commands = self.load_commands()
    
    def load_commands(self) -> Dict[str, Any]:
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
    
    def save_commands(self, commands: Optional[Dict[str, Any]] = None) -> bool:
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
    
    def add_command(self, name: str, description: str, llm_prompt: str, output_format: str, enabled: bool = True) -> bool:
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
    
    def get_command(self, name: str) -> Optional[Dict[str, Any]]:
        """コマンドを取得"""
        return self.commands["commands"].get(name)
    
    def remove_command(self, name: str) -> bool:
        """コマンドを削除"""
        if name in self.commands["commands"]:
            del self.commands["commands"][name]
            self.commands["metadata"]["last_updated"] = datetime.now().isoformat()
            self.commands["metadata"]["total_commands"] -= 1
            return self.save_commands()
        return False


class DeviceManager:
    """デバイス管理クラス（簡易版）"""
    
    def __init__(self) -> None:
        self.devices = self.get_available_devices()
    
    def get_available_devices(self) -> List[Dict[str, Any]]:
        """利用可能なデバイスを取得（簡易版）"""
        try:
            # pyaudioが利用可能な場合は実際のデバイスを検出
            import pyaudio
            p = pyaudio.PyAudio()
            devices = []
            
            for i in range(p.get_device_count()):
                try:
                    device_info = p.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:  # 入力デバイスのみ
                        devices.append({
                            "index": i,
                            "name": device_info['name'],
                            "channels": device_info['maxInputChannels'],
                            "sample_rate": int(device_info['defaultSampleRate'])
                        })
                except Exception:
                    continue
            
            p.terminate()
            return devices if devices else self._get_default_devices()
            
        except ImportError:
            # pyaudioが利用できない場合はデフォルトデバイスを返す
            return self._get_default_devices()
        except Exception:
            # その他のエラーの場合もデフォルトデバイスを返す
            return self._get_default_devices()
    
    def _get_default_devices(self) -> List[Dict[str, Any]]:
        """デフォルトデバイスリストを返す"""
        return [
            {"index": 0, "name": "デフォルトマイク", "channels": 1, "sample_rate": 44100},
            {"index": 1, "name": "ヘッドセット マイク", "channels": 1, "sample_rate": 44100},
            {"index": 2, "name": "内蔵マイク", "channels": 1, "sample_rate": 44100}
        ]
    
    def get_device_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """インデックスでデバイスを取得"""
        for device in self.devices:
            if device["index"] == index:
                return device
        return None
    
    def get_device_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """名前でデバイスを取得"""
        for device in self.devices:
            if device["name"] == name:
                return device
        return None


class TaskManager:
    """タスク管理クラス"""
    
    def __init__(self) -> None:
        self.tasks_file = "settings/tasks.json"
        self.ensure_settings_directory()
    
    def ensure_settings_directory(self) -> None:
        """設定ディレクトリの作成"""
        os.makedirs("settings", exist_ok=True)
    
    def load_tasks(self) -> Dict[str, Any]:
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
    
    def _merge_tasks(self, default_tasks: Dict[str, Any], loaded_tasks: Dict[str, Any]) -> Dict[str, Any]:
        """タスクの統合"""
        merged = default_tasks.copy()
        if "tasks" in loaded_tasks:
            merged["tasks"] = loaded_tasks["tasks"]
        if "metadata" in loaded_tasks:
            merged["metadata"].update(loaded_tasks["metadata"])
        return merged
    
    def save_tasks(self, tasks: Optional[Dict[str, Any]] = None) -> bool:
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
    
    def add_task(self, title: str, description: str = "", priority: str = "medium", 
                due_date: Optional[str] = None, category: str = "general", status: str = "pending") -> bool:
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
    
    def update_task(self, task_id: str, **kwargs: Any) -> bool:
        """タスクを更新"""
        tasks = self.load_tasks()
        
        if task_id in tasks["tasks"]:
            tasks["tasks"][task_id].update(kwargs)
            tasks["tasks"][task_id]["updated_at"] = datetime.now().isoformat()
            return self.save_tasks(tasks)
        return False
    
    def delete_task(self, task_id: str) -> bool:
        """タスクを削除"""
        tasks = self.load_tasks()
        
        if task_id in tasks["tasks"]:
            del tasks["tasks"][task_id]
            return self.save_tasks(tasks)
        return False
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """タスクを取得"""
        tasks = self.load_tasks()
        return tasks["tasks"].get(task_id)
    
    def get_tasks_by_status(self, status: str = "pending") -> Dict[str, Any]:
        """ステータス別にタスクを取得"""
        tasks = self.load_tasks()
        return {k: v for k, v in tasks["tasks"].items() if v["status"] == status}
    
    def get_tasks_by_category(self, category: str) -> Dict[str, Any]:
        """カテゴリ別にタスクを取得"""
        tasks = self.load_tasks()
        return {k: v for k, v in tasks["tasks"].items() if v["category"] == category}


class CalendarManager:
    """カレンダー管理クラス"""
    
    def __init__(self) -> None:
        self.events_file = "settings/calendar.json"
        self.ensure_settings_directory()
    
    def ensure_settings_directory(self) -> None:
        """設定ディレクトリの作成"""
        os.makedirs("settings", exist_ok=True)
    
    def load_events(self) -> Dict[str, Any]:
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
    
    def _merge_events(self, default_events: Dict[str, Any], loaded_events: Dict[str, Any]) -> Dict[str, Any]:
        """イベントの統合"""
        merged = default_events.copy()
        if "events" in loaded_events:
            merged["events"] = loaded_events["events"]
        if "metadata" in loaded_events:
            merged["metadata"].update(loaded_events["metadata"])
        return merged
    
    def save_events(self, events: Optional[Dict[str, Any]] = None) -> bool:
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
    
    def add_event(self, title: str, description: str = "", start_date: Optional[str] = None, 
                 end_date: Optional[str] = None, all_day: bool = False, category: str = "general") -> bool:
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
    
    def update_event(self, event_id: str, **kwargs: Any) -> bool:
        """イベントを更新"""
        events = self.load_events()
        
        if event_id in events["events"]:
            events["events"][event_id].update(kwargs)
            events["events"][event_id]["updated_at"] = datetime.now().isoformat()
            return self.save_events(events)
        return False
    
    def delete_event(self, event_id: str) -> bool:
        """イベントを削除"""
        events = self.load_events()
        
        if event_id in events["events"]:
            del events["events"][event_id]
            return self.save_events(events)
        return False
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """イベントを取得"""
        events = self.load_events()
        return events["events"].get(event_id)
    
    def get_events_by_date(self, target_date: Union[date, str]) -> Dict[str, Any]:
        """日付別にイベントを取得"""
        events = self.load_events()
        target_date_str = target_date.isoformat() if isinstance(target_date, date) else str(target_date)
        
        result = {}
        for event_id, event in events["events"].items():
            if event["start_date"] and event["start_date"].startswith(target_date_str):
                result[event_id] = event
        return result
    
    def get_events_by_category(self, category: str) -> Dict[str, Any]:
        """カテゴリ別にイベントを取得"""
        events = self.load_events()
        return {k: v for k, v in events["events"].items() if v["category"] == category}


class ShortcutManager:
    """ショートカットキー管理クラス"""
    
    def __init__(self) -> None:
        self.shortcuts = {
            "add_task": "Ctrl+T",
            "add_event": "Ctrl+E",
            "open_tasks": "Ctrl+Shift+T",
            "open_calendar": "Ctrl+Shift+E",
            "quick_transcribe": "F11",
            "save_transcription": "Ctrl+S"
        }
    
    def get_shortcut(self, action: str) -> str:
        """ショートカットキーを取得"""
        return self.shortcuts.get(action, "")
    
    def register_shortcut(self, action: str, key: str) -> None:
        """ショートカットキーを登録"""
        self.shortcuts[action] = key
    
    def handle_shortcut(self, action: str, callback) -> None:
        """ショートカットキーの処理"""
        # Streamlitでは直接的なキーボードイベント処理が制限されるため、
        # ボタンクリックと組み合わせて使用
        pass


class TaskAnalyzer:
    """タスク分析クラス"""
    
    def __init__(self, openai_client: Optional[openai.OpenAI] = None) -> None:
        self.openai_client = openai_client
    
    def analyze_text_for_tasks(self, text: str) -> tuple[List[Dict[str, Any]], Optional[str]]:
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
    
    def _parse_task_result(self, result: str) -> List[Dict[str, Any]]:
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
    
    def is_task_related(self, text: str) -> bool:
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
    
    def __init__(self, openai_client: Optional[openai.OpenAI] = None) -> None:
        self.openai_client = openai_client
    
    def analyze_text_for_events(self, text: str) -> tuple[List[Dict[str, Any]], Optional[str]]:
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
    
    def _parse_event_result(self, result: str) -> List[Dict[str, Any]]:
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
    
    def is_event_related(self, text: str) -> bool:
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


class GoogleCalendarManager:
    """GoogleカレンダーとのStreamlit対応連携クラス"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.pickle'
    
    def __init__(self) -> None:
        self.service = None
        self.credentials: Optional[Credentials] = None
        self._initialize_session_state()
    
    def _initialize_session_state(self) -> None:
        """Streamlitセッション状態の初期化"""
        if 'google_auth_flow' not in st.session_state:
            st.session_state.google_auth_flow = None
        if 'google_credentials' not in st.session_state:
            st.session_state.google_credentials = None
    
    def authenticate(self) -> bool:
        """Google認証を実行（Streamlit対応）"""
        try:
            # セッション状態から認証情報を復元
            if st.session_state.google_credentials:
                self.credentials = st.session_state.google_credentials
                if self._is_credentials_valid():
                    self.service = build('calendar', 'v3', credentials=self.credentials)
                    return True
            
            # 環境変数またはStreamlit Secretsから認証情報を取得
            client_id, client_secret, _ = get_google_credentials()
            
            if client_id and client_secret:
                creds = self._create_credentials_from_env(client_id, client_secret)
            else:
                creds = self._authenticate_from_file()
            
            if not creds:
                return False
                
            self.credentials = creds
            st.session_state.google_credentials = creds
            self.service = build('calendar', 'v3', credentials=creds)
            return True
            
        except Exception as e:
            st.error(f"認証エラー: {str(e)}")
            return False
    
    def _is_credentials_valid(self) -> bool:
        """認証情報の有効性を確認"""
        if not self.credentials:
            return False
        
        if self.credentials.expired:
            if self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    return True
                except Exception:
                    return False
            return False
        
        return True
    
    def _create_credentials_from_env(self, client_id: str, client_secret: str) -> Optional[Credentials]:
        """環境変数またはStreamlit Secretsから認証情報を作成"""
        try:
            refresh_token = get_secret('GOOGLE_REFRESH_TOKEN')
            
            if not refresh_token:
                st.warning("⚠️ GOOGLE_REFRESH_TOKENが設定されていません。初回認証が必要です。")
                return self._handle_initial_auth(client_id, client_secret)
            
            # 既存の認証情報から復元
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=self.SCOPES
            )
            
            # トークンをリフレッシュ
            if creds.expired:
                creds.refresh(Request())
            
            return creds
        except Exception as e:
            st.error(f"環境変数からの認証情報作成に失敗しました: {e}")
            return None
    
    def _handle_initial_auth(self, client_id: str, client_secret: str) -> Optional[Credentials]:
        """初回認証の処理（Streamlit対応）"""
        st.warning("⚠️ 初回認証が必要です。以下の手順に従ってください：")
        
        # 認証URLを生成
        try:
            client_config = {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
                }
            }
            
            flow = Flow.from_client_config(
                client_config,
                scopes=self.SCOPES,
                redirect_uri="urn:ietf:wg:oauth:2.0:oob"
            )
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            st.info("📋 認証手順:")
            st.markdown(f"1. [この認証URL]({auth_url})をクリック")
            st.markdown("2. Googleアカウントでログインし、権限を許可")
            st.markdown("3. 表示された認証コードを下のフィールドに入力")
            
            # 認証コード入力
            auth_code = st.text_input("認証コードを入力してください:", key="google_auth_code")
            
            if auth_code and st.button("認証を完了", key="complete_google_auth"):
                try:
                    flow.fetch_token(code=auth_code)
                    creds = flow.credentials
                    
                    # リフレッシュトークンを表示（ユーザーが環境変数に設定するため）
                    if creds.refresh_token:
                        st.success("✅ 認証が完了しました！")
                        st.info("以下のリフレッシュトークンを.envファイルのGOOGLE_REFRESH_TOKENに設定してください:")
                        st.code(creds.refresh_token)
                        
                        # セッション状態に保存
                        st.session_state.google_credentials = creds
                        return creds
                    else:
                        st.error("❌ リフレッシュトークンの取得に失敗しました")
                        
                except Exception as e:
                    st.error(f"❌ 認証コードの処理に失敗しました: {e}")
            
            return None
            
        except Exception as e:
            st.error(f"認証フローの初期化に失敗しました: {e}")
            return None
    
    def _authenticate_from_file(self) -> Optional[Credentials]:
        """ファイルベースの認証（開発用・Streamlit非対応）"""
        st.warning("⚠️ ファイルベース認証はStreamlit環境では制限があります。")
        st.info("環境変数による認証を推奨します。setup_google_auth.pyを実行してください。")
        
        # 既存のトークンファイルがあるかチェック
        if os.path.exists(self.TOKEN_FILE):
            try:
                with open(self.TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
                
                if creds and self._is_credentials_valid():
                    return creds
            except Exception as e:
                st.error(f"トークンファイルの読み込みに失敗しました: {e}")
        
        # credentials.jsonファイルの確認
        if not os.path.exists(self.CREDENTIALS_FILE):
            st.error("❌ credentials.jsonファイルが見つかりません")
            st.info("setup_google_auth.pyを実行して認証を設定してください")
            return None
        
        st.error("❌ ファイルベース認証はStreamlit環境では完全にサポートされていません")
        st.info("💡 解決方法: 環境変数による認証を使用してください")
        return None
    
    def get_authentication_status(self) -> str:
        """認証状態を確認"""
        if not self.credentials:
            return "未認証"
        
        if self.credentials.expired:
            return "認証期限切れ"
        
        return "認証済み"
    
    def setup_web_authentication(self) -> None:
        """Streamlit用の認証設定を表示"""
        st.subheader("🔐 Googleカレンダー認証設定")
        
        # 現在の認証状態を表示
        auth_status = self.get_authentication_status()
        if auth_status == "認証済み":
            st.success(f"✅ {auth_status}")
        else:
            st.warning(f"⚠️ {auth_status}")
        
        # 認証方法の説明
        st.info("📋 認証設定手順:")
        
        with st.expander("🔧 環境変数による認証設定（推奨）"):
            st.markdown("""
            **手順:**
            1. Google Cloud Consoleでプロジェクトを作成
            2. Google Calendar APIを有効化
            3. OAuth 2.0認証情報を作成
            4. 以下の環境変数を設定:
            """)
            
            st.code("""
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REFRESH_TOKEN=your_refresh_token  # 初回認証後に取得
            """)
            
            st.markdown("5. `setup_google_auth.py`を実行して設定を完了")
        
        # 環境変数またはStreamlit Secretsの確認
        client_id, client_secret, refresh_token = get_google_credentials()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if client_id:
                st.success("✅ CLIENT_ID")
            else:
                st.error("❌ CLIENT_ID")
        
        with col2:
            if client_secret:
                st.success("✅ CLIENT_SECRET")
            else:
                st.error("❌ CLIENT_SECRET")
        
        with col3:
            if refresh_token:
                st.success("✅ REFRESH_TOKEN")
            else:
                st.warning("⚠️ REFRESH_TOKEN")
        
        # 認証実行
        if client_id and client_secret:
            if st.button("🔄 認証を実行", key="execute_google_auth"):
                with st.spinner("認証中..."):
                    if self.authenticate():
                        st.success("✅ 認証が完了しました")
                        st.rerun()
                    else:
                        st.error("❌ 認証に失敗しました")
        else:
            st.warning("⚠️ 環境変数を設定してください")
            if st.button("🔧 設定スクリプトを実行", key="run_setup_script"):
                st.info("ターミナルで `python setup_google_auth.py` を実行してください")
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """利用可能なカレンダーリストを取得"""
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            calendar_list = self.service.calendarList().list().execute()
            return calendar_list.get('items', [])
        except HttpError as e:
            st.error(f"カレンダーリストの取得に失敗しました: {e}")
            return []
        except Exception as e:
            st.error(f"予期しないエラー: {e}")
            return []
    
    def get_events(self, calendar_id: str = 'primary', max_results: int = 10) -> List[Dict[str, Any]]:
        """指定したカレンダーからイベントを取得"""
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except HttpError as e:
            st.error(f"イベントの取得に失敗しました: {e}")
            return []
        except Exception as e:
            st.error(f"予期しないエラー: {e}")
            return []
    
    def create_event(self, event_data: Dict[str, Any], calendar_id: str = 'primary') -> Optional[Dict[str, Any]]:
        """新しいイベントを作成"""
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            event = {
                'summary': event_data['title'],
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': event_data['start_date'],
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': event_data['end_date'],
                    'timeZone': 'Asia/Tokyo',
                }
            }
            
            if event_data.get('all_day', False):
                event['start'] = {'date': event_data['start_date'][:10]}
                event['end'] = {'date': event_data['end_date'][:10]}
            
            created_event = self.service.events().insert(
                calendarId=calendar_id, body=event).execute()
            
            st.success(f"イベント「{event_data['title']}」を作成しました")
            return created_event
            
        except HttpError as e:
            st.error(f"イベントの作成に失敗しました: {e}")
            return None
        except Exception as e:
            st.error(f"予期しないエラー: {e}")
            return None
    
    def update_event(self, event_id: str, event_data: Dict[str, Any], calendar_id: str = 'primary') -> Optional[Dict[str, Any]]:
        """イベントを更新"""
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            event = {
                'summary': event_data['title'],
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': event_data['start_date'],
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': event_data['end_date'],
                    'timeZone': 'Asia/Tokyo',
                }
            }
            
            if event_data.get('all_day', False):
                event['start'] = {'date': event_data['start_date'][:10]}
                event['end'] = {'date': event_data['end_date'][:10]}
            
            updated_event = self.service.events().update(
                calendarId=calendar_id, eventId=event_id, body=event
            ).execute()
            
            return updated_event
        except HttpError as e:
            st.error(f"イベントの更新に失敗しました: {e}")
            return None
        except Exception as e:
            st.error(f"予期しないエラー: {e}")
            return None
    
    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> bool:
        """イベントを削除"""
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            self.service.events().delete(
                calendarId=calendar_id, eventId=event_id
            ).execute()
            return True
        except HttpError as e:
            st.error(f"イベントの削除に失敗しました: {e}")
            return False
        except Exception as e:
            st.error(f"予期しないエラー: {e}")
            return False
    
    def sync_local_to_google(self, local_events: List[Dict[str, Any]], calendar_id: str = 'primary') -> bool:
        """ローカルイベントをGoogleカレンダーに同期"""
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            synced_count = 0
            for event in local_events:
                if not event.get('google_id'):  # まだGoogleカレンダーに同期されていない
                    google_event = self.create_event(event, calendar_id)
                    if google_event:
                        event['google_id'] = google_event['id']
                        synced_count += 1
            
            st.success(f"{synced_count}件のイベントをGoogleカレンダーに同期しました。")
            return True
        except Exception as e:
            st.error(f"同期に失敗しました: {e}")
            return False
    
    def sync_google_to_local(self, calendar_id: str = 'primary') -> List[Dict[str, Any]]:
        """Googleカレンダーからローカルに同期"""
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            google_events = self.get_events(calendar_id, max_results=50)
            local_events = []
            
            for event in google_events:
                local_event = {
                    'id': str(uuid.uuid4()),
                    'title': event.get('summary', '無題'),
                    'description': event.get('description', ''),
                    'start_date': event['start'].get('dateTime', event['start'].get('date')),
                    'end_date': event['end'].get('dateTime', event['end'].get('date')),
                    'all_day': 'date' in event['start'],
                    'category': 'Google同期',
                    'google_id': event['id']
                }
                local_events.append(local_event)
            
            return local_events
        except Exception as e:
            st.error(f"Googleカレンダーからの同期に失敗しました: {e}")
            return []


def save_audio_file(audio_data: bytes, filename: str) -> bool:
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


def save_transcription_file(transcription_text: str, filename: str) -> bool:
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
