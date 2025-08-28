"""
iThome 鐵人賽登入自動化
使用 Class 架構
"""
from playwright.async_api import async_playwright, Browser, Page, Playwright
from .login import Login
from .profile import Profile


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
    
    async def initialize(self):
        """
        初始化瀏覽器和頁面
        """
        # 啟動 Playwright
        self.playwright = await async_playwright().start()
        
        # 啟動瀏覽器
        self.browser = await self.playwright.webkit.launch(headless=self.headless)
        
        # 建立新頁面
        self.page = await self.browser.new_page()

    async def login(self, account: str, password: str) -> bool:
        """
        登入 iThome
        
        Args:
            account: 使用者帳號
            password: 使用者密碼
            
        Returns:
            bool: 登入是否成功
        """
        if not self.page:
            await self.initialize()
        
        # 使用 Login class 執行登入
        login_handler = Login(self.page)
        return await login_handler.login(account, password)
    
    async def goto_user_profile(self) -> None:
        """
        導航到使用者主頁
        需要先執行 login() 成功後才能呼叫
        """
        if not self.page:
            raise RuntimeError("尚未登入，請先執行 login() 方法")
        
        # 使用 Profile class 
        profile = Profile(self.page)
        # 導航到 ithelp
        await profile.goto_ithelp()
        # 執行 ithelp 登入
        await profile.ithelp_login()
        # 導航到使用者主頁
        await profile.navigate_to_user_profile()

    async def close(self):
        """關閉瀏覽器"""
        if self.browser:
            await self.browser.close()
            print("瀏覽器已關閉")
        if self.playwright:
            await self.playwright.stop()
