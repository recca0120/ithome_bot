"""
共用的 pytest fixtures 和設定
"""
import pytest
import pytest_asyncio
import os
from dotenv import load_dotenv
from src.ithome_automation import IThomeAutomation

# 載入環境變數
load_dotenv()


@pytest.fixture
def credential():
    """從環境變數取得帳號密碼"""
    return {
        "account": os.getenv("ITHOME_ACCOUNT"),
        "password": os.getenv("ITHOME_PASSWORD")
    }


@pytest_asyncio.fixture
async def automation():
    """建立並初始化 IThomeAutomation 實例，並載入 cookies"""
    from src.profile import Profile
    
    automation = IThomeAutomation()
    await automation.initialize()
    
    # 載入 cookies
    await automation.load_cookies()
    
    # 導航到 ithelp 並確認登入狀態
    profile = Profile(automation.page)
    await profile.goto_ithelp()
    await profile.ithelp_login()
    
    yield automation
    
    # 清理
    await automation.close()