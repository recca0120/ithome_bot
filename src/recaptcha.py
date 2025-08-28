"""
reCAPTCHA 處理模組
"""
import random
from playwright.async_api import Page


class ReCaptcha:
    """reCAPTCHA 處理器"""

    def __init__(self, page: Page):
        """
        初始化 reCAPTCHA 處理器
        
        Args:
            page: Playwright 頁面物件
        """
        self.page = page

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