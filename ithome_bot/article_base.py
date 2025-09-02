"""
文章操作基類模組
"""
from playwright.async_api import Page

from .recaptcha import ReCaptcha


class ArticleBase:
    """文章操作基類"""

    def __init__(self, page: Page):
        """
        初始化文章操作基類

        Args:
            page: Playwright 頁面物件
        """
        self.page = page
        # 共用的 locators
        self.subject_input = page.locator('input[name="subject"]')

    async def _set_subject(self, subject: str, clear_first: bool = False) -> None:
        """
        設定文章標題（共用方法）

        Args:
            subject: 文章標題
            clear_first: 是否先清空內容
        """
        # 準備設定文章標題...

        # 模擬人類行為：隨機延遲
        # await self.page.wait_for_timeout(random.randint(500, 1500))

        await self.subject_input.wait_for(state="visible", timeout=5000)

        # 模擬人類輸入
        await self.subject_input.focus()
        # await self.page.wait_for_timeout(random.randint(100, 300))
        
        if clear_first:
            await self.subject_input.fill("")
            # await self.page.wait_for_timeout(random.randint(200, 500))
        
        await self.subject_input.fill(subject)

        # 已設定文章標題: {subject}

    async def _set_description(self, description: str, clear_first: bool = False) -> None:
        """
        設定文章內容（共用方法）

        Args:
            description: 文章內容
            clear_first: 是否先清空內容
        """
        # 準備設定文章內容...

        # 模擬人類行為：在標題和內容之間的延遲
        # await self.page.wait_for_timeout(random.randint(800, 2000))

        # SimpleMDE 編輯器需要特殊處理
        if clear_first:
            # 先清空內容
            await self.page.evaluate("""
                () => {
                    const textarea = document.querySelector('textarea[name="description"]');
                    const simplemde = $(textarea).data('simplemde');
                    
                    if (simplemde) {
                        simplemde.value('');
                    } else {
                        textarea.value = '';
                    }
                }
            """)
            await self.page.wait_for_timeout(300)

        # 設定新內容
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

    async def _handle_recaptcha(self) -> bool:
        """
        處理 reCAPTCHA（共用方法）

        Returns:
            bool: 是否成功處理
        """
        recaptcha = ReCaptcha(self.page)
        recaptcha_handled = await recaptcha.handle_recaptcha()

        if not recaptcha_handled:
            # 自動處理 reCAPTCHA 失敗，切換到手動模式
            # 固定顯示瀏覽器，可以手動處理
            await recaptcha.wait_for_manual_recaptcha()

        return True

    async def _submit(self) -> bool:
        """
        模板方法：提交表單的通用流程
        
        Returns:
            bool: 是否成功提交
        """
        # 準備提交...

        # 模擬人類行為：檢查內容後再提交的延遲
        # await self.page.wait_for_timeout(random.randint(1500, 3000))

        # 處理 reCAPTCHA
        if not await self._handle_recaptcha():
            return False

        # 執行具體的提交動作（由子類實作）
        await self._perform_submit_action()

        # 等待頁面跳轉（由子類決定排除模式）
        return await self._wait_for_redirect(self._get_redirect_exclude_patterns())
    
    async def _perform_submit_action(self) -> None:
        """
        執行具體的提交動作（子類需要覆寫此方法）
        """
        raise NotImplementedError("子類必須實作 _perform_submit_action 方法")
    
    def _get_redirect_exclude_patterns(self) -> list:
        """
        取得跳轉時要排除的 URL 模式（子類可覆寫）
        
        Returns:
            list: 要排除的 URL 模式列表
        """
        return []

    async def _wait_for_redirect(self, exclude_patterns: list = None, timeout: int = 15000) -> bool:
        """
        等待頁面跳轉（共用方法）

        Args:
            exclude_patterns: 要排除的 URL 模式列表
            timeout: 超時時間（毫秒）

        Returns:
            bool: 是否成功跳轉
        """
        if exclude_patterns is None:
            exclude_patterns = []

        try:
            await self.page.wait_for_url(
                lambda url: all(pattern not in url for pattern in exclude_patterns),
                timeout=timeout
            )
            # 頁面已跳轉
            return True
        except:
            # 跳轉狀態未知
            return False