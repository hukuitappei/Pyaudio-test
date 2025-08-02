"""
app_audiorec.py用の統合ユーティリティクラス
設定管理、デバイス管理、ユーザー辞書、コマンド処理などの機能を統合
"""

import json
import os
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any
import tempfile
import wave
import numpy as np

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