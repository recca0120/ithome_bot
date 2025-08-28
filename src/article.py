"""
文章管理模組
"""
import random
from playwright.async_api import Page

from .recaptcha import ReCaptcha


class Article:
    """文章管理器"""

    def __init__(self, page: Page):
        """
        初始化文章管理器

        Args:
            page: Playwright 頁面物件
        """
        self.page = page
        # 初始化 locators
        self.subject_input = page.locator('input[name="subject"]')
        self.update_button = page.locator('#updateSubmitBtn')

    async def update_article(self, article_id: str, subject: str, description: str) -> bool:
        """
        更新文章內容

        Args:
            article_id: 文章 ID
            subject: 文章標題
            description: 文章內容

        Returns:
            bool: 是否更新成功
        """
        # 導航到編輯頁面
        await self._navigate_to_edit_page(article_id)

        # 等待頁面載入
        await self.page.wait_for_load_state("domcontentloaded")

        # 更新標題和內容
        await self._update_subject(subject)
        await self._update_description(description)

        # 提交更新
        return await self._submit_update()

    async def _navigate_to_edit_page(self, article_id: str) -> None:
        """導航到文章編輯頁面"""
        edit_url = f"https://ithelp.ithome.com.tw/articles/{article_id}/edit"
        await self.page.goto(edit_url)
        # 已導航到文章編輯頁面: {edit_url}

    async def _update_subject(self, subject: str) -> None:
        """更新文章標題"""
        # 準備更新文章標題...

        # 模擬人類行為：隨機延遲
        await self.page.wait_for_timeout(random.randint(500, 1500))

        await self.subject_input.wait_for(state="visible", timeout=5000)

        # 模擬人類輸入：先清空再輸入
        await self.subject_input.focus()
        await self.page.wait_for_timeout(random.randint(100, 300))
        await self.subject_input.fill("")
        await self.page.wait_for_timeout(random.randint(200, 500))
        await self.subject_input.fill(subject)

        # 已更新文章標題: {subject}

    async def _update_description(self, description: str) -> None:
        """更新文章內容"""
        # 準備更新文章內容...

        # 模擬人類行為：在標題和內容之間的延遲
        await self.page.wait_for_timeout(random.randint(800, 2000))

        # SimpleMDE 編輯器需要特殊處理
        await self.page.evaluate("""
            (description) => {
                const textarea = document.querySelector('textarea[name="description"]');
                const simplemde = $(textarea).data('simplemde');

                // 先清空內容
                if (simplemde) {
                    simplemde.value('');
                } else {
                    textarea.value = '';
                }

                // 模擬延遲後設定內容
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
        # 已更新文章內容

    async def _submit_update(self) -> bool:
        """提交更新"""
        # 準備提交更新...

        # 模擬人類行為：檢查內容後再提交的延遲
        await self.page.wait_for_timeout(random.randint(1500, 3000))

        # 處理 reCAPTCHA
        if not await self._handle_recaptcha():
            return False

        # 點擊更新按鈕
        await self._click_update_button()

        # 等待頁面跳轉
        return await self._wait_for_redirect()

    async def _handle_recaptcha(self) -> bool:
        """處理 reCAPTCHA"""
        recaptcha = ReCaptcha(self.page)
        recaptcha_handled = await recaptcha.handle_recaptcha()

        if not recaptcha_handled:
            # 自動處理 reCAPTCHA 失敗，切換到手動模式
            # 固定顯示瀏覽器，可以手動處理
            await recaptcha.wait_for_manual_recaptcha()

        return True

    async def _click_update_button(self) -> None:
        """點擊更新按鈕"""
        await self.update_button.wait_for(state="visible", timeout=5000)
        await self.update_button.click()
        # 已點擊更新按鈕

    async def _wait_for_redirect(self) -> bool:
        """等待頁面跳轉"""
        try:
            await self.page.wait_for_url(
                lambda url: "/edit" not in url,
                timeout=15000
            )
            # 文章已更新，跳轉到: {current_url}
            return True
        except:
            # 更新狀態未知，當前頁面: {current_url}
            return False