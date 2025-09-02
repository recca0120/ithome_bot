"""
文章建立模組
"""
import random
from playwright.async_api import Page

from .recaptcha import ReCaptcha


class ArticleCreator:
    """文章建立器"""

    def __init__(self, page: Page):
        """
        初始化文章建立器

        Args:
            page: Playwright 頁面物件
        """
        self.page = page
        # 初始化 locators
        self.ironman_button = page.locator('.menu__ironman-btn')
        self.series_modal = page.locator('#ir-select-series__common')
        self.subject_input = page.locator('input[name="subject"]')
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

        # 設定標題和內容
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

    async def _set_subject(self, subject: str) -> None:
        """設定文章標題"""
        # 準備設定文章標題...

        # 模擬人類行為：隨機延遲
        # await self.page.wait_for_timeout(random.randint(500, 1500))

        await self.subject_input.wait_for(state="visible", timeout=5000)

        # 模擬人類輸入
        await self.subject_input.focus()
        # await self.page.wait_for_timeout(random.randint(100, 300))
        await self.subject_input.fill(subject)

        # 已設定文章標題: {subject}

    async def _set_description(self, description: str) -> None:
        """設定文章內容"""
        # 準備設定文章內容...

        # 模擬人類行為：在標題和內容之間的延遲
        # await self.page.wait_for_timeout(random.randint(800, 2000))

        # SimpleMDE 編輯器需要特殊處理
        await self.page.evaluate("""
            (description) => {
                const textarea = document.querySelector('textarea[name="description"]');
                const simplemde = $(textarea).data('simplemde');

                // 設定內容
                setTimeout(() => {
                    if (simplemde) {
                        simplemde.value(description);
                    } else {
                        textarea.value = description;
                    }
                }, 300);
            }
        """, description)

        # 等待內容設定完成
        await self.page.wait_for_timeout(1000)
        # 已設定文章內容

    async def _publish_article(self) -> bool:
        """發表文章"""
        # 準備發表文章...

        # 模擬人類行為：檢查內容後再提交的延遲
        # await self.page.wait_for_timeout(random.randint(1500, 3000))

        # 處理 reCAPTCHA
        if not await self._handle_recaptcha():
            return False

        # 點擊下拉選單
        await self._click_dropdown_toggle()
        
        # 點擊發表按鈕
        # await self._click_publish_button()

        # 等待頁面跳轉
        # return await self._wait_for_redirect()

    async def _handle_recaptcha(self) -> bool:
        """處理 reCAPTCHA"""
        recaptcha = ReCaptcha(self.page)
        recaptcha_handled = await recaptcha.handle_recaptcha()

        if not recaptcha_handled:
            # 自動處理 reCAPTCHA 失敗，切換到手動模式
            # 固定顯示瀏覽器，可以手動處理
            await recaptcha.wait_for_manual_recaptcha()

        return True

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
        """等待頁面跳轉"""
        try:
            await self.page.wait_for_url(
                lambda url: "/draft" not in url and "/create" not in url,
                timeout=15000
            )
            # 文章已發表，跳轉到: {current_url}
            return True
        except:
            # 發表狀態未知，當前頁面: {current_url}
            return False