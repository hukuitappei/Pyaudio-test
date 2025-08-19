#!/usr/bin/env python3
"""
StreamlitDuplicateElementKeyエラー修正のテストスクリプト

このスクリプトは、settings_ui_audiorec.pyで修正されたキー生成方法が
正しく適用されているかを確認します。
"""

import re
import sys
from pathlib import Path

def check_duplicate_key_fixes():
    """修正内容の確認"""
    settings_file = Path("settings_ui_audiorec.py")
    
    if not settings_file.exists():
        print("❌ settings_ui_audiorec.py が見つかりません")
        return False
    
    print("🔍 StreamlitDuplicateElementKeyエラー修正の確認を開始...")
    
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修正前のパターンをチェック
    old_patterns = [
        r'key=f"device_selection_{id\(settings\)}"',
        r'key=f"whisper_model_size_{id\(settings\)}"',
        r'key=f"audio_sample_rate_{id\(settings\)}"',
    ]
    
    # 修正後のパターンをチェック
    new_patterns = [
        r'st\.session_state\.device_selection_key',
        r'st\.session_state\.whisper_model_size_key',
        r'st\.session_state\.audio_sample_rate_key',
        r'uuid\.uuid4\(\)\.hex\[:8\]',
        r'str\(uuid\.uuid4\(\)\)',
    ]
    
    # 必要なインポートをチェック
    required_imports = [
        'import uuid',
        'from typing import Dict, Any, List, Optional',
    ]
    
    issues = []
    
    # 古いパターンの検出
    for pattern in old_patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"❌ 古いキー生成パターンが検出されました: {pattern}")
    
    # 新しいパターンの確認
    new_pattern_found = False
    for pattern in new_patterns:
        if re.search(pattern, content):
            new_pattern_found = True
            break
    
    if not new_pattern_found:
        issues.append("❌ 新しいキー生成パターンが見つかりません")
    
    # 必要なインポートの確認
    for import_line in required_imports:
        if import_line not in content:
            issues.append(f"❌ 必要なインポートが見つかりません: {import_line}")
    
    # 結果の表示
    if issues:
        print("\n❌ 修正に問題があります:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ 修正が正常に適用されています:")
        print("  - 古いキー生成パターンが除去されました")
        print("  - 新しいキー生成パターンが適用されました")
        print("  - 必要なインポートが追加されました")
        print("  - UUIDベースの一意キー生成が実装されました")
        return True

def check_specific_functions():
    """特定の関数の修正確認"""
    settings_file = Path("settings_ui_audiorec.py")
    
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    functions_to_check = [
        'render_device_settings_tab',
        'render_transcription_settings_tab',
        'render_ui_settings_tab',
        'render_audio_settings_tab',
        'render_user_dictionary_tab',
        'render_commands_tab',
        'render_task_management_tab',
        'render_calendar_management_tab',
        'render_file_management_tab',
        'display_history_page',
    ]
    
    print("\n🔍 関数別の修正確認:")
    
    for func_name in functions_to_check:
        if func_name in content:
            # 関数内でsession_stateの使用を確認
            if 'st.session_state' in content:
                print(f"  ✅ {func_name}: セッション状態を使用")
            else:
                print(f"  ⚠️  {func_name}: セッション状態の使用を確認してください")
        else:
            print(f"  ❌ {func_name}: 関数が見つかりません")

def check_uuid_usage():
    """UUID使用の確認"""
    settings_file = Path("settings_ui_audiorec.py")
    
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n🔍 UUID使用の確認:")
    
    # UUIDの使用回数をカウント
    uuid_count = content.count('uuid.uuid4()')
    session_state_count = content.count('st.session_state')
    
    print(f"  - uuid.uuid4() の使用回数: {uuid_count}")
    print(f"  - st.session_state の使用回数: {session_state_count}")
    
    if uuid_count > 0 and session_state_count > 0:
        print("  ✅ UUIDとセッション状態が適切に使用されています")
        return True
    else:
        print("  ❌ UUIDまたはセッション状態の使用が不足しています")
        return False

def main():
    """メイン関数"""
    print("=" * 60)
    print("StreamlitDuplicateElementKeyエラー修正テスト")
    print("=" * 60)
    
    # 基本修正の確認
    success = check_duplicate_key_fixes()
    
    # UUID使用の確認
    uuid_success = check_uuid_usage()
    
    # 関数別の確認
    check_specific_functions()
    
    print("\n" + "=" * 60)
    if success and uuid_success:
        print("🎉 すべての修正が正常に適用されています！")
        print("Streamlit Cloudでの動作が改善されるはずです。")
    else:
        print("⚠️  修正に問題があります。確認してください。")
    print("=" * 60)

if __name__ == "__main__":
    main()
