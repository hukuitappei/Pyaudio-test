"""
app_audiorec.py用の統合ユーティリティクラス
設定管理、デバイス管理、ユーザー辞書、コマンド処理などの機能を統合
"""

# 標準ライブラリ
import json
import os
import pickle
import sys
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple

# サードパーティライブラリ
import streamlit as st
import numpy as np

# Google認証ライブラリ
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    # フォールバック用のダミークラス
    class Credentials:
        def __init__(self, *args, **kwargs):
            pass
        @property
        def expired(self):
            return True
        def refresh(self, request):
            pass
    class Request:
        pass
    class Flow:
        def __init__(self, *args, **kwargs):
            pass
        def authorization_url(self, *args, **kwargs):
            return "http://example.com", None
        def fetch_token(self, *args, **kwargs):
            pass
    class build:
        def __init__(self, *args, **kwargs):
            pass

# OpenAIライブラリ
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    # フォールバック用のダミークラス
    class OpenAI:
        def __init__(self, *args, **kwargs):
            pass
    openai = type('openai', (), {'OpenAI': OpenAI})()

# PyAudioの代替実装
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    # Streamlit Cloud環境でのフォールバック
    class PyAudio:
        def __init__(self):
            pass
        def get_device_count(self):
            return 0
        def get_device_info_by_index(self, index):
            return {'name': f'Device {index}', 'maxInputChannels': 1, 'defaultSampleRate': 44100}
        def open(self, *args, **kwargs):
            raise RuntimeError("PyAudio is not available in this environment")
    
    pyaudio = PyAudio()

# 音声処理ライブラリ（Python 3.13対応版）
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# 代替音声処理ライブラリ（Python 3.13対応）
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

try:
    from scipy import signal
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


# ローカルインポート
try:
    from config.config_manager import get_secret, get_google_credentials, is_streamlit_cloud
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    # Streamlit Cloud環境でのフォールバック
    CONFIG_MANAGER_AVAILABLE = False
    def get_secret(key: str, default=None):
        """フォールバック用の設定取得関数"""
        import os
        import streamlit as st
        # 環境変数を優先
        value = os.getenv(key)
        if value:
            return value
        # Streamlit Secretsを確認
        try:
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except Exception:
            pass
        return default
    
    # フォールバック用の関数は削除（config_managerから正しくインポート）


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
    """デバイス管理クラス"""
    
    def __init__(self) -> None:
        # PyAudioの初期化を条件付きで実行
        if PYAUDIO_AVAILABLE:
            try:
                self.pa = pyaudio.PyAudio()
            except Exception as e:
                st.warning(f"PyAudioの初期化に失敗しました: {e}")
                self.pa = None
        else:
            self.pa = None
    
    def get_available_devices(self) -> List[Dict[str, Any]]:
        """利用可能な録音デバイスを取得"""
        devices = []
        
        if not PYAUDIO_AVAILABLE or self.pa is None:
            # Streamlit Cloud環境でのフォールバック
            devices.append({
                'index': 0,
                'name': 'Streamlit Cloud Audio (streamlit-audiorec)',
                'channels': 1,
                'sample_rate': 44100,
                'max_input_channels': 1,
                'description': 'streamlit-audiorecコンポーネントを使用'
            })
            return devices
        
        try:
            device_count = self.pa.get_device_count()
            for i in range(device_count):
                try:
                    device_info = self.pa.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        devices.append({
                            'index': i,
                            'name': device_info['name'],
                            'channels': device_info['maxInputChannels'],
                            'sample_rate': int(device_info['defaultSampleRate']),
                            'max_input_channels': device_info['maxInputChannels']
                        })
                except Exception as e:
                    st.warning(f"デバイス {i} の情報取得に失敗: {e}")
                    continue
        except Exception as e:
            st.error(f"デバイス情報の取得に失敗: {e}")
        
        return devices
    
    def get_device_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """指定されたインデックスのデバイス情報を取得"""
        devices = self.get_available_devices()
        for device in devices:
            if device['index'] == index:
                return device
        return None
    
    def get_current_device_info(self) -> Optional[Dict[str, Any]]:
        """現在のデバイス情報を取得"""
        if not PYAUDIO_AVAILABLE or self.pa is None:
            return {
                'name': 'Streamlit Cloud Audio (streamlit-audiorec)',
                'channels': 1,
                'sample_rate': 44100,
                'description': 'streamlit-audiorecコンポーネントを使用'
            }
        
        try:
            # デフォルトデバイスの情報を取得
            default_device = self.pa.get_default_input_device_info()
            return {
                'name': default_device['name'],
                'channels': default_device['maxInputChannels'],
                'sample_rate': int(default_device['defaultSampleRate']),
                'description': 'ローカル環境のデフォルトデバイス'
            }
        except Exception as e:
            st.warning(f"デフォルトデバイス情報の取得に失敗: {e}")
            return None
    
    def test_device(self, device_index: int) -> bool:
        """デバイスのテスト"""
        if not PYAUDIO_AVAILABLE or self.pa is None:
            st.info("Streamlit Cloud環境ではデバイステストは利用できません")
            st.info("💡 streamlit-audiorecコンポーネントを使用してください")
            return True
        
        try:
            device_info = self.pa.get_device_info_by_index(device_index)
            st.success(f"デバイステスト成功: {device_info['name']}")
            return True
        except Exception as e:
            st.error(f"デバイステスト失敗: {e}")
            return False
    
    def __del__(self):
        """デストラクタ"""
        if PYAUDIO_AVAILABLE and self.pa is not None:
            try:
                self.pa.terminate()
            except:
                pass


class TaskManager:
    """タスク管理クラス"""
    
    def __init__(self) -> None:
        self.tasks_file = "settings/tasks.json"
        self.ensure_tasks_directory()
        self.auth_manager = get_google_auth_manager()
    
    def ensure_tasks_directory(self) -> None:
        """タスクディレクトリの作成"""
        os.makedirs("settings", exist_ok=True)
    
    def load_tasks(self) -> Dict[str, Any]:
        """タスクを読み込み"""
        default_tasks = {
            "tasks": {},
            "categories": ["仕事", "プライベート", "勉強", "健康", "その他"],
            "priorities": ["低", "中", "高", "緊急"]
        }
        
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.save_tasks(default_tasks)
                return default_tasks
        except Exception as e:
            st.error(f"タスク読み込みエラー: {e}")
            return default_tasks
    
    def save_tasks(self, tasks: Dict[str, Any]) -> bool:
        """タスクを保存"""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"タスク保存エラー: {e}")
            return False
    
    def add_task(self, title: str, description: str = "", priority: str = "中", 
                 due_date: Optional[str] = None, category: str = "その他") -> bool:
        """タスクを追加"""
        try:
            tasks = self.load_tasks()
            task_id = str(uuid.uuid4())
            
            task = {
                "id": task_id,
                "title": title,
                "description": description,
                "priority": priority,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "due_date": due_date,
                "category": category,
                "google_event_id": None
            }
            
            tasks["tasks"][task_id] = task
            return self.save_tasks(tasks)
        except Exception as e:
            st.error(f"タスク追加エラー: {e}")
            return False
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """タスクを更新"""
        try:
            tasks = self.load_tasks()
            if task_id in tasks["tasks"]:
                tasks["tasks"][task_id].update(kwargs)
                return self.save_tasks(tasks)
            return False
        except Exception as e:
            st.error(f"タスク更新エラー: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """タスクを削除"""
        try:
            tasks = self.load_tasks()
            if task_id in tasks["tasks"]:
                # Googleカレンダーからも削除
                task = tasks["tasks"][task_id]
                if task.get('google_event_id'):
                    self.auth_manager.get_service().events().delete(
                        calendarId='primary', 
                        eventId=task['google_event_id']
                    ).execute()
                
                del tasks["tasks"][task_id]
                return self.save_tasks(tasks)
            return False
        except Exception as e:
            st.error(f"タスク削除エラー: {e}")
            return False
    
    def sync_to_google_calendar(self, task_id: str) -> bool:
        """タスクをGoogleカレンダーに同期"""
        try:
            tasks = self.load_tasks()
            if task_id not in tasks["tasks"]:
                return False
            
            task = tasks["tasks"][task_id]
            if task.get('google_event_id'):
                st.info("既にGoogleカレンダーに同期済みです")
                return True
            
            service = self.auth_manager.get_service()
            if not service:
                st.error("Googleカレンダーが認証されていません")
                return False
            
            event = {
                'summary': task['title'],
                'description': task['description'],
                'start': {
                    'dateTime': task['due_date'] or datetime.now().isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': task['due_date'] or (datetime.now() + timedelta(hours=1)).isoformat(),
                    'timeZone': 'Asia/Tokyo',
                }
            }
            
            created_event = service.events().insert(
                calendarId='primary', body=event
            ).execute()
            
            # タスクにGoogleイベントIDを保存
            task['google_event_id'] = created_event['id']
            self.save_tasks(tasks)
            
            st.success("Googleカレンダーに同期しました")
            return True
            
        except Exception as e:
            st.error(f"Googleカレンダー同期エラー: {e}")
            return False


class CalendarManager:
    """カレンダー管理クラス"""
    
    def __init__(self) -> None:
        self.calendar_file = "settings/calendar.json"
        self.ensure_calendar_directory()
        self.auth_manager = get_google_auth_manager()
    
    def ensure_calendar_directory(self) -> None:
        """カレンダーディレクトリの作成"""
        os.makedirs("settings", exist_ok=True)
    
    def load_events(self) -> Dict[str, Any]:
        """イベントを読み込み"""
        default_events = {
            "events": {},
            "categories": ["会議", "予定", "イベント", "その他"]
        }
        
        try:
            if os.path.exists(self.calendar_file):
                with open(self.calendar_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.save_events(default_events)
                return default_events
        except Exception as e:
            st.error(f"イベント読み込みエラー: {e}")
            return default_events
    
    def save_events(self, events: Dict[str, Any]) -> bool:
        """イベントを保存"""
        try:
            with open(self.calendar_file, 'w', encoding='utf-8') as f:
                json.dump(events, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"イベント保存エラー: {e}")
            return False
    
    def add_event(self, title: str, description: str = "", 
                  start_date: str = None, end_date: str = None,
                  all_day: bool = False, category: str = "その他") -> bool:
        """イベントを追加"""
        try:
            events = self.load_events()
            event_id = str(uuid.uuid4())
            
            if not start_date:
                start_date = datetime.now().isoformat()
            if not end_date:
                end_date = (datetime.now() + timedelta(hours=1)).isoformat()
            
            event = {
                "id": event_id,
                "title": title,
                "description": description,
                "start_date": start_date,
                "end_date": end_date,
                "all_day": all_day,
                "category": category,
                "created_at": datetime.now().isoformat(),
                "google_event_id": None
            }
            
            events["events"][event_id] = event
            return self.save_events(events)
        except Exception as e:
            st.error(f"イベント追加エラー: {e}")
            return False
    
    def update_event(self, event_id: str, **kwargs) -> bool:
        """イベントを更新"""
        try:
            events = self.load_events()
            if event_id in events["events"]:
                events["events"][event_id].update(kwargs)
                return self.save_events(events)
            return False
        except Exception as e:
            st.error(f"イベント更新エラー: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """イベントを削除"""
        try:
            events = self.load_events()
            if event_id in events["events"]:
                # Googleカレンダーからも削除
                event = events["events"][event_id]
                if event.get('google_event_id'):
                    self.auth_manager.get_service().events().delete(
                        calendarId='primary', 
                        eventId=event['google_event_id']
                    ).execute()
                
                del events["events"][event_id]
                return self.save_events(events)
            return False
        except Exception as e:
            st.error(f"イベント削除エラー: {e}")
            return False
    
    def sync_to_google_calendar(self, event_id: str) -> bool:
        """イベントをGoogleカレンダーに同期"""
        try:
            events = self.load_events()
            if event_id not in events["events"]:
                return False
            
            event = events["events"][event_id]
            if event.get('google_event_id'):
                st.info("既にGoogleカレンダーに同期済みです")
                return True
            
            service = self.auth_manager.get_service()
            if not service:
                st.error("Googleカレンダーが認証されていません")
                return False
            
            google_event = {
                'summary': event['title'],
                'description': event['description'],
                'start': {
                    'dateTime': event['start_date'],
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': event['end_date'],
                    'timeZone': 'Asia/Tokyo',
                }
            }
            
            if event.get('all_day', False):
                google_event['start'] = {'date': event['start_date'][:10]}
                google_event['end'] = {'date': event['end_date'][:10]}
            
            created_event = service.events().insert(
                calendarId='primary', body=google_event
            ).execute()
            
            # イベントにGoogleイベントIDを保存
            event['google_event_id'] = created_event['id']
            self.save_events(events)
            
            st.success("Googleカレンダーに同期しました")
            return True
            
        except Exception as e:
            st.error(f"Googleカレンダー同期エラー: {e}")
            return False


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
    
    def __init__(self, openai_client=None) -> None:
        self.openai_client = openai_client
    
    def analyze_text(self, text: str) -> List[Dict[str, Any]]:
        """テキストからタスクを分析"""
        if not self.openai_client:
            return [], "OpenAI APIキーが設定されていません"
        
        try:
            prompt = f"""
            以下のテキストからタスクを抽出してください。
            各タスクについて、以下の情報を提供してください：
            - title: タスクのタイトル
            - description: タスクの詳細説明
            - priority: 優先度（低、中、高、緊急）
            - due_date: 期限（YYYY-MM-DD形式、不明な場合はnull）
            - category: カテゴリ（仕事、プライベート、勉強、健康、その他）
            
            テキスト: {text}
            
            JSON形式で回答してください。
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            # JSON解析の実装
            return self._parse_tasks(result)
            
        except Exception as e:
            return [], f"タスク分析エラー: {str(e)}"
    
    def _parse_tasks(self, result: str) -> List[Dict[str, Any]]:
        """タスク解析結果をパース"""
        try:
            import json
            tasks = json.loads(result)
            return tasks if isinstance(tasks, list) else []
        except:
            return []


class EventAnalyzer:
    """イベント分析クラス"""
    
    def __init__(self, openai_client=None) -> None:
        self.openai_client = openai_client
    
    def analyze_text(self, text: str) -> List[Dict[str, Any]]:
        """テキストからイベントを分析"""
        if not self.openai_client:
            return [], "OpenAI APIキーが設定されていません"
        
        try:
            prompt = f"""
            以下のテキストからイベントを抽出してください。
            各イベントについて、以下の情報を提供してください：
            - title: イベントのタイトル
            - description: イベントの詳細説明
            - start_date: 開始日時（YYYY-MM-DD HH:MM形式、不明な場合はnull）
            - end_date: 終了日時（YYYY-MM-DD HH:MM形式、不明な場合はnull）
            - category: カテゴリ（会議、予定、イベント、その他）
            - all_day: 終日イベントかどうか（true/false）
            
            テキスト: {text}
            
            JSON形式で回答してください。
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            # JSON解析の実装
            return self._parse_events(result)
            
        except Exception as e:
            return [], f"イベント分析エラー: {str(e)}"
    
    def _parse_events(self, result: str) -> List[Dict[str, Any]]:
        """イベント解析結果をパース"""
        try:
            import json
            events = json.loads(result)
            return events if isinstance(events, list) else []
        except:
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


class GoogleAuthManager:
    """Google認証の統合管理クラス"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.pickle'
    
    def __init__(self) -> None:
        self.service = None
        self.credentials: Optional[Credentials] = None
        
        # Google認証ライブラリが利用できない場合の処理
        if not GOOGLE_AUTH_AVAILABLE:
            st.warning("⚠️ Google認証ライブラリが利用できません。Google認証機能は無効化されます。")
            return
        
        self._initialize_session_state()
    
    def _initialize_session_state(self) -> None:
        """Streamlitセッション状態の初期化"""
        if 'google_auth_flow' not in st.session_state:
            st.session_state.google_auth_flow = None
        if 'google_credentials' not in st.session_state:
            st.session_state.google_credentials = None
        if 'google_auth_url' not in st.session_state:
            st.session_state.google_auth_url = None
        if 'google_auth_key' not in st.session_state:
            st.session_state.google_auth_key = None
        if 'google_auth_status' not in st.session_state:
            st.session_state.google_auth_status = False
    
    def authenticate(self) -> bool:
        """Google認証を実行（Streamlit対応）"""
        if not GOOGLE_AUTH_AVAILABLE:
            st.error("❌ Google認証ライブラリが利用できません")
            return False
        
        try:
            # セッション状態の初期化
            self._initialize_session_state()
            
            # 既に認証済みの場合は復元
            if st.session_state.google_auth_status and st.session_state.google_credentials:
                self.credentials = st.session_state.google_credentials
                if self._is_credentials_valid():
                    self.service = build('calendar', 'v3', credentials=self.credentials)
                    return True
            
            # 環境変数またはStreamlit Secretsから認証情報を取得
            credentials = get_google_credentials()
            if credentials is None:
                st.error("Google認証情報が取得できませんでした")
                return False
            
            client_id, client_secret, _ = credentials
            
            if client_id and client_secret:
                creds = self._create_credentials_from_env(client_id, client_secret)
            else:
                creds = self._authenticate_from_file()
            
            if not creds:
                return False
                
            self.credentials = creds
            st.session_state.google_credentials = creds
            st.session_state.google_auth_status = True
            self.service = build('calendar', 'v3', credentials=creds)
            return True
            
        except Exception as e:
            st.error(f"認証エラー: {str(e)}")
            return False
    
    def _is_credentials_valid(self) -> bool:
        """認証情報の有効性を確認"""
        if not GOOGLE_AUTH_AVAILABLE:
            return False
        
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
        if not GOOGLE_AUTH_AVAILABLE:
            st.error("❌ Google認証ライブラリが利用できません")
            return None
        
        try:
            # 1. config_managerを使用（推奨）
            refresh_token = get_secret('GOOGLE_REFRESH_TOKEN')
            
            # 2. フォールバック: st.secretsを直接使用
            if not refresh_token:
                try:
                    if hasattr(st, 'secrets') and st.secrets is not None:
                        refresh_token = st.secrets.get('GOOGLE_REFRESH_TOKEN')
                except Exception as e:
                    st.warning(f"Streamlit Secretsの読み込みエラー: {e}")
            
            # 3. フォールバック: 環境変数
            if not refresh_token:
                refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
            
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
        if not GOOGLE_AUTH_AVAILABLE:
            st.error("❌ Google認証ライブラリが利用できません")
            return None
        
        st.warning("⚠️ 初回認証が必要です。以下の手順に従ってください：")
        
        # セッション状態の初期化
        self._initialize_session_state()
        
        # セッション状態で認証フローを管理
        if 'google_auth_flow' not in st.session_state:
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
                
                # セッション状態に保存
                st.session_state.google_auth_flow = flow
                st.session_state.google_auth_url = auth_url
                st.session_state.google_auth_key = uuid.uuid4().hex[:8]
                
            except Exception as e:
                st.error(f"認証フローの初期化に失敗しました: {e}")
                return None
        
        # 認証URLの表示
        st.info("📋 認証手順:")
        st.markdown("1. 以下の認証URLをクリックしてGoogle認証画面を開いてください:")
        st.markdown(f"**認証URL**: {st.session_state.google_auth_url}")
        st.markdown("2. Googleアカウントでログインし、権限を許可してください")
        st.markdown("3. 表示された認証コードを下のフィールドに入力してください")
        
        # 認証URLをクリック可能なボタンとして表示
        if st.button("🔗 Google認証画面を開く", key=f"open_auth_url_{st.session_state.google_auth_key}"):
            st.markdown(f"[Google認証画面を開く]({st.session_state.google_auth_url})")
        
        # 認証フローをリセットするボタン
        if st.button("🔄 認証フローをリセット", key=f"reset_auth_flow_{st.session_state.google_auth_key}"):
            if 'google_auth_flow' in st.session_state:
                del st.session_state.google_auth_flow
            if 'google_auth_url' in st.session_state:
                del st.session_state.google_auth_url
            if 'google_auth_key' in st.session_state:
                del st.session_state.google_auth_key
            st.rerun()
        
        # 認証コード入力（固定キーを使用）
        auth_code = st.text_input(
            "認証コードを入力してください:", 
            key=f"google_auth_code_{st.session_state.google_auth_key}"
        )
        
        if auth_code and st.button(
            "認証を完了", 
            key=f"complete_google_auth_{st.session_state.google_auth_key}"
        ):
            try:
                flow = st.session_state.google_auth_flow
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
                
                # リフレッシュトークンを表示（ユーザーが環境変数に設定するため）
                if creds.refresh_token:
                    st.success("✅ 認証が完了しました！")
                    st.info("🔑 リフレッシュトークン（環境変数に設定してください）:")
                    st.code(creds.refresh_token)
                    
                    # セッション状態をクリア
                    if 'google_auth_flow' in st.session_state:
                        del st.session_state.google_auth_flow
                    if 'google_auth_url' in st.session_state:
                        del st.session_state.google_auth_url
                    if 'google_auth_key' in st.session_state:
                        del st.session_state.google_auth_key
                    
                    return creds
                else:
                    st.error("❌ リフレッシュトークンが取得できませんでした")
                    return None
                    
            except Exception as e:
                st.error(f"認証完了エラー: {e}")
                return None
        
        return None
    
    def _authenticate_from_file(self) -> Optional[Credentials]:
        """ファイルからの認証（フォールバック）"""
        if not GOOGLE_AUTH_AVAILABLE:
            st.error("❌ Google認証ライブラリが利用できません")
            return None
        
        try:
            if os.path.exists(self.CREDENTIALS_FILE):
                creds = None
                if os.path.exists(self.TOKEN_FILE):
                    with open(self.TOKEN_FILE, 'rb') as token:
                        creds = pickle.load(token)
                
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = Flow.from_client_secrets_file(
                            self.CREDENTIALS_FILE, 
                            self.SCOPES
                        )
                        creds = flow.run_local_server(port=0)
                    
                    with open(self.TOKEN_FILE, 'wb') as token:
                        pickle.dump(creds, token)
                
                return creds
            else:
                st.warning(f"⚠️ {self.CREDENTIALS_FILE}が見つかりません")
                return None
                
        except Exception as e:
            st.error(f"ファイル認証エラー: {e}")
            return None
    
    def get_service(self):
        """Google Calendarサービスを取得"""
        if self.service:
            return self.service
        elif self.authenticate():
            return self.service
        return None
    
    def is_authenticated(self) -> bool:
        """認証状態を確認"""
        return st.session_state.get('google_auth_status', False) and self._is_credentials_valid()
    
    def logout(self):
        """ログアウト"""
        self.service = None
        self.credentials = None
        st.session_state.google_credentials = None
        st.session_state.google_auth_status = False
        st.success("ログアウトしました")


# グローバル認証マネージャーインスタンス
_google_auth_manager = None

def get_google_auth_manager() -> 'GoogleAuthManager':
    """グローバル認証マネージャーを取得"""
    global _google_auth_manager
    if _google_auth_manager is None:
        _google_auth_manager = GoogleAuthManager()
    return _google_auth_manager


class GoogleCalendarManager:
    """Google Calendar管理クラス"""
    
    def __init__(self):
        self.auth_manager = get_google_auth_manager()
        self.service = None
    
    def authenticate(self) -> bool:
        """Google認証を実行"""
        if not GOOGLE_AUTH_AVAILABLE:
            st.warning("⚠️ Google認証ライブラリが利用できません")
            return False
        
        return self.auth_manager.authenticate()
    
    def get_service(self):
        """Google Calendarサービスを取得"""
        if not GOOGLE_AUTH_AVAILABLE:
            return None
        
        if self.service:
            return self.service
        
        if self.authenticate():
            self.service = self.auth_manager.get_service()
            return self.service
        
        return None
    
    def is_authenticated(self) -> bool:
        """認証状態を確認"""
        if not GOOGLE_AUTH_AVAILABLE:
            return False
        
        return self.auth_manager.is_authenticated()
    
    def add_event(self, title: str, description: str = "", start_date: str = None, 
                  end_date: str = None, category: str = "音声文字起こし") -> bool:
        """イベントを追加"""
        if not GOOGLE_AUTH_AVAILABLE:
            st.warning("⚠️ Google認証ライブラリが利用できません")
            return False
        
        try:
            service = self.get_service()
            if not service:
                return False
            
            # イベント作成処理
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_date or datetime.now().isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': end_date or (datetime.now() + timedelta(hours=1)).isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
            }
            
            event = service.events().insert(calendarId='primary', body=event).execute()
            st.success(f"✅ イベントを追加しました: {event.get('htmlLink')}")
            return True
            
        except Exception as e:
            st.error(f"❌ イベント追加エラー: {e}")
            return False
    
    def get_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """イベントを取得"""
        if not GOOGLE_AUTH_AVAILABLE:
            return []
        
        try:
            service = self.get_service()
            if not service:
                return []
            
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(
                calendarId='primary', 
                timeMin=now,
                maxResults=max_results, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
            
        except Exception as e:
            st.error(f"❌ イベント取得エラー: {e}")
            return []
    
    def logout(self):
        """ログアウト"""
        if self.auth_manager:
            self.auth_manager.logout()
        self.service = None


def record_audio(duration: int = 5, sample_rate: int = 44100, channels: int = 1) -> Optional[np.ndarray]:
    """音声録音機能（Streamlit Cloud対応）"""
    
    if not PYAUDIO_AVAILABLE:
        st.warning("Streamlit Cloud環境では直接録音は利用できません")
        st.info("代わりにstreamlit-audiorecコンポーネントを使用してください")
        return None
    
    try:
        p = pyaudio.PyAudio()
        
        # 録音ストリームを開く
        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=1024
        )
        
        st.info(f"録音を開始します（{duration}秒間）...")
        
        frames = []
        for i in range(0, int(sample_rate / 1024 * duration)):
            data = stream.read(1024)
            frames.append(data)
        
        st.success("録音が完了しました！")
        
        # ストリームを閉じる
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # データを結合してnumpy配列に変換
        audio_data = b''.join(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        return audio_array
        
    except Exception as e:
        st.error(f"録音エラー: {e}")
        return None

def save_audio_file(audio_data: np.ndarray, filename: str, sample_rate: int = 44100) -> bool:
    """音声ファイルを保存（Python 3.13対応版）"""
    
    # 1. soundfileライブラリを試行
    if SOUNDFILE_AVAILABLE:
        try:
            sf.write(filename, audio_data, sample_rate)
            return True
        except Exception as e:
            st.warning(f"soundfileでの保存に失敗: {e}")
    
    # 2. scipyライブラリを試行
    if SCIPY_AVAILABLE:
        try:
            wavfile.write(filename, sample_rate, audio_data)
            return True
        except Exception as e:
            st.warning(f"scipyでの保存に失敗: {e}")
    
    # 3. pydubライブラリを試行
    if PYDUB_AVAILABLE:
        try:
            # numpy配列をAudioSegmentに変換
            audio_segment = AudioSegment(
                audio_data.tobytes(), 
                frame_rate=sample_rate,
                sample_width=audio_data.dtype.itemsize,
                channels=1
            )
            audio_segment.export(filename, format="wav")
            return True
        except Exception as e:
            st.warning(f"pydubでの保存に失敗: {e}")
    
    # 4. フォールバック: 生のWAVファイルとして保存
    try:
        import wave
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        return True
    except Exception as e:
        st.error(f"音声ファイル保存エラー: {e}")
        return False

def load_audio_file(filename: str) -> Optional[Tuple[np.ndarray, int]]:
    """音声ファイルを読み込み（Python 3.13対応版）"""
    
    # 1. soundfileライブラリを試行
    if SOUNDFILE_AVAILABLE:
        try:
            audio_data, sample_rate = sf.read(filename)
            return audio_data, sample_rate
        except Exception as e:
            st.warning(f"soundfileでの読み込みに失敗: {e}")
    
    # 2. scipyライブラリを試行
    if SCIPY_AVAILABLE:
        try:
            sample_rate, audio_data = wavfile.read(filename)
            return audio_data, sample_rate
        except Exception as e:
            st.warning(f"scipyでの読み込みに失敗: {e}")
    
    # 3. pydubライブラリを試行
    if PYDUB_AVAILABLE:
        try:
            audio_segment = AudioSegment.from_file(filename)
            audio_data = np.array(audio_segment.get_array_of_samples())
            sample_rate = audio_segment.frame_rate
            return audio_data, sample_rate
        except Exception as e:
            st.warning(f"pydubでの読み込みに失敗: {e}")
    
    # 4. フォールバック: 生のWAVファイルとして読み込み
    try:
        import wave
        with wave.open(filename, 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            audio_data = np.frombuffer(wav_file.readframes(wav_file.getnframes()), dtype=np.int16)
            return audio_data, sample_rate
    except Exception as e:
        st.error(f"音声ファイル読み込みエラー: {e}")
        return None


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


def show_audio_library_status():
    """音声処理ライブラリの利用状況を表示"""
    st.sidebar.write("### 🎵 音声処理ライブラリ状況")
    
    # 基本ライブラリ
    st.sidebar.write(f"**PyAudio**: {'✅ 利用可能' if PYAUDIO_AVAILABLE else '❌ 利用不可'}")
    st.sidebar.write(f"**OpenAI**: {'✅ 利用可能' if OPENAI_AVAILABLE else '❌ 利用不可'}")
    
    # 音声処理ライブラリ
    st.sidebar.write(f"**SoundFile**: {'✅ 利用可能' if SOUNDFILE_AVAILABLE else '❌ 利用不可'}")
    st.sidebar.write(f"**Librosa**: {'✅ 利用可能' if LIBROSA_AVAILABLE else '❌ 利用不可'}")
    
    # 代替ライブラリ
    st.sidebar.write(f"**PyDub**: {'✅ 利用可能' if PYDUB_AVAILABLE else '❌ 利用不可'}")
    st.sidebar.write(f"**SciPy**: {'✅ 利用可能' if SCIPY_AVAILABLE else '❌ 利用不可'}")
    
    # Python 3.13対応状況
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 13:
        st.sidebar.warning("⚠️ Python 3.13+環境: 一部の音声処理ライブラリが利用できません")
        st.sidebar.info("💡 代替ライブラリ（PyDub, SciPy）を使用します")
    else:
        st.sidebar.success("✅ 標準的なPython環境: 全ライブラリが利用可能")


def get_available_audio_libraries() -> List[str]:
    """利用可能な音声処理ライブラリのリストを取得"""
    available_libs = []
    
    if SOUNDFILE_AVAILABLE:
        available_libs.append("SoundFile")
    if LIBROSA_AVAILABLE:
        available_libs.append("Librosa")
    if PYDUB_AVAILABLE:
        available_libs.append("PyDub")
    if SCIPY_AVAILABLE:
        available_libs.append("SciPy")
    
    return available_libs
