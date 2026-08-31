"""
iThome 鐵人賽登入自動化
使用 Class 架構
"""
import base64
import json
import os
from pathlib import Path

from playwright.async_api import Page

from .article import Article
from .authenticator import Authenticator
from .article_updater import ArticleUpdater
from .article_creator import ArticleCreator


class Client:
    """客戶端操作類別"""

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
        # 使用 Authenticator class 執行登入
        auth = Authenticator(self.page)
        login_success = await auth.login(account, password)

        return login_success

    async def create_article(self, article_data: dict | Article) -> str | None:
        """
        建立新文章

        Args:
            article_data: 文章資料，dict 或 Article 物件都可以（Article 通常
                來自 markdown_parser 這類 parser 的輸出）。dict 格式包含:
                - category_id: 分類 ID（例如鐵人賽的分類）
                - subject: 文章標題
                - description: 文章內容
                - tags: 選填，要另外加上的自訂 tag 清單

        Returns:
            str | None: 成功時回傳 article_id，失敗時回傳 None
        """
        if isinstance(article_data, Article):
            article_data = article_data.to_dict()
        # 使用 ArticleCreator class 處理文章建立
        creator = ArticleCreator(self.page)
        return await creator.create(article_data)

    async def update_article(self, article_data: dict | Article) -> str | None:
        """
        更新文章內容

        Args:
            article_data: 文章資料，dict 或 Article 物件都可以（Article 通常
                來自 markdown_parser 這類 parser 的輸出，記得設定
                article_id，否則轉成 dict 後會缺這個必要欄位）。dict 格式
                包含:
                - article_id: 文章 ID
                - subject: 文章標題
                - description: 文章內容
                - tags: 選填，要另外加上的自訂 tag 清單

        Returns:
            str | None: 成功時回傳 article_id，失敗時回傳 None
        """
        if isinstance(article_data, Article):
            article_data = article_data.to_dict()
        # 使用 ArticleUpdater class 處理文章更新
        updater = ArticleUpdater(self.page)
        return await updater.update(article_data)

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

        檔案不存在時，會嘗試從環境變數 ITHOME_COOKIES 讀取（內容跟
        cookies.txt 檔案內容一樣，即 save_cookies() 存出來的 base64
        字串），存成檔案後再載入。CI 環境常見用法：把 cookies.txt 的
        內容設成 Secret，跑的時候不需要先手動產生這個檔案。

        Returns:
            bool: 是否成功載入 cookies
        """
        if not self.cookies_file.exists():
            env_cookies = os.getenv('ITHOME_COOKIES')
            if not env_cookies:
                # 找不到 cookies 檔案，也沒有 ITHOME_COOKIES 環境變數
                return False
            self.cookies_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                f.write(env_cookies)

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


