"""
測試文章編輯功能
"""
import pytest
from pathlib import Path



@pytest.mark.asyncio
async def test_update_article(client):
    """測試更新文章"""

    # 讀取文章內容
    description_file = Path(__file__).parent / "fixtures/day01-python-environment-setup.md"
    with open(description_file, 'r', encoding='utf-8') as f:
        description = f.read()

    # 設定文章資料
    article_data = {
        "article_id": "10376177",
        "subject": "[Day 01] Python pytest TDD 實戰：從零開始的測試驅動開發 - 環境設置與第一個測試",
        "description": description
    }

    # Act - 更新文章內容
    result = await client.update_article(article_data)

    # Assert - 驗證更新結果
    assert result is True, "文章更新應該成功"
