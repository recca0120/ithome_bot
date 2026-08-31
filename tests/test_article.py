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
async def test_update_article_with_tags(client):
    """測試更新文章時可以附加自訂 tag，且不影響原有的鐵人賽自動 tag"""

    description_file = Path(__file__).parent / "fixtures/day01-python-environment-setup.md"
    with open(description_file, 'r', encoding='utf-8') as f:
        description = f.read()

    unique_tag = f"pytest-tag-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    article_data = {
        "article_id": "10406474",
        "subject": "Day 01：AI 重構 legacy 系統的真正難點在哪裡",
        "description": description,
        "tags": ["PHP", unique_tag],
    }

    # Act
    result = await client.update_article(article_data)

    # Assert - 更新成功，且文章頁面上看得到剛加上去的 tag
    assert result == "10406474"

    # 網站會把 tag 統一轉成小寫存
    tag_links = await client.page.locator("a.qa-header__tagList").all_text_contents()
    assert "php" in tag_links
    assert unique_tag in tag_links
    # 鐵人賽自動 tag 不該被我們動到
    assert "18th鐵人賽" in tag_links


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
