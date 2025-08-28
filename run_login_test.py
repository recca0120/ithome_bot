"""
手動執行登入測試
從 .env 檔案讀取帳號密碼
"""
import asyncio
import os
from dotenv import load_dotenv
from src.ithome_automation import IThomeAutomation


async def test_login():
    """測試登入功能"""
    # 載入環境變數
    load_dotenv()
    
    account = os.getenv("ITHOME_ACCOUNT")
    password = os.getenv("ITHOME_PASSWORD")
    
    if not account or not password:
        print("錯誤：請在 .env 檔案中設定 ITHOME_ACCOUNT 和 ITHOME_PASSWORD")
        print("範例：")
        print("ITHOME_ACCOUNT=your_account")
        print("ITHOME_PASSWORD=your_password")
        return
    
    print(f"使用帳號: {account}")
    print("開始測試登入功能...")
    
    # 建立自動化物件（非 headless 模式，可以看到瀏覽器）
    automation = IThomeAutomation(headless=False)
    
    try:
        # 執行登入
        await automation.login(account, password)
        
        print("登入流程已完成")
        print("瀏覽器將保持開啟 10 秒...")
        
        # 等待 10 秒讓使用者看到結果
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        # 關閉瀏覽器
        await automation.close()
        print("測試完成")


if __name__ == "__main__":
    asyncio.run(test_login())