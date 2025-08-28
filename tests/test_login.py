"""
TDD: 測試 Bot 的 login 功能
"""
import pytest
from src.bot import Bot


@pytest.mark.asyncio
async def test_user_can_login_to_ithome(page, credential):
    """測試使用者可以登入到 iThome"""
    
    bot = Bot(page)

    # Act - 執行登入
    login_success = await bot.login(credential["account"], credential["password"])

    # Assert - 驗證登入成功
    assert login_success is True, "登入應該要成功"
    assert bot.page is not None

    # 驗證登入後的 URL（應該在使用者主頁）
    current_url = bot.page.url
    assert "ithelp.ithome.com.tw/users/" in current_url, f"登入後應該在使用者主頁，但目前在 {current_url}"

    # 儲存 cookies 供後續測試使用
    await bot.save_cookies()

