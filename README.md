# iThome Bot

iThome 鐵人賽文章更新自動化工具

## 功能特點

- 🤖 自動化登入 iThome 網站
- 📝 批量更新鐵人賽文章
- 🍪 自動儲存和載入 cookies
- 🔐 安全的密碼處理（支援環境變數）
- 🎯 簡單易用的命令列介面

## 安裝方式

### 方法 1: 從原始碼安裝（開發模式）

```bash
# Clone 專案
git clone https://github.com/yourusername/ironman-bot.git
cd ironman-bot

# 安裝 package（開發模式）
pip install -e .

# 安裝 playwright 瀏覽器
playwright install
```

### 方法 2: 直接安裝

```bash
# 安裝 package
pip install ithome-bot

# 安裝 playwright 瀏覽器
playwright install
```

## 使用方法

### 設定環境變數

建立 `.env` 檔案或設定環境變數：

```bash
export ITHOME_ACCOUNT=your_account
export ITHOME_PASSWORD=your_password
```

或建立 `.env` 檔案：

```
ITHOME_ACCOUNT=your_account
ITHOME_PASSWORD=your_password
```

### 執行命令

```bash
# 基本用法
ithome-bot <article_id> "<subject>" <description_file>

# 範例
ithome-bot 10376177 "Day 01 Python 環境設置" day01.md

# 使用命令列參數提供帳密（不建議，會在歷史記錄中顯示）
ithome-bot 10376177 "Day 01 標題" day01.md --account myaccount --password mypass
```

### 參數說明

- `article_id`: iThome 文章 ID（必填）
- `subject`: 文章標題（必填）
- `description_file`: 文章內容的 Markdown 檔案路徑（必填）
- `--account`: iThome 帳號（選填，預設從環境變數讀取）
- `--password`: iThome 密碼（選填，預設從環境變數讀取）

## 在其他專案中使用

### 作為 Python 模組使用

```python
import asyncio
from playwright.async_api import async_playwright
from ithome_bot import Client

async def update_my_article():
    # 啟動瀏覽器
    playwright = await async_playwright().start()
    browser = await playwright.webkit.launch(headless=False)
    page = await browser.new_page()
    
    try:
        # 建立 Client 實例
        client = Client(page)
        
        # 登入
        await client.login("account", "password")
        
        # 更新文章（tags 選填，會另外加上去，不會清掉既有的 tag）
        article_data = {
            "article_id": "10376177",
            "subject": "文章標題",
            "description": "文章內容...",
            "tags": ["PHP", "TDD"]
        }
        success = await client.update_article(article_data)

        # 建立新文章（鐵人賽），category_id 是系列 ID
        article_data = {
            "category_id": "8446",
            "subject": "文章標題",
            "description": "文章內容...",
            "tags": ["PHP", "TDD"]
        }
        article_id = await client.create_article(article_data)

    finally:
        await browser.close()
        await playwright.stop()

# 執行
asyncio.run(update_my_article())
```

`tags` 是選填欄位，`create_article`／`update_article` 都支援；沒有帶
`tags` 就完全不動 tag 欄位。目前的 CLI（`ithome-bot` 指令）沒有開放
`--tags` 參數，只能透過程式化呼叫使用。

### 複製到其他專案

如果不想安裝 package，可以直接複製以下檔案到你的專案：

1. 複製整個 `ithome_bot/` 目錄到你的專案
2. 安裝相依套件：`pip install playwright python-dotenv click`
3. 使用 `python -m ithome_bot.cli` 執行

## 系統需求

- Python 3.8+
- playwright
- python-dotenv
- click

## 注意事項

1. 第一次執行時需要手動處理 reCAPTCHA 驗證
2. 登入成功後會自動儲存 cookies，下次執行時會自動載入
3. cookies 檔案會儲存在專案根目錄的 `cookies.txt`
4. 請勿將含有帳密的 `.env` 檔案提交到版本控制系統

## License

MIT License

## 作者

Your Name

## 貢獻

歡迎提交 Issue 和 Pull Request！