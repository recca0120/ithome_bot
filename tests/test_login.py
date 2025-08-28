"""
TDD: 測試 IThomeAutomation 的 login 功能
"""
import pytest
from src.ithome_automation import IThomeAutomation


@pytest.mark.asyncio
async def test_user_can_login_to_ithome(credential):
    """測試使用者可以登入到 iThome"""
    
    automation = IThomeAutomation()
    
    try:
        # 初始化瀏覽器
        await automation.initialize()
        
        # Act - 執行登入
        login_success = await automation.login(credential["account"], credential["password"])
        
        # Assert - 驗證登入成功
        assert login_success is True, "登入應該要成功"
        assert automation.page is not None
        assert automation.browser is not None
        
        # 驗證登入後的 URL（應該在使用者主頁）
        current_url = automation.page.url
        assert "ithelp.ithome.com.tw/users/" in current_url, f"登入後應該在使用者主頁，但目前在 {current_url}"
        
        # 儲存 cookies 供後續測試使用
        await automation.save_cookies()
        
    finally:
        # Cleanup
        await automation.close()

