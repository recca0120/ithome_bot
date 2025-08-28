"""
iThome 鐵人賽登入自動化
使用 Class 架構
"""
import asyncio
import base64
import json
import random
from pathlib import Path

from playwright.async_api import async_playwright, Browser, Page, Playwright

from .login import Login
from .profile import Profile
from .utils import base_path


class IThomeAutomation:
    """iThome 自動化操作類別"""

    def __init__(self, headless: bool = False, cookies_file: str = None):
        """
        初始化
        
        Args:
            headless: 是否使用 headless 模式（預設 False，會顯示瀏覽器）
            cookies_file: 儲存 cookies 的檔案路徑（預設為專案根目錄下的 cookies.txt）
        """
        self.headless = headless
        # 如果沒有指定 cookies_file，使用專案根目錄下的 cookies.txt
        if cookies_file is None:
            self.cookies_file = base_path() / "cookies.txt"
        else:
            self.cookies_file = Path(cookies_file).resolve()
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.page: Page = None

    async def initialize(self):
        """
        初始化瀏覽器和頁面
        """
        # 啟動 Playwright
        self.playwright = await async_playwright().start()

        # 啟動瀏覽器
        self.browser = await self.playwright.webkit.launch(headless=self.headless)

        # 建立新頁面
        self.page = await self.browser.new_page()

    async def login(self, account: str, password: str) -> bool:
        """
        登入 iThome
        
        Args:
            account: 使用者帳號
            password: 使用者密碼
            
        Returns:
            bool: 登入是否成功
        """
        if not self.page:
            await self.initialize()

        # 使用 Login class 執行登入
        login_handler = Login(self.page)
        return await login_handler.login(account, password)

    async def goto_user_profile(self) -> None:
        """
        導航到使用者主頁
        需要先執行 login() 成功後才能呼叫
        """
        if not self.page:
            raise RuntimeError("尚未登入，請先執行 login() 方法")

        # 使用 Profile class 
        profile = Profile(self.page)
        # 導航到 ithelp
        await profile.goto_ithelp()
        # 執行 ithelp 登入
        await profile.ithelp_login()
        # 導航到使用者主頁
        await profile.navigate_to_user_profile()

    async def goto_article_edit(self, article_id: str, subject: str = None, description: str = None) -> None:
        """
        導航到文章編輯頁面並更新內容
        
        Args:
            article_id: 文章 ID
            subject: 文章標題（可選）
            description: 文章內容（可選）
        """
        if not self.page:
            raise RuntimeError("頁面尚未初始化，請先執行 initialize() 方法")

        edit_url = f"https://ithelp.ithome.com.tw/articles/{article_id}/edit"
        await self.page.goto(edit_url)
        print(f"已導航到文章編輯頁面: {edit_url}")

        # 等待頁面載入
        await self.page.wait_for_load_state("domcontentloaded")

        # 如果提供了標題，更新標題
        if subject is not None:
            print(f"📝 準備更新文章標題...")
            # 模擬人類行為：隨機延遲
            await self.page.wait_for_timeout(random.randint(500, 1500))
            
            subject_input = self.page.locator('input[name="subject"]')
            await subject_input.wait_for(state="visible", timeout=5000)
            
            # 模擬人類輸入：先清空再輸入
            await subject_input.focus()
            await self.page.wait_for_timeout(random.randint(100, 300))
            await subject_input.fill("")
            await self.page.wait_for_timeout(random.randint(200, 500))
            await subject_input.fill(subject)
            
            print(f"✅ 已更新文章標題: {subject}")

        # 如果提供了內容，更新內容
        if description is not None:
            print(f"📄 準備更新文章內容...")
            # 模擬人類行為：在標題和內容之間的延遲
            await self.page.wait_for_timeout(random.randint(800, 2000))
            
            # SimpleMDE 編輯器需要特殊處理
            # 使用 JavaScript 直接設定 SimpleMDE 的值
            await self.page.evaluate("""
                (description) => {
                    const textarea = document.querySelector('textarea[name="description"]');
                    const simplemde = $(textarea).data('simplemde');
                    
                    // 先清空內容
                    if (simplemde) {
                        simplemde.value('');
                    } else {
                        textarea.value = '';
                    }
                    
                    // 模擬延遲後設定內容
                    setTimeout(() => {
                        if (simplemde) {
                            simplemde.value(description);
                        } else {
                            textarea.value = description;
                        }
                    }, 300);
                }
            """, description)
            
            # 等待內容設定完成
            await self.page.wait_for_timeout(1000)
            print(f"✅ 已更新文章內容")
        
        # 如果有提供標題或內容，點擊更新按鈕
        if subject is not None or description is not None:
            print("🎯 準備提交更新...")
            # 模擬人類行為：檢查內容後再提交的延遲
            await self.page.wait_for_timeout(random.randint(1500, 3000))
            
            update_button = self.page.locator('#updateSubmitBtn')
            await update_button.wait_for(state="visible", timeout=5000)
            await update_button.click()
            print("已點擊更新按鈕")
            
            # 處理 reCAPTCHA
            recaptcha_handled = await self.handle_recaptcha()
            
            if not recaptcha_handled:
                # 自動處理失敗，嘗試手動處理
                print("🔄 自動處理 reCAPTCHA 失敗，切換到手動模式")
                await self.wait_for_manual_recaptcha()
            
            # 再次嘗試點擊更新按鈕（如果 reCAPTCHA 導致頁面重載）
            try:
                update_button = self.page.locator('#updateSubmitBtn')
                if await update_button.is_visible(timeout=2000):
                    print("🔄 重新點擊更新按鈕")
                    await update_button.click()
            except:
                pass
            
            # 等待頁面跳轉或成功訊息
            try:
                # 等待 URL 變化（從編輯頁面跳轉到文章頁面）
                await self.page.wait_for_url(
                    lambda url: "/edit" not in url,
                    timeout=15000  # 增加等待時間
                )
                print(f"✅ 文章已成功更新，跳轉到: {self.page.url}")
            except:
                # 檢查是否有成功訊息或其他狀態指示
                success_indicators = [
                    '.alert-success',
                    '.success-message', 
                    '[class*="success"]',
                    'text=成功',
                    'text=已更新',
                    'text=saved'
                ]
                
                success_found = False
                for indicator in success_indicators:
                    try:
                        element = self.page.locator(indicator)
                        if await element.is_visible(timeout=1000):
                            success_found = True
                            print(f"✅ 發現成功指示: {indicator}")
                            break
                    except:
                        continue
                
                if not success_found:
                    print("⚠️ 無法確認更新狀態，請手動檢查")

    async def save_cookies(self) -> None:
        """
        儲存當前的 cookies 到檔案（Base64 編碼格式）
        """
        if not self.page:
            raise RuntimeError("頁面尚未初始化")

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

        print(f"Cookies 已儲存到 {self.cookies_file.absolute()}")

    async def load_cookies(self) -> bool:
        """
        從檔案載入 cookies（Base64 編碼格式）
        
        Returns:
            bool: 是否成功載入 cookies
        """
        if not self.cookies_file.exists():
            print(f"找不到 cookies 檔案: {self.cookies_file.absolute()}")
            return False

        try:
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookies_encoded = f.read().strip()

            # Base64 解碼並轉換為 JSON
            cookies_json = base64.b64decode(cookies_encoded).decode('utf-8')
            cookies = json.loads(cookies_json)

            if self.page and cookies:
                await self.page.context.add_cookies(cookies)
                print(f"已從 {self.cookies_file.absolute()} 載入 {len(cookies)} 個 cookies")
                return True
        except Exception as e:
            print(f"載入 cookies 失敗: {e}")

        return False

    async def handle_recaptcha(self) -> bool:
        """
        處理 reCAPTCHA 驗證
        
        Returns:
            bool: 是否成功處理 reCAPTCHA
        """
        print("🔍 檢查是否有 reCAPTCHA...")
        
        # 等待頁面完全載入
        await self.page.wait_for_timeout(2000)
        
        # 檢查不同類型的 reCAPTCHA
        recaptcha_selectors = [
            'iframe[src*="recaptcha/api2/anchor"]',
            'iframe[title="reCAPTCHA"]', 
            '.g-recaptcha',
            'iframe[src*="recaptcha"]'
        ]
        
        recaptcha_found = False
        for selector in recaptcha_selectors:
            elements = self.page.locator(selector)
            if await elements.count() > 0:
                print(f"⚠️ 偵測到 reCAPTCHA: {selector}")
                recaptcha_found = True
                break
        
        if not recaptcha_found:
            print("✅ 未發現 reCAPTCHA")
            return True
        
        # 嘗試自動處理 reCAPTCHA checkbox
        try:
            print("🤖 嘗試自動處理 reCAPTCHA checkbox...")
            
            # 隨機等待，模擬人類行為
            await self.page.wait_for_timeout(random.randint(1000, 3000))
            
            # 方法 1: 使用 frame_locator
            recaptcha_frame = self.page.frame_locator('iframe[src*="recaptcha/api2/anchor"]')
            checkbox_selectors = [
                '.recaptcha-checkbox-border',
                '.recaptcha-checkbox',
                '#recaptcha-anchor',
                '[role="checkbox"]'
            ]
            
            checkbox_clicked = False
            for checkbox_selector in checkbox_selectors:
                try:
                    checkbox = recaptcha_frame.locator(checkbox_selector)
                    if await checkbox.is_visible(timeout=2000):
                        print(f"找到 checkbox: {checkbox_selector}")
                        
                        # 模擬滑鼠移動和點擊
                        await checkbox.hover()
                        await self.page.wait_for_timeout(random.randint(200, 800))
                        await checkbox.click()
                        
                        print("✅ 已點擊 reCAPTCHA checkbox")
                        checkbox_clicked = True
                        break
                except Exception as e:
                    print(f"嘗試 {checkbox_selector} 失敗: {str(e)[:100]}")
                    continue
            
            if not checkbox_clicked:
                # 方法 2: 嘗試通過所有 frames 尋找
                print("🔄 嘗試通過所有 frames 尋找 checkbox...")
                frames = self.page.frames
                for frame in frames:
                    if 'recaptcha' in frame.url.lower():
                        try:
                            for selector in checkbox_selectors:
                                checkbox = frame.locator(selector)
                                if await checkbox.is_visible(timeout=1000):
                                    await checkbox.click()
                                    print("✅ 在 frame 中成功點擊 checkbox")
                                    checkbox_clicked = True
                                    break
                            if checkbox_clicked:
                                break
                        except:
                            continue
            
            if checkbox_clicked:
                # 等待驗證完成
                print("⏳ 等待 reCAPTCHA 驗證完成...")
                await self.page.wait_for_timeout(3000)
                
                # 檢查是否出現圖片挑戰
                challenge_frame = self.page.frame_locator('iframe[src*="recaptcha/api2/bframe"]')
                try:
                    challenge_visible = await challenge_frame.locator('.rc-imageselect-desc').is_visible(timeout=2000)
                    if challenge_visible:
                        print("❌ 出現圖片挑戰，需要手動處理")
                        return False
                except:
                    pass
                
                print("✅ reCAPTCHA checkbox 處理完成")
                return True
            else:
                print("❌ 無法找到或點擊 reCAPTCHA checkbox")
                return False
                
        except Exception as e:
            print(f"❌ 自動處理 reCAPTCHA 失敗: {e}")
            return False

    async def wait_for_manual_recaptcha(self):
        """等待手動完成 reCAPTCHA"""
        if self.headless:
            print("⚠️ Headless 模式下無法手動處理 reCAPTCHA")
            return False
        
        print("🖐️ 請手動完成 reCAPTCHA 驗證...")
        print("   - 如果需要，點擊 checkbox")
        print("   - 如果出現圖片挑戰，請完成挑戰")
        print("   - 完成後程式將自動繼續")
        
        # 等待 30 秒讓用戶完成
        for i in range(30):
            await self.page.wait_for_timeout(1000)
            
            # 檢查是否還有未完成的 reCAPTCHA
            recaptcha_frames = self.page.locator('iframe[src*="recaptcha"]')
            if await recaptcha_frames.count() == 0:
                print("✅ reCAPTCHA 已完成")
                return True
            
            # 檢查是否有錯誤訊息或成功狀態
            if i % 5 == 0:  # 每 5 秒檢查一次
                print(f"⏳ 等待中... ({30-i} 秒剩餘)")
        
        print("⏰ 手動處理時間已到")
        return True

    async def close(self):
        """關閉瀏覽器"""
        if self.browser:
            await self.browser.close()
            print("瀏覽器已關閉")
        if self.playwright:
            await self.playwright.stop()
