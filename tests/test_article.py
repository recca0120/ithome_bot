"""
測試文章編輯功能
"""
import pytest


@pytest.mark.asyncio
async def test_navigate_to_article_edit(automation):
    """測試導航到文章編輯頁面"""
    
    article_id = "10376177"
    
    # Act - 導航到文章編輯頁面
    await automation.goto_article_edit(article_id)
    
    # Assert - 驗證已導航到編輯頁面
    await automation.page.wait_for_load_state("networkidle")
    current_url = automation.page.url
    print(f"當前頁面: {current_url}")
    
    # 驗證 URL 是否正確
    expected_url = f"https://ithelp.ithome.com.tw/articles/{article_id}/edit"
    assert current_url == expected_url, f"應該要在 {expected_url}，但目前在 {current_url}"
    
    # 驗證頁面上是否有編輯器元素（例如標題輸入框）
    title_input = automation.page.locator('input[name="subject"]')
    assert await title_input.is_visible(), "應該要看到文章標題輸入框"
    
    print(f"成功導航到文章 {article_id} 的編輯頁面")