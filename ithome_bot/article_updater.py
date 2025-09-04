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
        # 儲存當前編輯的文章 ID
        self._current_article_id = None

    async def update(self, article_data: dict) -> str | None:
        """
        更新文章內容

        Args:
            article_data: 文章資料字典，包含:
                - article_id: 文章 ID
                - subject: 文章標題
                - description: 文章內容

        Returns:
            str | None: 成功時回傳 article_id，失敗時回傳 None
        """
        # 從字典中取出參數
        article_id = article_data['article_id']
        subject = article_data['subject']
        description = article_data['description']
        
        # 儲存當前文章 ID
        self._current_article_id = article_id
        
        # 導航到編輯頁面
        await self._navigate_to_edit_page(article_id)

        # 等待頁面載入
        await self.page.wait_for_load_state("domcontentloaded")

        # 更新標題和內容（使用基類方法）
        await self._set_subject(subject, clear_first=True)
        await self._set_description(description, clear_first=True)

        # 提交更新
        return await self._submit()

    async def _navigate_to_edit_page(self, article_id: str) -> None:
        """導航到文章編輯頁面"""
        edit_url = f"https://ithelp.ithome.com.tw/articles/{article_id}/edit"
        await self.page.goto(edit_url)
        # 已導航到文章編輯頁面: {edit_url}

    async def _perform_submit_action(self) -> None:
        """實作具體的提交動作：點擊更新按鈕"""
        await self._click_submit_button()
    
    async def _wait_for_submit_redirect(self) -> bool:
        """等待更新後的頁面跳轉"""
        try:
            # 等待跳轉到文章檢視頁面（非編輯頁面）
            await self.page.wait_for_url(
                f"**/articles/{self._current_article_id}",
                timeout=15000
            )
            return True
        except:
            return False

    async def _click_submit_button(self) -> None:
        """點擊提交按鈕（更新）"""
        await self.update_button.wait_for(state="visible", timeout=5000)
        await self.update_button.click()
        # 已點擊更新按鈕
    
    def _extract_article_id_from_url(self) -> str | None:
        """
        從當前 URL 中提取文章 ID
        對於更新操作，只在成功跳轉後回傳 article_id
        
        Returns:
            str | None: 文章 ID
        """
        current_url = self.page.url
        
        # 檢查是否還在編輯頁面（表示更新失敗）
        if "/edit" in current_url:
            return None
            
        # 檢查 URL 是否包含預期的文章 ID
        if self._current_article_id and f"/articles/{self._current_article_id}" in current_url:
            return self._current_article_id
            
        # 嘗試從 URL 提取
        return super()._extract_article_id_from_url()