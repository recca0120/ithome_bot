"""
TDD: 測試 IThomeAutomation 的 login 功能
"""
import pytest
import os
from dotenv import load_dotenv
from src.ithome_automation import IThomeAutomation

# 載入環境變數
load_dotenv()


@pytest.fixture
def test_config():
    """從環境變數取得測試設定"""
    return {
        "account": os.getenv("ITHOME_ACCOUNT"),
        "password": os.getenv("ITHOME_PASSWORD"),
        "headless": os.getenv("HEADLESS", "false").lower() == "true"
    }


@pytest.mark.asyncio
async def test_user_can_login_to_ithome(test_config):
    """測試使用者可以登入到 iThome"""
    
    automation = IThomeAutomation(headless=test_config["headless"])
    
    try:
        # 初始化瀏覽器
        await automation.initialize()
        
        # Act - 執行登入
        login_success = await automation.login(test_config["account"], test_config["password"])
        
        # Assert - 驗證登入成功
        assert login_success is True, "登入應該要成功"
        assert automation.page is not None
        assert automation.browser is not None
        
        # 導航到使用者主頁
        await automation.goto_user_profile()
        
        # 驗證已導航到我的主頁
        # 點擊我的主頁後應該會跳轉到使用者頁面
        await automation.page.wait_for_load_state("domcontentloaded")
        current_url = automation.page.url
        print(f"登入完成後的頁面: {current_url}")
        
        # 驗證最終網址是否正確
        expected_url = "https://ithelp.ithome.com.tw/users/20065818"
        assert current_url == expected_url, f"應該要在 {expected_url}，但目前在 {current_url}"
        
    finally:
        # Cleanup
        await automation.close()