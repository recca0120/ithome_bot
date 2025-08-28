"""
測試使用者主頁導航功能
"""
import pytest


@pytest.mark.asyncio
async def test_navigate_to_user_profile(automation):
    """測試導航到使用者主頁"""
    
    # Act - 導航到使用者主頁
    await automation.goto_user_profile()
    
    # Assert - 驗證已導航到我的主頁
    await automation.page.wait_for_load_state("domcontentloaded")
    current_url = automation.page.url
    print(f"導航完成後的頁面: {current_url}")
    
    # 驗證最終網址是否正確
    expected_url = "https://ithelp.ithome.com.tw/users/20065818"
    assert current_url == expected_url, f"應該要在 {expected_url}，但目前在 {current_url}"