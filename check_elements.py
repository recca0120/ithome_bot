"""
檢查登入頁面的元素
"""
import asyncio
from playwright.async_api import async_playwright


async def check_login_page_elements():
    """檢查登入頁面上的表單元素"""
    async with async_playwright() as p:
        # 啟動瀏覽器
        browser = await p.webkit.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 導航到登入頁面
            await page.goto("https://member.ithome.com.tw/login")
            print("已開啟登入頁面")
            
            # 等待頁面載入
            await page.wait_for_load_state("networkidle")
            
            # 取得所有 input 元素
            print("\n頁面上的所有 input 元素:")
            inputs = await page.query_selector_all('input')
            
            for i, input_elem in enumerate(inputs):
                attrs = await input_elem.evaluate('''
                    el => ({
                        id: el.id,
                        name: el.name,
                        type: el.type,
                        placeholder: el.placeholder,
                        className: el.className
                    })
                ''')
                print(f"{i+1}. {attrs}")
            
            # 取得所有 button 元素
            print("\n頁面上的所有 button 元素:")
            buttons = await page.query_selector_all('button')
            
            for i, button in enumerate(buttons):
                text = await button.text_content()
                attrs = await button.evaluate('''
                    el => ({
                        id: el.id,
                        type: el.type,
                        className: el.className
                    })
                ''')
                print(f"{i+1}. 文字: '{text}', 屬性: {attrs}")
            
            # 等待使用者查看
            print("\n保持開啟 10 秒...")
            await asyncio.sleep(10)
            
        finally:
            await browser.close()
            print("瀏覽器已關閉")


if __name__ == "__main__":
    asyncio.run(check_login_page_elements())