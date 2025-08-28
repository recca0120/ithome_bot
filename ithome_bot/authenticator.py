"""
iThome 登入功能
"""
from playwright.async_api import Page


class Authenticator:
    """認證器類別"""

    def __init__(self, page: Page):
        """
        初始化

        Args:
            page: Playwright 的 Page 物件
        """
        self.page = page

        # 登入相關 locators
        self.account_input = page.locator('#account')
        self.password_input = page.locator('#password')
        self.remember_checkbox = page.locator('input[name="remember"]')
        self.login_button = page.locator('#loginBtn')

        # Profile 相關 locators
        self.login_register_button = page.locator('text=登入/註冊')
        self.user_dropdown = page.locator('a#dLabel')
        self.my_page_link = page.locator('text=我的主頁')

    async def login(self, account: str, password: str) -> bool:
        """
        執行登入
        先嘗試透過 ithelp_login，如果失敗則使用帳密登入
        最後都會導航到使用者主頁

        Args:
            account: 使用者帳號
            password: 使用者密碼

        Returns:
            bool: 登入是否成功
        """
        # 先嘗試透過 ithelp 登入
        login_success = await self._ithelp_login()

        # 如果 ithelp 登入失敗，則使用帳密登入
        if not login_success:
            # 填寫表單並送出（包含導航到登入頁面、等待跳轉和執行 ithelp_login）
            login_success = await self._submit_login(account, password)

        # 最後導航到使用者主頁
        if login_success:
            await self._navigate_to_user_profile()

        return login_success

    async def _submit_login(self, account: str, password: str) -> bool:
        """
        導航到登入頁面、填寫登入表單並送出

        Args:
            account: 使用者帳號
            password: 使用者密碼

        Returns:
            bool: 登入是否成功
        """
        # 導航到登入頁面
        await self.page.goto("https://member.ithome.com.tw/login")

        # 等待頁面載入完畢
        await self.page.wait_for_load_state("domcontentloaded")

        # 填寫帳號
        await self.account_input.fill(account)

        # 填寫密碼
        await self.password_input.fill(password)

        # 勾選「記住我」checkbox
        is_checked = await self.remember_checkbox.is_checked()
        if not is_checked:
            await self.remember_checkbox.check()

        # 點擊登入按鈕
        await self.login_button.click()

        # 等待頁面跳轉
        await self.page.wait_for_load_state("networkidle")

        # 登入成功後再次執行 ithelp_login
        return await self._ithelp_login()

    async def _ithelp_login(self) -> bool:
        """
        導航到 ithelp.ithome.com.tw 並進行登入
        如果已經登入（找到 user_dropdown），返回 True

        Returns:
            bool: 登入是否成功（如果 URL 是登入頁面則返回 False）
        """
        # 導航到 ithelp.ithome.com.tw
        await self.page.goto("https://ithelp.ithome.com.tw/")
        # 等待頁面載入
        await self.page.wait_for_load_state("domcontentloaded")

        # 檢查是否已經登入（是否存在使用者下拉選單）
        # 使用 is_visible() 立即檢查，不等待
        if await self.user_dropdown.is_visible():
            # 已經登入，直接返回成功
            return True

        # 點擊登入/註冊按鈕
        await self.login_register_button.click()

        # 等待頁面載入
        await self.page.wait_for_load_state("domcontentloaded")

        # 檢查 URL 是否仍在登入頁面
        current_url = self.page.url
        if "https://member.ithome.com.tw/login" in current_url:
            return False

        # 再次檢查是否已經登入
        if await self.user_dropdown.is_visible():
            return True

        return False

    async def _navigate_to_user_profile(self) -> None:
        """
        導航到使用者主頁

        執行流程：
        1. 點擊使用者下拉選單
        2. 點擊我的主頁
        """
        # 點擊使用者下拉選單
        await self.user_dropdown.click()
        # 已點擊使用者下拉選單

        # 點擊「我的主頁」
        await self.my_page_link.click()
        # 已點擊我的主頁
