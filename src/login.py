"""
iThome 登入功能
"""
from playwright.async_api import Page


class Login:
    """登入功能類別"""

    def __init__(self, page: Page):
        """
        初始化
        
        Args:
            page: Playwright 的 Page 物件
        """
        self.page = page
        
        # 定義所有 locators
        self.account_input = page.locator('#account')
        self.password_input = page.locator('#password')
        self.remember_checkbox = page.locator('input[name="remember"]')
        self.login_button = page.locator('#loginBtn')

    async def login(self, account: str, password: str) -> bool:
        """
        執行登入
        
        Args:
            account: 使用者帳號
            password: 使用者密碼
            
        Returns:
            bool: 登入是否成功
        """
        # 導航到登入頁面
        await self.page.goto("https://member.ithome.com.tw/login")
        # 已開啟登入頁面

        # 等待頁面載入完畢
        await self.page.wait_for_load_state("domcontentloaded")

        # 填寫帳號
        await self.account_input.fill(account)
        # 已填寫帳號: {account}

        # 填寫密碼
        await self.password_input.fill(password)
        # 已填寫密碼

        # 勾選「記住我」checkbox
        is_checked = await self.remember_checkbox.is_checked()
        if not is_checked:
            await self.remember_checkbox.check()
            # 已勾選「記住我」

        # 點擊登入按鈕
        await self.login_button.click()
        # 已點擊登入按鈕

        # 檢查是否登入成功
        return await self.is_logged_in()

    async def is_logged_in(self) -> bool:
        """
        檢查是否已登入
        
        Returns:
            bool: 是否已登入
        """
        if not self.page:
            return False

        current_url = self.page.url
        # 檢查是否在個人檔案頁面
        if "https://member.ithome.com.tw/profile/account" in current_url:
            # 登入成功！當前頁面: {current_url}
            return True
        else:
            # 登入失敗，當前頁面: {current_url}
            return False