"""
Streamlit Cloud用エントリーポイント
音声録音・文字起こしアプリ
"""

# メインアプリケーションをインポートして実行
import sys
import os

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app_audiorec import main

if __name__ == "__main__":
    main()
