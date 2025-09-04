#!/usr/bin/env python3
"""
iThome Bot CLI - 命令列介面
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click
from playwright.async_api import async_playwright

# 從同一個 package 載入模組
from .client import Client
from .authenticator import Authenticator
from .article_updater import ArticleUpdater


async def update_article_with_bot(
    article_id: str,
    subject: str,
    description_file: str,
    account: Optional[str] = None,
    password: Optional[str] = None
) -> bool:
    """
    使用 Client 更新文章的核心函數
    
    Args:
        article_id: 文章 ID
        subject: 文章標題
        description_file: 文章內容檔案路徑
        account: iThome 帳號（可選，預設從環境變數讀取）
        password: iThome 密碼（可選，預設從環境變數讀取）
    
    Returns:
        bool: 是否更新成功
    """
    
    # 讀取文章內容
    file_path = Path(description_file)
    if not file_path.exists():
        click.echo(f"❌ 錯誤: 找不到檔案 {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        description = f.read()
    click.echo(f"📖 已讀取文章內容檔案: {description_file}，長度: {len(description)} 字元")
    
    # 取得帳密
    if not account:
        account = os.getenv('ITHOME_ACCOUNT')
    if not password:
        password = os.getenv('ITHOME_PASSWORD')
    
    if not account or not password:
        click.echo("❌ 錯誤: 請提供帳號密碼或設定環境變數 ITHOME_ACCOUNT 和 ITHOME_PASSWORD")
        return False
    
    # 啟動瀏覽器和執行更新
    click.echo("🚀 正在初始化瀏覽器...")
    playwright = await async_playwright().start()
    browser = await playwright.webkit.launch(headless=False)
    page = await browser.new_page()
    
    try:
        # 建立 Client 實例
        client = Client(page)
        
        # 載入 cookies
        click.echo("🔑 載入 cookies...")
        await client.load_cookies()
        
        # 執行登入
        click.echo("🔐 執行登入...")
        if not await client.login(account, password):
            click.echo("❌ 登入失敗")
            return False
        click.echo("✅ 登入成功")
        
        # 儲存 cookies
        click.echo("💾 儲存 cookies...")
        await client.save_cookies()
        click.echo("✅ Cookies 已儲存")
        
        # 更新文章
        click.echo("🔄 更新文章中...")
        article_data = {
            "article_id": article_id,
            "subject": subject,
            "description": description
        }
        
        result = await client.update_article(article_data)
        
        if result:
            click.echo(f"✅ 文章更新成功! (文章 ID: {result})")
        else:
            click.echo("❌ 文章更新失敗")
        
        return result is not None
        
    finally:
        await browser.close()
        await playwright.stop()
        click.echo("🏁 程式執行完成")


@click.command()
@click.argument('article_id')
@click.argument('subject')
@click.argument('description_file')
@click.option('--account', envvar='ITHOME_ACCOUNT', help='iThome 帳號（預設從環境變數 ITHOME_ACCOUNT 讀取）')
@click.option('--password', envvar='ITHOME_PASSWORD', help='iThome 密碼（預設從環境變數 ITHOME_PASSWORD 讀取）')
def main(article_id: str, subject: str, description_file: str, account: str, password: str):
    """
    iThome 鐵人賽文章更新工具
    
    ARTICLE_ID: 文章 ID
    
    SUBJECT: 文章標題
    
    DESCRIPTION_FILE: 文章內容檔案路徑
    
    \b
    使用範例:
      ithome-bot 10376177 "Day 01 標題" article.md
      ithome-bot 10376177 "Day 01 標題" article.md --account myaccount --password mypass
    """
    # 載入 .env 檔案（如果存在）
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    click.echo("🤖 iThome 鐵人賽文章更新工具")
    click.echo("=" * 50)
    click.echo(f"📄 文章 ID: {article_id}")
    click.echo(f"📝 文章標題: {subject}")
    click.echo(f"📁 內容檔案: {description_file}")
    click.echo("=" * 50)
    
    # 執行更新
    success = asyncio.run(update_article_with_bot(
        article_id,
        subject,
        description_file,
        account,
        password
    ))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()