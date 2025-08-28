"""
測試文章編輯功能
"""
import pytest
from src.utils import base_path



@pytest.mark.asyncio
async def test_update_article(bot):
    """測試更新文章"""

    # 讀取文章內容
    content_file = base_path() / "tests/fixtures/day01-python-environment-setup.md"
    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 設定文章資料
    article_data = {
        "article_id": "10376177",
        "subject": "[Day 01] Python pytest TDD 實戰：從零開始的測試驅動開發 - 環境設置與第一個測試",
        "description": content
    }

    # Act - 更新文章內容
    result = await bot.update_article(article_data)

    # Assert - 驗證更新結果
    assert result is True, "文章更新應該成功"
