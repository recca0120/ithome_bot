# iThome 鐵人賽文章更新 Bot

## 專案簡介
使用 Playwright 開發的自動化工具，能夠將本地撰寫的 Markdown 文章更新到 iThome 鐵人賽平台。採用 TDD (Test-Driven Development) 方法論開發，確保程式碼品質與穩定性。

## 核心功能
1. **自動登入**: 支援帳號密碼登入與 Cookie 持久化
2. **文章更新**: 根據文章 ID 更新標題與內容
3. **reCAPTCHA 處理**: 自動偵測並提供手動處理機制
4. **CLI 介面**: 使用 Click 框架提供友善的命令列操作

## 系統架構

### 模組結構
```
src/
├── ithome_automation.py  # 主要自動化控制器
├── login.py              # 登入功能模組
├── profile.py            # 使用者檔案管理
├── article.py            # 文章編輯功能
├── recaptcha.py          # reCAPTCHA 處理器
└── utils.py              # 工具函式
```

### 類別設計
- **IThomeAutomation**: 主控制器，協調各模組運作
- **Login**: 處理登入流程
- **Profile**: 管理使用者檔案與導航
- **Article**: 文章更新邏輯
- **ReCaptcha**: reCAPTCHA 偵測與處理

## 專案結構
```
ironman-bot/
├── src/                      # 源碼目錄
│   ├── __init__.py
│   ├── ithome_automation.py
│   ├── login.py
│   ├── profile.py
│   ├── article.py
│   ├── recaptcha.py
│   └── utils.py
├── tests/                    # 測試目錄
│   ├── conftest.py          # pytest 設定與 fixtures
│   ├── test_login.py        # 登入測試
│   ├── test_article.py     # 文章更新測試
│   └── fixtures/            # 測試資料
│       └── day01-python-environment-setup.md
├── main.py                  # CLI 主程式
├── .env.example             # 環境變數範例
├── requirements.txt         # Python 套件依賴
├── pytest.ini               # pytest 設定
└── cookies.txt              # Cookie 儲存檔案（自動產生）
```

## 環境設定

### 1. 安裝依賴
```bash
pip install -r requirements.txt
playwright install webkit
```

### 2. 設定環境變數
複製 `.env.example` 為 `.env` 並填入帳號密碼：
```bash
cp .env.example .env
```

編輯 `.env`：
```
ITHOME_ACCOUNT=your_account
ITHOME_PASSWORD=your_password
```

## 使用方式

### CLI 命令
```bash
# 更新單篇文章
python main.py <article_id> "<標題>" <markdown檔案路徑>

# 範例
python main.py 10376177 "Day 01 Python 環境設置" tests/fixtures/day01-python-environment-setup.md
```

### 程式化使用
```python
import asyncio
from src.ithome_automation import IThomeAutomation

async def update_article():
    automation = IThomeAutomation()
    
    try:
        # 初始化
        await automation.initialize()
        
        # 載入 cookies 或登入
        if not await automation.load_cookies():
            await automation.login(account, password)
            await automation.save_cookies()
        
        # 導航到使用者主頁
        await automation.goto_user_profile()
        
        # 更新文章
        success = await automation.update_article(
            article_id="10376177",
            subject="文章標題",
            description="文章內容..."
        )
        
    finally:
        await automation.close()

asyncio.run(update_article())
```

## 工作流程

### 1. 初始化階段
- 啟動 Playwright 與 Webkit 瀏覽器（顯示模式）
- 建立新的瀏覽器頁面

### 2. 認證階段
- 嘗試載入已儲存的 cookies
- 若 cookies 無效或不存在：
  - 執行登入流程
  - 儲存新的 cookies 供下次使用

### 3. 導航階段
- 前往 ithelp.ithome.com.tw
- 確認登入狀態
- 導航到使用者主頁

### 4. 更新階段
- 導航到指定文章的編輯頁面
- 更新文章標題
- 使用 SimpleMDE 編輯器更新內容
- 處理 reCAPTCHA（如有）
- 提交更新

## 技術特色

### Cookie 持久化
- 使用 Base64 編碼儲存 cookies
- 自動載入與儲存機制
- 減少重複登入需求

### reCAPTCHA 處理
- 自動偵測 reCAPTCHA 存在
- 自動捲動到 reCAPTCHA 位置
- 嘗試自動點擊 checkbox
- 提供手動處理時間（30秒）

### 人性化操作
- 隨機延遲模擬真人操作
- 漸進式內容輸入
- 適當的等待時間

### 錯誤處理
- 完善的異常捕獲
- 明確的錯誤訊息
- 自動資源清理

## 測試架構

### Fixtures
- **credential**: 提供測試用帳號密碼
- **automation**: 初始化並設定自動化實例

### 測試覆蓋
- 登入功能測試
- Cookie 載入/儲存測試
- 文章更新測試
- reCAPTCHA 處理測試

### 執行測試
```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/test_login.py::test_user_can_login_to_ithome

# 顯示詳細輸出
pytest -v -s
```

## 技術棧
- **Python 3.10+**: 主要開發語言
- **Playwright**: 瀏覽器自動化框架
- **pytest**: 測試框架
- **pytest-asyncio**: 非同步測試支援
- **Click**: CLI 框架
- **python-dotenv**: 環境變數管理

## 注意事項
1. **瀏覽器模式**: 固定使用顯示模式（headless=False）以便處理 reCAPTCHA
2. **帳號安全**: 不要將 .env 檔案提交到版本控制
3. **文章權限**: 只能更新自己帳號的文章
4. **請求頻率**: 避免過於頻繁的操作以防被偵測為機器人
5. **SimpleMDE**: 文章編輯使用 SimpleMDE 編輯器，需特殊處理

## 開發指引

### 新增功能
1. 在對應模組中新增方法
2. 撰寫單元測試
3. 更新整合測試
4. 更新文檔

### 除錯技巧
- 使用顯示模式觀察操作過程
- 檢查 cookies.txt 是否正確儲存
- 確認環境變數是否正確設定
- 查看瀏覽器開發者工具的網路請求

## 未來改進方向
- [ ] 支援批次更新多篇文章
- [ ] 加入重試機制
- [ ] 支援草稿儲存
- [ ] 加入進度顯示
- [ ] 支援其他瀏覽器引擎
- [ ] 加入 CI/CD 整合

## 貢獻指南
1. Fork 專案
2. 建立功能分支
3. 撰寫測試與實作
4. 確保所有測試通過
5. 提交 Pull Request

## 授權
MIT License