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

    async def create(self, category_id: str, article_data: dict) -> bool:
        """
        建立新文章（鐵人賽）

        Args:
            category_id: 系列 ID（例如 "8446" 對應 Python pytest TDD 系列）
            article_data: 文章資料字典，包含:
                - subject: 文章標題
                - description: 文章內容

        Returns:
            bool: 是否建立成功
        """
        # 從字典中取出參數
        subject = article_data['subject']
        description = article_data['description']
        
        # 點擊鐵人發文按鈕
        await self._click_ironman_post_button()
        
        # 等待並選擇系列
        await self._wait_for_series_modal()
        await self._select_series(category_id)

        # 等待頁面載入
        await self.page.wait_for_load_state("domcontentloaded")

        # 設定標題和內容（使用基類方法）
        await self._set_subject(subject)
        await self._set_description(description)

        # 發表文章
        return await self._publish_article()

    async def _click_ironman_post_button(self) -> None:
        """點擊鐵人發文按鈕"""
        await self.ironman_button.wait_for(state="visible", timeout=5000)
        await self.ironman_button.click()
        # 已點擊鐵人發文按鈕

    async def _wait_for_series_modal(self) -> None:
        """等待系列選擇 modal 顯示"""
        await self.series_modal.wait_for(state="visible", timeout=5000)
        # 系列選擇 modal 已顯示

    async def _select_series(self, category_id: str) -> None:
        """選擇特定系列"""
        series_link = self.page.locator(f'a[href*="/2025ironman/create/{category_id}"]')
        await series_link.wait_for(state="visible", timeout=5000)
        await series_link.click()
        # 已選擇系列: {category_id}

    async def _publish_article(self) -> bool:
        """發表文章"""
        # 準備發表文章...

        # 模擬人類行為：檢查內容後再提交的延遲
        # await self.page.wait_for_timeout(random.randint(1500, 3000))

        # 處理 reCAPTCHA（使用基類方法）
        if not await self._handle_recaptcha():
            return False

        # 點擊下拉選單
        await self._click_dropdown_toggle()
        
        # 點擊發表按鈕
        await self._click_publish_button()

        # 等待頁面跳轉
        return await self._wait_for_redirect()

    async def _click_dropdown_toggle(self) -> None:
        """點擊下拉選單觸發按鈕"""
        await self.dropdown_toggle.wait_for(state="visible", timeout=5000)
        await self.dropdown_toggle.click()
        # 等待下拉選單展開
        await self.page.wait_for_timeout(500)
        # 已展開下拉選單

    async def _click_publish_button(self) -> None:
        """點擊發表按鈕"""
        await self.publish_button.wait_for(state="visible", timeout=5000)
        await self.publish_button.click()
        # 已點擊發表按鈕

    async def _wait_for_redirect(self) -> bool:
        """等待頁面跳轉（覆寫基類方法）"""
        return await super()._wait_for_redirect(
            exclude_patterns=["/draft", "/create"],
            timeout=15000
        )