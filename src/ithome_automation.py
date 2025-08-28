"""
iThome 鐵人賽登入自動化
使用 Class 架構
"""
from playwright.async_api import async_playwright, Browser, Page, Playwright
from .login import Login


class IThomeAutomation:
    """iThome 自動化操作類別"""

    def __init__(self, headless: bool = False):
        """
        初始化
        
        Args:
            headless: 是否使用 headless 模式（預設 False，會顯示瀏覽器）
        """
        self.headless = headless
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.page: Page = None

    async def login(self, account: str, password: str) -> bool:
        """
        登入 iThome 並導航到 ithelp
        
        Args:
            account: 使用者帳號
            password: 使用者密碼
            
        Returns:
            bool: 登入是否成功
        """
        # 啟動 Playwright
        self.playwright = await async_playwright().start()

        # 啟動瀏覽器
        self.browser = await self.playwright.webkit.launch(headless=self.headless)

        # 建立新頁面
        self.page = await self.browser.new_page()

        # 使用 Login class 執行登入
        login_handler = Login(self.page)
        login_success = await login_handler.login(account, password)
        
        if login_success:
            # 登入成功後導航到 ithelp.ithome.com.tw
            await self.page.goto("https://ithelp.ithome.com.tw/")
            print(f"已導航到 ithelp.ithome.com.tw")

            # 點擊登入/註冊按鈕
            login_register_button = self.page.locator('text=登入/註冊')
            await login_register_button.click()
            print(f"已點擊登入/註冊按鈕")
            
            # 等待頁面載入
            await self.page.wait_for_load_state("domcontentloaded")
            
            # 點擊 #dLabel (使用者下拉選單) - 選擇 a 標籤的那個
            dlabel_button = self.page.locator('a#dLabel')
            await dlabel_button.click()
            print(f"已點擊使用者下拉選單")
            
            # 點擊「我的主頁」
            my_page_link = self.page.locator('text=我的主頁')
            await my_page_link.click()
            print(f"已點擊我的主頁")

            return True
        return False

    async def close(self):
        """關閉瀏覽器"""
        if self.browser:
            await self.browser.close()
            print("瀏覽器已關閉")
        if self.playwright:
            await self.playwright.stop()
