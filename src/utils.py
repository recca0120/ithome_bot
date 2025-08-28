"""
專案工具函數
"""
from pathlib import Path


def base_path() -> Path:
    """
    取得專案根目錄路徑

    Returns:
        Path: 專案根目錄路徑
    """
    # 從 src 目錄往上一層取得專案根目錄
    return Path(__file__).parent.parent.resolve()
