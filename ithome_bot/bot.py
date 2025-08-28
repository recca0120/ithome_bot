"""
iThome 鐵人賽登入自動化
使用 Class 架構
"""
import base64
import json
from pathlib import Path

from playwright.async_api import Page

from .login import Login
from .article import Article


class Bot:
    """Bot 操作類別"""

    def __init__(self, page: Page, cookies_file: str = "cookies.txt"):
        """
        初始化

        Args:
            page: Playwright 的 Page 物件
            cookies_file: 儲存 cookies 的檔案路徑（預設為當前目錄的 cookies.txt）
        """
        self.page = page
        self.cookies_file = Path(cookies_file)

    async def login(self, account: str, password: str) -> bool:
        """
        登入 iThome

        Args:
            account: 使用者帳號
            password: 使用者密碼

        Returns:
            bool: 登入是否成功
        """
        # 使用 Login class 執行登入
        login = Login(self.page)
        login_success = await login.login(account, password)

        return login_success

    async def update_article(self, article_data: dict) -> bool:
        """
        更新文章內容

        Args:
            article_data: 文章資料字典，包含:
                - article_id: 文章 ID
                - subject: 文章標題
                - description: 文章內容

        Returns:
            bool: 是否更新成功
        """
        # 使用 Article class 處理文章更新
        article = Article(self.page)
        return await article.update_article(article_data)

    async def save_cookies(self) -> None:
        """
        儲存當前的 cookies 到檔案（Base64 編碼格式）
        """

        # 取得所有 cookies
        cookies = await self.page.context.cookies()

        # 確保目錄存在
        self.cookies_file.parent.mkdir(parents=True, exist_ok=True)

        # 將 cookies 轉換為 JSON 字串，然後進行 Base64 編碼
        cookies_json = json.dumps(cookies, ensure_ascii=False)
        cookies_encoded = base64.b64encode(cookies_json.encode('utf-8')).decode('ascii')

        # 儲存到檔案
        with open(self.cookies_file, 'w', encoding='utf-8') as f:
            f.write(cookies_encoded)

        # Cookies 已儲存

    async def load_cookies(self) -> bool:
        """
        從檔案載入 cookies（Base64 編碼格式）

        Returns:
            bool: 是否成功載入 cookies
        """
        if not self.cookies_file.exists():
            # 找不到 cookies 檔案
            return False

        try:
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookies_encoded = f.read().strip()

            # Base64 解碼並轉換為 JSON
            cookies_json = base64.b64decode(cookies_encoded).decode('utf-8')
            cookies = json.loads(cookies_json)

            if self.page and cookies:
                await self.page.context.add_cookies(cookies)
                # 已載入 cookies
                return True
        except Exception:
            # 載入 cookies 失敗
            pass

        return False


