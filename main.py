#!/usr/bin/env python3
"""
iThome 鐵人賽文章更新 CLI 工具
"""
import asyncio
import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from playwright.async_api import async_playwright
from src.bot import Bot

# 載入 .env 檔案
load_dotenv()


async def perform_login(bot: Bot) -> bool:
    """
    執行登入流程

    Args:
        bot: Bot 實例

    Returns:
        bool: 登入是否成功
    """
    click.echo("🔑 載入 cookies...")
    await bot.load_cookies()

    # 從環境變數讀取帳密
    account = os.getenv('ITHOME_ACCOUNT')
    password = os.getenv('ITHOME_PASSWORD')

    if not account or not password:
        click.echo("❌ 錯誤: 請設定環境變數 ITHOME_ACCOUNT 和 ITHOME_PASSWORD")
        return False

    # 執行登入（會自動檢查 cookies 並導航到使用者主頁）
    click.echo("🔐 執行登入...")
    if await bot.login(account, password):
        click.echo("✅ 登入成功")

        # 儲存 cookies
        click.echo("💾 儲存 cookies...")
        await bot.save_cookies()
        click.echo("✅ Cookies 已儲存")
        return True
    else:
        click.echo("❌ 登入失敗")
        return False


async def update_article_cli(article_id: str, subject: str, description_file: str) -> None:
    """
    透過 CLI 更新文章

    Args:
        article_id: 文章 ID
        subject: 文章標題
        description_file: 文章內容檔案路徑
    """
    # 檢查描述檔案是否存在
    file_path = Path(description_file)
    if not file_path.exists():
        click.echo(f"❌ 錯誤: 找不到檔案 {file_path}")
        sys.exit(1)

    # 讀取文章內容
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            description = f.read()
        click.echo(f"📖 已讀取文章內容檔案: {description_file}，長度: {len(description)} 字元")
    except Exception as e:
        click.echo(f"❌ 讀取檔案失敗: {e}")
        sys.exit(1)

    # 啟動 Playwright 和瀏覽器
    playwright = await async_playwright().start()
    browser = await playwright.webkit.launch(headless=False)
    page = await browser.new_page()
    
    # 建立 Bot 實例
    bot = Bot(page)

    try:
        click.echo("🚀 瀏覽器已啟動")

        # 執行登入
        if not await perform_login(bot):
            sys.exit(1)

        click.echo("🔄 更新文章中...")
        article_data = {
            "article_id": article_id,
            "subject": subject,
            "description": description
        }
        success = await bot.update_article(article_data)

        if success:
            click.echo("✅ 文章更新成功!")
        else:
            click.echo("❌ 文章更新失敗")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ 執行過程中發生錯誤: {e}")
        sys.exit(1)
    finally:
        await browser.close()
        await playwright.stop()
        click.echo("🏁 程式執行完成")


@click.command()
@click.argument('article_id')
@click.argument('subject')
@click.argument('description_file')
def main(article_id: str, subject: str, description_file: str) -> None:
    """
    iThome 鐵人賽文章更新工具

    ARTICLE_ID: 文章 ID

    SUBJECT: 文章標題

    DESCRIPTION_FILE: 文章內容檔案路徑

    \b
    使用範例:
      python main.py 10376177 "Day 01 標題" tests/fixtures/day01-python-environment-setup.md
    """
    click.echo("🤖 iThome 鐵人賽文章更新工具")
    click.echo("=" * 50)
    click.echo(f"📄 文章 ID: {article_id}")
    click.echo(f"📝 文章標題: {subject}")
    click.echo(f"📁 內容檔案: {description_file}")
    click.echo("=" * 50)

    # 執行更新
    asyncio.run(update_article_cli(article_id, subject, description_file))


if __name__ == "__main__":
    main()
