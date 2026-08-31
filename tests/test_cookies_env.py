"""
測試 load_cookies() 在 cookies 檔案不存在、但有 ITHOME_COOKIES 環境變數時的行為
（CI 常見用法：cookies.txt 內容存成 Secret，不用先手動產生檔案）
"""
import pytest
from pathlib import Path

from ithome_bot.client import Client


@pytest.mark.asyncio
async def test_load_cookies_falls_back_to_env_var(page, tmp_path, monkeypatch):
    """cookies 檔案不存在、但有 ITHOME_COOKIES 時，應該用環境變數的內容"""

    # Arrange - 先用真實登入拿到一組有效的 cookies 內容
    real_cookies_file = Path(__file__).parent.parent / "cookies.txt"
    assert real_cookies_file.exists(), "需要先跑過一次真的登入，讓根目錄的 cookies.txt 存在"
    cookies_content = real_cookies_file.read_text(encoding="utf-8")

    missing_cookies_file = tmp_path / "does-not-exist-yet.txt"
    monkeypatch.setenv("ITHOME_COOKIES", cookies_content)

    client = Client(page, cookies_file=str(missing_cookies_file))

    # Act
    loaded = await client.load_cookies()

    # Assert - 讀取成功、且把內容寫成了檔案（下次可以直接用檔案，不用再讀環境變數）
    assert loaded is True
    assert missing_cookies_file.exists()
    assert missing_cookies_file.read_text(encoding="utf-8") == cookies_content

    # cookies 是有效的：導到 ithelp 應該已經是登入狀態
    await page.goto("https://ithelp.ithome.com.tw/")
    await page.wait_for_load_state("domcontentloaded")
    assert await page.locator("a#dLabel").is_visible()


@pytest.mark.asyncio
async def test_load_cookies_returns_false_without_file_or_env(page, tmp_path, monkeypatch):
    """cookies 檔案不存在、也沒有 ITHOME_COOKIES 時，應該回傳 False"""

    monkeypatch.delenv("ITHOME_COOKIES", raising=False)
    missing_cookies_file = tmp_path / "does-not-exist.txt"
    client = Client(page, cookies_file=str(missing_cookies_file))

    loaded = await client.load_cookies()

    assert loaded is False
    assert not missing_cookies_file.exists()
