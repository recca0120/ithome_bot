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
        # 初始化 selectors
        self.recaptcha_selectors = [
            'iframe[src*="recaptcha/api2/anchor"]',
            'iframe[title="reCAPTCHA"]', 
            '.g-recaptcha',
            'iframe[src*="recaptcha"]'
        ]
        self.checkbox_selectors = [
            '.recaptcha-checkbox-border',
            '.recaptcha-checkbox',
            '#recaptcha-anchor',
            '[role="checkbox"]'
        ]

    async def handle_recaptcha(self) -> bool:
        """
        處理 reCAPTCHA 驗證
        
        Returns:
            bool: 是否成功處理 reCAPTCHA
        """
        print("🔍 檢查是否有 reCAPTCHA...")
        
        # 等待頁面完全載入
        await self.page.wait_for_timeout(2000)
        
        # 檢查是否有 reCAPTCHA
        if not await self._detect_recaptcha():
            print("✅ 未發現 reCAPTCHA")
            return True
        
        # 捲動到 reCAPTCHA
        await self._scroll_to_recaptcha()
        
        # 嘗試自動處理
        return await self._attempt_auto_solve()

    async def _detect_recaptcha(self) -> bool:
        """偵測是否有 reCAPTCHA"""
        for selector in self.recaptcha_selectors:
            elements = self.page.locator(selector)
            if await elements.count() > 0:
                print(f"⚠️ 偵測到 reCAPTCHA: {selector}")
                return True
        return False

    async def _scroll_to_recaptcha(self) -> None:
        """捲動到 reCAPTCHA 位置"""
        print("📜 捲動到 reCAPTCHA 位置...")
        try:
            # 嘗試找到 reCAPTCHA 元素並捲動到它
            for selector in self.recaptcha_selectors:
                elements = self.page.locator(selector)
                if await elements.count() > 0:
                    await elements.first.scroll_into_view_if_needed()
                    await self.page.wait_for_timeout(500)
                    print("✅ 已捲動到 reCAPTCHA")
                    return
        except Exception as e:
            print(f"⚠️ 捲動到 reCAPTCHA 失敗: {e}")

    async def _attempt_auto_solve(self) -> bool:
        """嘗試自動解決 reCAPTCHA"""
        print("🤖 嘗試自動處理 reCAPTCHA checkbox...")
        
        # 隨機等待，模擬人類行為
        await self.page.wait_for_timeout(random.randint(1000, 3000))
        
        # 方法 1: 使用 frame_locator
        if await self._try_frame_locator():
            return await self._verify_completion()
        
        # 方法 2: 嘗試通過所有 frames 尋找
        if await self._try_all_frames():
            return await self._verify_completion()
        
        print("❌ 無法自動處理 reCAPTCHA")
        return False

    async def _try_frame_locator(self) -> bool:
        """使用 frame_locator 嘗試點擊 checkbox"""
        try:
            recaptcha_frame = self.page.frame_locator('iframe[src*="recaptcha/api2/anchor"]')
            
            for checkbox_selector in self.checkbox_selectors:
                try:
                    checkbox = recaptcha_frame.locator(checkbox_selector)
                    if await checkbox.is_visible(timeout=2000):
                        print(f"找到 checkbox: {checkbox_selector}")
                        await self._click_checkbox(checkbox)
                        return True
                except Exception as e:
                    print(f"嘗試 {checkbox_selector} 失敗: {str(e)[:100]}")
                    continue
            
        except Exception as e:
            print(f"frame_locator 方法失敗: {str(e)[:100]}")
        
        return False

    async def _try_all_frames(self) -> bool:
        """嘗試通過所有 frames 尋找 checkbox"""
        print("🔄 嘗試通過所有 frames 尋找 checkbox...")
        
        try:
            frames = self.page.frames
            for frame in frames:
                if 'recaptcha' in frame.url.lower():
                    for selector in self.checkbox_selectors:
                        try:
                            checkbox = frame.locator(selector)
                            if await checkbox.is_visible(timeout=1000):
                                await checkbox.click()
                                print("✅ 在 frame 中成功點擊 checkbox")
                                return True
                        except:
                            continue
        except Exception as e:
            print(f"all_frames 方法失敗: {str(e)[:100]}")
        
        return False

    async def _click_checkbox(self, checkbox) -> None:
        """點擊 checkbox"""
        # 模擬滑鼠移動和點擊
        await checkbox.hover()
        await self.page.wait_for_timeout(random.randint(200, 800))
        await checkbox.click()
        print("✅ 已點擊 reCAPTCHA checkbox")

    async def _verify_completion(self) -> bool:
        """驗證 reCAPTCHA 完成狀態"""
        # 等待驗證完成
        print("⏳ 等待 reCAPTCHA 驗證完成...")
        await self.page.wait_for_timeout(3000)
        
        # 檢查是否出現圖片挑戰
        if await self._has_image_challenge():
            print("❌ 出現圖片挑戰，需要手動處理")
            return False
        
        print("✅ reCAPTCHA checkbox 處理完成")
        return True

    async def _has_image_challenge(self) -> bool:
        """檢查是否有圖片挑戰"""
        try:
            challenge_frame = self.page.frame_locator('iframe[src*="recaptcha/api2/bframe"]')
            return await challenge_frame.locator('.rc-imageselect-desc').is_visible(timeout=2000)
        except:
            return False

    async def wait_for_manual_recaptcha(self) -> bool:
        """等待手動完成 reCAPTCHA"""
        print("🖐️ 請手動完成 reCAPTCHA 驗證...")
        print("   - 如果需要，點擊 checkbox")
        print("   - 如果出現圖片挑戰，請完成挑戰")
        print("   - 完成後程式將自動繼續")
        
        # 等待 30 秒讓用戶完成
        for i in range(30):
            await self.page.wait_for_timeout(1000)
            
            # 檢查是否還有未完成的 reCAPTCHA
            if not await self._has_pending_recaptcha():
                print("✅ reCAPTCHA 已完成")
                return True
            
            # 顯示進度
            if i % 5 == 0:  # 每 5 秒檢查一次
                print(f"⏳ 等待中... ({30-i} 秒剩餘)")
        
        print("⏰ 手動處理時間已到")
        return True

    async def _has_pending_recaptcha(self) -> bool:
        """檢查是否還有未完成的 reCAPTCHA"""
        try:
            recaptcha_frames = self.page.locator('iframe[src*="recaptcha"]')
            return await recaptcha_frames.count() > 0
        except:
            return False