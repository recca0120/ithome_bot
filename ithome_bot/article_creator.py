"""
文章建立模組
"""
from playwright.async_api import Page

from .article_base import ArticleBase


class ArticleCreator(ArticleBase):
    """文章建立器"""

    def __init__(self, page: Page):
        """
        初始化文章建立器

        Args:
            page: Playwright 頁面物件
        """
        super().__init__(page)
        # 初始化特有的 locators
        self.ironman_button = page.locator('.menu__ironman-btn')
        self.series_modal = page.locator('#ir-select-series__common')
        self.dropdown_toggle = page.locator('.save-group__dropdown-toggle')
        self.publish_button = page.locator('#createSubmitBtn')

    async def create(self, article_data: dict) -> str | None:
        """
        建立新文章（鐵人賽）

        Args:
            article_data: 文章資料字典，包含:
                - category_id: 系列 ID（例如 "8446" 對應 Python pytest TDD 系列）
                - subject: 文章標題
                - description: 文章內容

        Returns:
            str | None: 成功時回傳 article_id，失敗時回傳 None
        """
        # 從字典中取出參數
        category_id = article_data['category_id']
        subject = article_data['subject']
        description = article_data['description']
        
        # 導航到建立頁面
        await self._navigate_to_create_page(category_id)

        # 等待頁面載入
        await self.page.wait_for_load_state("domcontentloaded")

        # 設定標題和內容（使用基類方法）
        await self._set_subject(subject)
        await self._set_description(description)

        # 提交文章
        return await self._submit()

    async def _navigate_to_create_page(self, category_id: str) -> None:
        """導航到文章建立頁面"""
        # 開啟鐵人發文選單
        await self._open_ironman_menu()
        
        # 選擇指定系列
        await self._select_series_from_modal(category_id)
        
        # 已導航到文章建立頁面
    
    async def _open_ironman_menu(self) -> None:
        """開啟鐵人發文選單"""
        await self.ironman_button.wait_for(state="visible", timeout=5000)
        await self.ironman_button.click()
        
        # 等待系列選擇 modal 顯示
        await self.series_modal.wait_for(state="visible", timeout=5000)
    
    async def _select_series_from_modal(self, category_id: str) -> None:
        """從 modal 中選擇指定系列"""
        series_link = self.page.locator(f'a[href*="/2025ironman/create/{category_id}"]')
        await series_link.wait_for(state="visible", timeout=5000)
        await series_link.click()

    async def _perform_submit_action(self) -> None:
        """實作具體的提交動作：點擊下拉選單後發表"""
        await self._click_dropdown_toggle()
        await self._click_submit_button()
    
    async def _wait_for_submit_redirect(self) -> bool:
        """等待發表後的頁面跳轉"""
        return await self._wait_for_redirect(
            exclude_patterns=["/draft", "/create"],
            timeout=15000
        )

    async def _click_dropdown_toggle(self) -> None:
        """點擊下拉選單觸發按鈕"""
        await self.dropdown_toggle.wait_for(state="visible", timeout=5000)
        await self.dropdown_toggle.click()
        # 等待下拉選單展開
        await self.page.wait_for_timeout(500)
        # 已展開下拉選單

    async def _click_submit_button(self) -> None:
        """點擊提交按鈕（發表）"""
        await self.publish_button.wait_for(state="visible", timeout=5000)
        await self.publish_button.click()
        # 已點擊發表按鈕