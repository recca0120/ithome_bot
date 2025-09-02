"""
文章管理模組
"""
from playwright.async_api import Page

from .article_base import ArticleBase


class ArticleUpdater(ArticleBase):
    """文章更新器"""

    def __init__(self, page: Page):
        """
        初始化文章管理器

        Args:
            page: Playwright 頁面物件
        """
        super().__init__(page)
        # 初始化特有的 locators
        self.update_button = page.locator('#updateSubmitBtn')

    async def update(self, article_data: dict) -> bool:
        """
        更新文章內容

        Args:
            article_data: 文章資料字典，包含:
                - article_id: 文章 ID
                - subject: 文章標題
                - description: 文章內容

        Returns:
            bool: 是否更新成功
        """
        # 從字典中取出參數
        article_id = article_data['article_id']
        subject = article_data['subject']
        description = article_data['description']
        
        # 導航到編輯頁面
        await self._navigate_to_edit_page(article_id)

        # 等待頁面載入
        await self.page.wait_for_load_state("domcontentloaded")

        # 更新標題和內容（使用基類方法）
        await self._set_subject(subject, clear_first=True)
        await self._set_description(description, clear_first=True)

        # 提交更新
        return await self._submit_update()

    async def _navigate_to_edit_page(self, article_id: str) -> None:
        """導航到文章編輯頁面"""
        edit_url = f"https://ithelp.ithome.com.tw/articles/{article_id}/edit"
        await self.page.goto(edit_url)
        # 已導航到文章編輯頁面: {edit_url}

    async def _submit_update(self) -> bool:
        """提交更新"""
        # 定義提交動作
        submit_actions = [
            self._click_update_button
        ]
        
        # 使用基類的通用提交方法
        return await self._submit_form(submit_actions, exclude_patterns=["/edit"])

    async def _click_update_button(self) -> None:
        """點擊更新按鈕"""
        await self.update_button.wait_for(state="visible", timeout=5000)
        await self.update_button.click()
        # 已點擊更新按鈕