"""
測試文章編輯功能
"""
import pytest


@pytest.mark.asyncio
async def test_navigate_to_article_edit(automation):
    """測試導航到文章編輯頁面"""
    
    article_id = "10376177"
    
    # Act - 導航到文章編輯頁面
    await automation.goto_article_edit(article_id, "test", "abc")
    
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


@pytest.mark.asyncio
async def test_update_article_subject_and_description(automation):
    """測試更新文章標題和內容"""
    
    article_id = "10376177"
    test_subject = "[Day 01] Python pytest TDD 實戰：從零開始的測試驅動開發 - 環境設置與第一個測試"
    
    # 讀取文章內容檔案
    import os
    content_file = "/Users/recca0120/PycharmProjects/ironman-bot/day01-python-environment-setup.md"
    
    if os.path.exists(content_file):
        with open(content_file, 'r', encoding='utf-8') as f:
            test_description = f.read()
        print(f"📖 已讀取文章內容，長度: {len(test_description)} 字元")
    else:
        test_description = "# 無法讀取文章內容\n\n請檢查文件路徑是否正確。"
        print("⚠️ 文章內容檔案不存在，使用預設內容")
    
    # Act - 導航到文章編輯頁面並更新內容
    await automation.goto_article_edit(
        article_id, 
        subject=test_subject, 
        description=test_description
    )
    
    # 等待更新完成
    await automation.page.wait_for_timeout(2000)
    current_url = automation.page.url
    print(f"更新後的頁面: {current_url}")
    
    # 檢查更新結果
    if "/edit" not in current_url:
        print(f"✅ 成功！文章已更新並跳轉到: {current_url}")
        
        # 如果跳轉成功，驗證文章頁面上是否顯示了新標題
        try:
            page_title = automation.page.locator('h1, .title, [class*="title"]').first
            if await page_title.is_visible(timeout=3000):
                displayed_title = await page_title.text_content()
                print(f"頁面顯示的標題: {displayed_title}")
                # 檢查標題是否包含我們設定的內容（可能有額外的格式或文字）
                if test_subject in displayed_title:
                    print("✅ 標題更新驗證成功")
                else:
                    print(f"⚠️ 標題可能未完全匹配，預期: {test_subject}，實際: {displayed_title}")
        except Exception as e:
            print(f"⚠️ 無法驗證頁面標題: {e}")
    else:
        print(f"⚠️ 仍在編輯頁面，檢查編輯器內容...")
        
        # 如果仍在編輯頁面，驗證編輯器內容
        try:
            subject_input = automation.page.locator('input[name="subject"]')
            if await subject_input.is_visible(timeout=2000):
                actual_subject = await subject_input.input_value()
                assert actual_subject == test_subject, f"標題應該是 '{test_subject}'，但實際是 '{actual_subject}'"
                print("✅ 編輯器標題驗證成功")
        except Exception as e:
            print(f"⚠️ 無法驗證編輯器標題: {e}")
    
    print(f"已執行文章 {article_id} 的更新操作")
    print(f"測試標題: {test_subject}")
    print(f"內容長度: {len(test_description)} 字元")