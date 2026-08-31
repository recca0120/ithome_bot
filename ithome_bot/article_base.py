"""
文章操作基類模組
"""
import re
from abc import ABC, abstractmethod
from playwright.async_api import Page

from .recaptcha import ReCaptcha


class ArticleBase(ABC):
    """文章操作基類（抽象類別）"""

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
            await self._update_simplemde_content('')
            await self.page.wait_for_timeout(300)

        # 設定新內容
        await self._update_simplemde_content(description)

        # 等待內容設定完成
        await self.page.wait_for_timeout(1000)
        # 已設定文章內容
    
    async def _update_simplemde_content(self, content: str) -> None:
        """
        更新 SimpleMDE 編輯器內容
        
        Args:
            content: 要設定的內容（空字串表示清空）
        """
        await self.page.evaluate("""
            (content) => {
                const textarea = document.querySelector('textarea[name="description"]');
                const simplemde = $(textarea).data('simplemde');
                
                // 優先使用 SimpleMDE API，它會自動同步到 textarea
                if (simplemde) {
                    simplemde.value(content);
                } else {
                    // 如果 SimpleMDE 不存在，直接設定 textarea
                    textarea.value = content;
                }
            }
        """, content)

    async def _set_tags(self, tags: list[str]) -> None:
        """
        新增自訂 tag（共用方法）

        Tag 欄位是 select2（多選、允許輸入新值）。原本嘗試用模擬打字 +
        Enter 操作 UI，但這個 select2 的「新增 tag 變成已選取」是延遲觸發的
        （要等下一次 Enter 或其他互動才會把 selected 標成 true），連續新增
        兩個 tag 時常常漏掉，時序不穩定、不能單靠加長等待時間解決。

        改成直接操作底層的 <select multiple id="tags">：手動 new Option()
        加進去（若已存在就直接標 selected），再用 jQuery 觸發 change 事件讓
        select2 重繪。這樣不管加幾個 tag 都是同一個 tick 內完成，不會有
        「這個 tag 有沒有真的被選到」的競態問題。既有的 tag（例如鐵人賽
        自動掛的「18th鐵人賽」）不會被清掉，這裡只會新增，不會清空重來。

        Args:
            tags: 要加入的 tag 清單
        """
        if not tags:
            return

        await self.page.evaluate(
            """(tags) => {
                const select = document.querySelector('#tags');
                for (const tag of tags) {
                    let opt = Array.from(select.options).find(o => o.value === tag);
                    if (!opt) {
                        opt = new Option(tag, tag, true, true);
                        select.add(opt);
                    } else {
                        opt.selected = true;
                    }
                }
                $(select).trigger('change');
            }""",
            tags,
        )
        await self.page.wait_for_timeout(300)

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

    async def _submit(self) -> str | None:
        """
        模板方法：提交表單的通用流程
        
        Returns:
            str | None: 成功時回傳 article_id，失敗時回傳 None
        """
        # 準備提交...

        # 模擬人類行為：檢查內容後再提交的延遲
        # await self.page.wait_for_timeout(random.randint(1500, 3000))

        # 處理 reCAPTCHA
        if not await self._handle_recaptcha():
            return None

        # 執行具體的提交動作（由子類實作）
        await self._perform_submit_action()

        # 等待頁面跳轉（由子類實作）
        if await self._wait_for_submit_redirect():
            # 從 URL 中提取 article_id
            return self._extract_article_id_from_url()
        
        return None
    
    @abstractmethod
    async def _perform_submit_action(self) -> None:
        """
        執行具體的提交動作（子類必須實作此方法）
        """
        pass
    
    @abstractmethod
    async def _wait_for_submit_redirect(self) -> bool:
        """
        等待提交後的頁面跳轉（子類必須實作此方法）
        
        Returns:
            bool: 是否成功跳轉
        """
        pass

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
    
    def _extract_article_id_from_url(self) -> str | None:
        """
        從當前 URL 中提取文章 ID
        
        Returns:
            str | None: 文章 ID，若無法提取則回傳 None
        """
        current_url = self.page.url
        # 匹配 /articles/{article_id} 的模式
        match = re.search(r'/articles/(\d+)', current_url)
        if match:
            return match.group(1)
        return None