"""
共用的 pytest fixtures 和設定
"""
import pytest
import pytest_asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from src.bot import Bot

# 載入環境變數
load_dotenv()


def base_path() -> Path:
    """
    取得專案根目錄路徑

    Returns:
        Path: 專案根目錄路徑
    """
    # 從 tests 目錄往上一層取得專案根目錄
    return Path(__file__).parent.parent.resolve()


@pytest.fixture
def credential():
    """從環境變數取得帳號密碼"""
    return {
        "account": os.getenv("ITHOME_ACCOUNT"),
        "password": os.getenv("ITHOME_PASSWORD")
    }


@pytest_asyncio.fixture
async def page():
    """建立並初始化 Playwright Page"""
    # 啟動 Playwright 和瀏覽器
    playwright = await async_playwright().start()
    browser = await playwright.webkit.launch(headless=False)
    page = await browser.new_page()
    
    yield page
    
    # 清理
    await browser.close()
    await playwright.stop()


@pytest_asyncio.fixture
async def bot(page, credential):
    """建立並初始化 Bot 實例，並執行登入"""
    # 建立 Bot 實例，指定 cookies 檔案位置在專案根目錄
    cookies_file = base_path() / "cookies.txt"
    bot = Bot(page, cookies_file=str(cookies_file))
    
    # 載入 cookies
    await bot.load_cookies()

    # 執行登入
    await bot.login(credential["account"], credential["password"])

    # 儲存 cookies
    await bot.save_cookies()

    yield bot
