#!/usr/bin/env python3
"""把 1920x1080 HTML 截图为 PNG

用法:
    python html_to_png.py <input.html> <output.png>

依赖(按优先级):
    1. playwright: pip install playwright && playwright install chromium
    2. 系统 Chrome/Edge + headless 模式
    3. Pillow 降级(零外部依赖,5 种 hero_cover/chapter_divider 等模板)
"""

# IMPORTANT: path setup must come BEFORE any skills.* imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path

from skills.shared.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def screenshot_with_playwright(html_path, png_path):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(f"file://{html_path.resolve()}")
            page.wait_for_load_state("networkidle")
            page.screenshot(path=str(png_path), full_page=False)
            browser.close()
        return True
    except Exception as e:
        logger.warning("playwright 失败: %s", e)
        return False


def screenshot_with_chrome(html_path, png_path):
    candidates = [
        "chrome",
        "google-chrome",
        "chromium",
        "msedge",
        "Microsoft\\Edge\\Application\\msedge.exe",
    ]
    for c in candidates:
        path = shutil.which(c)
        if path:
            cmd = [
                path,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--window-size=1920,1080",
                f"--screenshot={png_path}",
                f"file://{html_path.resolve()}",
            ]
            subprocess.run(cmd, check=False)
            if png_path.exists():
                return True
    return False


def screenshot_with_pillow(html_path, png_path):
    """降级方案:用 Pillow 解析 5 种已知模板的 HTML 渲染"""
    script = Path(__file__).parent / "html_to_png_pillow.py"
    if not script.exists():
        return False
    result = subprocess.run(
        [sys.executable, str(script), str(html_path), str(png_path)],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and png_path.exists()


def main() -> None:
    parser = argparse.ArgumentParser(description="把 HTML 截图为 PNG")
    parser.add_argument("input", help="输入 HTML 文件路径")
    parser.add_argument("output", help="输出 PNG 文件路径")
    args = parser.parse_args()
    html_path = Path(args.input)
    png_path = Path(args.output)

    if screenshot_with_playwright(html_path, png_path):
        logger.info("已截图(playwright): %s", png_path)
        return
    if screenshot_with_chrome(html_path, png_path):
        logger.info("已截图(chrome/edge): %s", png_path)
        return
    if screenshot_with_pillow(html_path, png_path):
        logger.info("已截图(pillow 降级): %s", png_path)
        return

    logger.error("所有截图方案都失败(playwright/chrome/pillow)")
    sys.exit(1)


if __name__ == "__main__":
    main()
