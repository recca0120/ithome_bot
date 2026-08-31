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
    """
    測試更新文章時可以附加自訂 tag，且不影響原有的鐵人賽自動 tag

    這個測試操作的是一篇真實在用的文章（不是拋棄式的測試文章），所以
    絕對不能把內容換成跟這篇文章無關的東西——先讀出目前真實的標題/內文，
    測試時原封不動用回去，只測 tag 這個維度的行為，不動到內容本身。
    只加 1 個新 tag，是因為這篇文章原本就有接近上限（見
    ArticleBase.MAX_TAGS）的既有 tag 數量，加太多會直接被
    _set_tags() 的保護擋下來。

    已知限制：_set_tags() 只會新增、不會清掉自己加的 tag，這篇文章目前
    正好卡在 MAX_TAGS 上限，所以測試跑完會留下一個 pytest-tag-<timestamp>
    沒清掉；連續重跑這個測試（不手動清掉上一次留下的 tag）會直接撞到
    MAX_TAGS 被 ValueError 擋下來，不是這個測試本身壞掉。
    """
    article_id = "10406474"

    await client.page.goto(f"https://ithelp.ithome.com.tw/articles/{article_id}/edit")
    await client.page.wait_for_load_state("domcontentloaded")
    real_subject = await client.page.locator('input[name="subject"]').input_value()
    real_description = await client.page.eval_on_selector(
        'textarea[name="description"]', "el => el.value"
    )

    unique_tag = f"pytest-tag-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    article_data = {
        "article_id": article_id,
        "subject": real_subject,
        "description": real_description,
        "tags": [unique_tag],
    }

    # Act
    result = await client.update_article(article_data)

    # Assert - 更新成功，且文章頁面上看得到剛加上去的 tag，內容沒有跑掉
    assert result == article_id

    # 內容沒被換掉：渲染後的 HTML 會把 markdown 語法符號去掉，所以不能拿去跟
    # 原始 markdown 逐字比對，改成檢查一段夠長、不太可能巧合出現的原文片段
    body_text = await client.page.locator(".markdown__style").inner_text()
    distinctive_snippet = real_description.strip().split("\n\n")[0].lstrip("#").strip()
    assert distinctive_snippet in body_text

    tag_links = await client.page.locator("a.qa-header__tagList").all_text_contents()
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
