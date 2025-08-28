"""
iThome 鐵人賽登入自動化
使用 Class 架構
"""
import json
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, Playwright
from .utils import base_path
from .login import Login
from .profile import Profile


class IThomeAutomation:
    """iThome 自動化操作類別"""

    def __init__(self, headless: bool = False, cookies_file: str = None):
        """
        初始化
        
        Args:
            headless: 是否使用 headless 模式（預設 False，會顯示瀏覽器）
            cookies_file: 儲存 cookies 的檔案路徑（預設為專案根目錄下的 cookies.json）
        """
        self.headless = headless
        # 如果沒有指定 cookies_file，使用專案根目錄下的 cookies.json
        if cookies_file is None:
            self.cookies_file = base_path() / "cookies.json"
        else:
            self.cookies_file = Path(cookies_file).resolve()
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
    
    async def goto_article_edit(self, article_id: str) -> None:
        """
        導航到文章編輯頁面
        
        Args:
            article_id: 文章 ID
        """
        if not self.page:
            raise RuntimeError("頁面尚未初始化，請先執行 initialize() 方法")
        
        edit_url = f"https://ithelp.ithome.com.tw/articles/{article_id}/edit"
        await self.page.goto(edit_url)
        print(f"已導航到文章編輯頁面: {edit_url}")
        
        # 等待頁面載入
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def save_cookies(self) -> None:
        """
        儲存當前的 cookies 到檔案
        """
        if not self.page:
            raise RuntimeError("頁面尚未初始化")
        
        # 取得所有 cookies
        cookies = await self.page.context.cookies()
        
        # 確保目錄存在
        self.cookies_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 儲存到檔案
        with open(self.cookies_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        
        print(f"Cookies 已儲存到 {self.cookies_file.absolute()}")
    
    async def load_cookies(self) -> bool:
        """
        從檔案載入 cookies
        
        Returns:
            bool: 是否成功載入 cookies
        """
        if not self.cookies_file.exists():
            print(f"找不到 cookies 檔案: {self.cookies_file.absolute()}")
            return False
        
        try:
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            if self.page and cookies:
                await self.page.context.add_cookies(cookies)
                print(f"已從 {self.cookies_file.absolute()} 載入 {len(cookies)} 個 cookies")
                return True
        except Exception as e:
            print(f"載入 cookies 失敗: {e}")
        
        return False

    async def close(self):
        """關閉瀏覽器"""
        if self.browser:
            await self.browser.close()
            print("瀏覽器已關閉")
        if self.playwright:
            await self.playwright.stop()
