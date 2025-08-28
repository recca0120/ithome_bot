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
async def automation(credential):
    """建立並初始化 IThomeAutomation 實例，並執行登入"""
    automation = IThomeAutomation()
    await automation.initialize()
    
    # 載入 cookies
    await automation.load_cookies()
    
    # 執行登入
    await automation.login(credential["account"], credential["password"])
    
    # 儲存 cookies
    await automation.save_cookies()
    
    yield automation
    
    # 清理
    await automation.close()