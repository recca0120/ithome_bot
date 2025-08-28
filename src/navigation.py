"""
iThome 導航功能
"""
from playwright.async_api import Page


class Navigation:
    """導航功能類別"""

    def __init__(self, page: Page):
        """
        初始化
        
        Args:
            page: Playwright 的 Page 物件
        """
        self.page = page
        
        # 定義 locators
        self.login_register_button = page.locator('text=登入/註冊')
        self.user_dropdown = page.locator('a#dLabel')
        self.my_page_link = page.locator('text=我的主頁')

    async def goto_ithelp(self) -> None:
        """
        導航到 ithelp.ithome.com.tw
        """
        await self.page.goto("https://ithelp.ithome.com.tw/")
        print(f"已導航到 ithelp.ithome.com.tw")
        # 等待頁面載入
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def ithelp_login(self) -> None:
        """
        登入到 ithelp.ithome.com.tw
        
        執行流程：
        1. 導航到 ithelp.ithome.com.tw
        2. 點擊登入/註冊按鈕
        """
        # 導航到 ithelp.ithome.com.tw
        await self.goto_ithelp()

        # 點擊登入/註冊按鈕
        await self.login_register_button.click()
        print(f"已點擊登入/註冊按鈕")
        
        # 等待頁面載入
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def navigate_to_user_profile(self) -> None:
        """
        導航到使用者主頁
        
        執行流程：
        1. 點擊使用者下拉選單
        2. 點擊我的主頁
        """
        # 點擊使用者下拉選單
        await self.user_dropdown.click()
        print(f"已點擊使用者下拉選單")
        
        # 點擊「我的主頁」
        await self.my_page_link.click()
        print(f"已點擊我的主頁")