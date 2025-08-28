"""
測試文章編輯功能
"""
import pytest



@pytest.mark.asyncio
async def test_update_article(automation):
    """測試更新文章"""
    
    # 讀取文章內容
    with open("day01-python-environment-setup.md", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 設定文章資料
    article_id = "10376177"
    subject = "[Day 01] Python pytest TDD 實戰：從零開始的測試驅動開發 - 環境設置與第一個測試"
    
    # Act - 更新文章內容
    result = await automation.update_article(article_id, subject, content)
    
    # Assert - 驗證更新結果
    assert result is True, "文章更新應該成功"