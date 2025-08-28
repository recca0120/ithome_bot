"""
主程式 - 使用 Class 架構開啟 iThome 鐵人賽登入頁面
"""
import asyncio
from src.ithome_automation import IThomeAutomation


async def main():
    """主函式 - 使用 IThomeAutomation 類別"""
    # 建立自動化物件（非 headless 模式）
    automation = IThomeAutomation(headless=False)
    
    try:
        # 開啟瀏覽器
        await automation.open_browser()
        
        # 導航到登入頁面
        await automation.goto_login_page()
        
        # 等待使用者查看
        print("瀏覽器將保持開啟狀態...")
        print("按 Ctrl+C 關閉")
        
        # 保持瀏覽器開啟
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n準備關閉...")
    finally:
        # 關閉瀏覽器
        await automation.close()
        print("完成！")


async def demo_login():
    """示範登入流程（需要真實帳號密碼）"""
    import os
    from dotenv import load_dotenv
    
    # 載入環境變數
    load_dotenv()
    
    username = os.getenv("ITHOME_USERNAME", "")
    password = os.getenv("ITHOME_PASSWORD", "")
    
    if not username or not password:
        print("請在 .env 檔案設定 ITHOME_USERNAME 和 ITHOME_PASSWORD")
        return
    
    # 建立自動化物件
    automation = IThomeAutomation(headless=False)
    
    try:
        # 鏈式呼叫
        await automation.open_browser()
        await automation.goto_login_page()
        await automation.fill_login_form(username, password)
        await automation.wait(2)  # 等待 2 秒讓使用者看到填寫的內容
        await automation.submit_login()
        
        # 等待登入完成
        await automation.wait(3)
        
        # 檢查是否登入成功
        if await automation.is_logged_in():
            print("登入成功！")
            current_url = automation.page.url
            print(f"當前頁面: {current_url}")
        else:
            print("登入失敗")
        
        # 等待 5 秒讓使用者查看結果
        await automation.wait(5)
        
    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        await automation.close()


if __name__ == "__main__":
    # 執行主程式
    asyncio.run(main())
    
    # 如果要測試登入，取消下面的註解
    # asyncio.run(demo_login())