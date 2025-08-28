# 鐵人賽文章更新 Bot - TDD 開發計畫

## 專案目的
開發一個使用 Playwright 的自動化工具，能夠將本地寫好的 Markdown 文章批次更新到 iThome 鐵人賽平台。採用 TDD (Test-Driven Development) 方法論進行開發，確保程式品質。

## 核心功能需求
1. **自動登入**: 使用 Playwright 自動登入 iThome 網站
2. **文章更新**: 根據文章 ID 更新對應的文章內容
3. **批次處理**: 支援多篇文章的批次更新
4. **錯誤處理**: 完善的錯誤處理和重試機制

## TDD 開發流程
遵循「紅燈-綠燈-重構」循環：
1. **紅燈** (Red): 先寫失敗的測試
2. **綠燈** (Green): 寫最少的程式碼讓測試通過
3. **重構** (Refactor): 優化程式碼但保持測試通過

## 實作清單

### Phase 1: 專案設置
- [ ] 建立專案目錄結構
- [ ] 安裝 Playwright 和測試框架
- [ ] 設定環境變數檔案 (.env)
- [ ] 建立文章目錄和對應表

### Phase 2: TDD - 登入功能
- [ ] **紅燈**: 撰寫登入測試 `test_login.py`
  - 測試開啟瀏覽器
  - 測試導航到 iThome 登入頁
  - 測試填寫帳號密碼
  - 測試點擊登入按鈕
  - 測試驗證登入成功
- [ ] **綠燈**: 實作登入功能 `ithome_automation.py`
  - 初始化 Playwright
  - 實作 `login()` 方法
  - 實作 `is_logged_in()` 檢查
- [ ] **重構**: 優化程式碼結構

### Phase 3: TDD - 文章更新功能
- [ ] **紅燈**: 撰寫更新測試 `test_update_article.py`
  - 測試導航到文章編輯頁
  - 測試定位編輯器元素
  - 測試清除現有內容
  - 測試輸入新內容
  - 測試儲存文章
- [ ] **綠燈**: 實作更新功能
  - 實作 `navigate_to_article()`
  - 實作 `update_content()`
  - 實作 `save_article()`
- [ ] **重構**: 錯誤處理與重試機制

### Phase 4: TDD - 文章讀取功能
- [ ] **紅燈**: 撰寫檔案讀取測試
  - 測試讀取 Markdown 檔案
  - 測試讀取 JSON 對應表
  - 測試處理不存在的檔案
- [ ] **綠燈**: 實作檔案處理
  - 實作 `read_article_file()`
  - 實作 `load_mapping()`
- [ ] **重構**: 加入檔案驗證

### Phase 5: TDD - 批次處理功能
- [ ] **紅燈**: 撰寫批次處理測試
  - 測試批次更新多篇文章
  - 測試進度顯示
  - 測試錯誤恢復
- [ ] **綠燈**: 實作批次更新
  - 實作 `batch_update()`
  - 加入進度追蹤
  - 實作斷點續傳
- [ ] **重構**: 效能優化

### Phase 6: CLI 介面
- [ ] 建立命令列介面 `main.py`
- [ ] 實作單篇更新模式
- [ ] 實作批次更新模式
- [ ] 加入 --dry-run 模式

### Phase 7: 整合測試
- [ ] 撰寫端對端測試
- [ ] 測試完整工作流程
- [ ] 測試異常情況處理

## 專案結構
```
ironman-bot/
├── src/
│   ├── ithome_automation.py   # Playwright 自動化核心
│   └── main.py                # CLI 主程式
├── tests/
│   ├── test_login.py          # 登入功能測試
│   ├── test_update_article.py # 文章更新測試
│   └── test_integration.py    # 整合測試
├── articles/                  # 文章目錄
│   ├── day01.md
│   ├── day02.md
│   └── mapping.json          # 文章 ID 對應表
├── .env                       # 環境變數（帳號密碼）
├── .env.example               # 環境變數範本
├── requirements.txt           # 套件依賴
├── pytest.ini                 # 測試設定
├── Makefile                   # 自動化指令
└── README.md                 # 使用說明
```

## 技術棧
- **Python 3.10+**: 主要開發語言
- **Playwright**: 瀏覽器自動化
- **pytest**: 測試框架
- **pytest-playwright**: Playwright 測試整合
- **python-dotenv**: 環境變數管理

## 文章對應表格式 (mapping.json)
```json
{
  "articles": [
    {
      "id": "10347561",
      "file": "day01.md",
      "title": "Day 01: 開始 TDD 之旅"
    },
    {
      "id": "10347562", 
      "file": "day02.md",
      "title": "Day 02: 實作第一個測試"
    }
  ]
}
```

## 使用方式（預期）
```bash
# 安裝依賴
pip install -r requirements.txt
playwright install chromium

# 執行測試
pytest

# 更新單篇文章
python src/main.py --id 10347561 --file articles/day01.md

# 批次更新所有文章
python src/main.py --batch articles/mapping.json

# 乾跑模式（不實際更新）
python src/main.py --batch articles/mapping.json --dry-run
```

## 開發指令 (Makefile)
```bash
make install      # 安裝依賴
make test        # 執行所有測試
make test-unit   # 執行單元測試
make coverage    # 測試覆蓋率報告
make lint        # 程式碼檢查
make format      # 程式碼格式化
```

## 測試策略
1. **單元測試**: 測試個別函式和方法
2. **整合測試**: 測試模組間的互動
3. **E2E 測試**: 測試完整的使用流程
4. **覆蓋率目標**: > 80%

## 注意事項
- 需要有效的 iThome 帳號密碼
- 文章 ID 必須是該帳號有權限編輯的文章
- 瀏覽器固定使用顯示模式（headless=False），方便手動處理 reCAPTCHA
- 設定適當的等待時間避免被偵測為機器人

## 下一步行動
1. 清理現有檔案，重新開始
2. 從 Phase 1 開始逐步實作
3. 每個功能都先寫測試，再寫實作
4. 持續重構和優化