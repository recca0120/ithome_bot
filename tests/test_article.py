"""
測試文章編輯功能
"""
import pytest
from pathlib import Path
from datetime import datetime



@pytest.mark.asyncio
async def test_create_article(client):
    """測試建立鐵人賽文章"""
    
    # 讀取文章內容
    description_file = Path(__file__).parent / "fixtures/day01-python-environment-setup.md"
    with open(description_file, 'r', encoding='utf-8') as f:
        description = f.read()
    
    # 設定文章資料 (使用時間戳記確保唯一標題)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    article_data = {
        "category_id": "8446",  # Python pytest TDD 實戰 系列
        "subject": f"[Day 07] 測試文章 - {timestamp}",
        "description": description
    }
    
    # Act - 建立並發表文章
    result = await client.create_article(article_data)
    
    # Assert - 驗證發表結果
    assert result is not None, "文章發表應該成功"
    assert isinstance(result, str), "應該回傳文章 ID"
    assert result.isdigit(), "文章 ID 應該是數字字串"


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
    assert result is not None, "文章更新應該成功"
    assert result == "10376177", "應該回傳正確的文章 ID"
