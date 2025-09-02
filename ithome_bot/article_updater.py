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
        # 準備提交更新...

        # 模擬人類行為：檢查內容後再提交的延遲
        # await self.page.wait_for_timeout(random.randint(1500, 3000))

        # 處理 reCAPTCHA（使用基類方法）
        if not await self._handle_recaptcha():
            return False

        # 點擊更新按鈕
        await self._click_update_button()

        # 等待頁面跳轉
        return await self._wait_for_redirect()

    async def _click_update_button(self) -> None:
        """點擊更新按鈕"""
        await self.update_button.wait_for(state="visible", timeout=5000)
        await self.update_button.click()
        # 已點擊更新按鈕

    async def _wait_for_redirect(self) -> bool:
        """等待頁面跳轉（覆寫基類方法）"""
        return await super()._wait_for_redirect(
            exclude_patterns=["/edit"],
            timeout=15000
        )