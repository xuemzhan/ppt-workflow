#!/usr/bin/env python3
"""HTML 视觉页 → PNG(零 Chrome 依赖)
仅支持 build_visual.py 的 5 种模板(hero_cover / chapter_divider / big_quote /
methodology / flow_diagram),通过解析 HTML 提取关键文本+位置+Pillow 渲染。

这是 html_to_png.py 的"降级路径",在无 Playwright/Chrome 时使用。
视觉保真度低于浏览器渲染,但作为"凑合用"够用。

用法:
    python html_to_png_pillow.py <input.html> <output.png>
"""

import argparse
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Make shared imports work when run standalone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from PIL import Image, ImageDraw, ImageFont
from skills.shared.fonts import get_font_path
from skills.shared.utils import hex_to_rgb

W, H = 1920, 1080


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Get a font at the given size, trying system CJK fonts first."""
    font_name = "msyhbd.ttc" if bold else "msyh.ttc"
    font_path = get_font_path(font_name)
    if font_path and font_path != "PIL_DEFAULT" and Path(font_path).exists():
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    any_font = get_font_path()
    if any_font and any_font != "PIL_DEFAULT" and Path(any_font).exists():
        try:
            return ImageFont.truetype(any_font, size)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_gradient(
    d: ImageDraw.ImageDraw, color1: str, color2: str, w: int, h: int
) -> None:
    """模拟 linear-gradient"""
    c1 = hex_to_rgb(color1)
    c2 = hex_to_rgb(color2)
    for y in range(h):
        t = y / h
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
        d.line([(0, y), (w, y)], fill=(r, g, b))


def detect_template(html: str) -> str:
    """通过 class 名识别模板"""
    if 'class="hero' in html:
        return "hero_cover"
    if 'class="chapter' in html:
        return "chapter_divider"
    if 'class="quote"' in html and 'class="method"' not in html:
        return "big_quote"
    if 'class="method"' in html:
        return "methodology"
    if 'class="flow"' in html:
        return "flow_diagram"
    return "unknown"


def extract_text(html: str, *patterns: str) -> str:
    """从 HTML 抓取文本,按提供的正则依次尝试"""
    for pat in patterns:
        m = re.search(pat, html, re.DOTALL)
        if m:
            return m.group(1).strip()
    return ""


def render_hero(html: str, out_path: str) -> None:
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_gradient(d, "#1E2761", "#065A82", W, H)

    # 网格背景
    grid_color = (255, 255, 255, 13)  # alpha 13/255
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(40, 60, 100), width=1)
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(40, 60, 100), width=1)

    eyebrow = extract_text(html, r'<div class="hero-eyebrow">([^<]+)</div>')
    title = extract_text(html, r'<h1 class="hero-title">([^<]+)</h1>').replace(
        "<br>", "\n"
    )
    sub = extract_text(html, r'<div class="hero-sub">([^<]+)</div>')
    author = extract_text(html, r'<div class="hero-author">([^<]+)</div>')

    # eyebrow 框
    if eyebrow:
        ex = W // 2 - 200
        ey = 320
        d.rectangle(
            [(ex, ey), (ex + 400, ey + 60)], outline=hex_to_rgb("#F96167"), width=2
        )
        eb_font = get_font(28, bold=True)
        bbox = d.textbbox((0, 0), eyebrow, font=eb_font)
        tw = bbox[2] - bbox[0]
        d.text(
            (ex + (400 - tw) // 2, ey + 15),
            eyebrow,
            fill=hex_to_rgb("#F96167"),
            font=eb_font,
        )

    # 标题(自动换行)
    if title:
        t_font = get_font(110, bold=True)
        lines = title.split("\n")
        total_h = 130 * len(lines)
        ty = (H - total_h) // 2 - 50
        for i, line in enumerate(lines):
            bbox = d.textbbox((0, 0), line, font=t_font)
            tw = bbox[2] - bbox[0]
            d.text(
                ((W - tw) // 2, ty + i * 130), line, fill=(255, 255, 255), font=t_font
            )

    if sub:
        s_font = get_font(40)
        bbox = d.textbbox((0, 0), sub, font=s_font)
        tw = bbox[2] - bbox[0]
        d.text(((W - tw) // 2, 720), sub, fill=hex_to_rgb("#CADCFC"), font=s_font)

    if author:
        a_font = get_font(28)
        bbox = d.textbbox((0, 0), author, font=a_font)
        tw = bbox[2] - bbox[0]
        d.text(((W - tw) // 2, 900), author, fill=(180, 200, 220), font=a_font)

    img.save(out_path)


def render_chapter(html: str, out_path: str) -> None:
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_gradient(d, "#1E2761", "#0a0f2c", W, H)

    number = extract_text(html, r'<div class="chapter-number">([^<]+)</div>')
    title = extract_text(html, r'<div class="chapter-title">([^<]+)</div>')
    sub = extract_text(html, r'<div class="chapter-sub">([^<]+)</div>')

    if number:
        n_font = get_font(280, bold=True)
        bbox = d.textbbox((0, 0), number, font=n_font)
        tw = bbox[2] - bbox[0]
        d.text(((W - tw) // 2, 180), number, fill=hex_to_rgb("#F96167"), font=n_font)

    if title:
        t_font = get_font(80, bold=True)
        bbox = d.textbbox((0, 0), title, font=t_font)
        tw = bbox[2] - bbox[0]
        d.text(((W - tw) // 2, 580), title, fill=(255, 255, 255), font=t_font)

    if sub:
        s_font = get_font(32)
        bbox = d.textbbox((0, 0), sub, font=s_font)
        tw = bbox[2] - bbox[0]
        d.text(((W - tw) // 2, 720), sub, fill=hex_to_rgb("#CADCFC"), font=s_font)

    img.save(out_path)


def render_quote(html: str, out_path: str) -> None:
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_gradient(d, "#1E2761", "#2C5F2D", W, H)

    text = extract_text(html, r'<p class="quote-text">([^<]+)</p>').replace(
        "<br>", "\n"
    )
    author = extract_text(html, r'<div class="quote-author">([^<]+)</div>')

    if text:
        t_font = get_font(72, bold=True)
        lines = text.split("\n")
        total_h = 100 * len(lines)
        ty = (H - total_h) // 2 - 50
        for i, line in enumerate(lines):
            bbox = d.textbbox((0, 0), '"' + line + '"', font=t_font)
            tw = bbox[2] - bbox[0]
            d.text(
                ((W - tw) // 2, ty + i * 100),
                '"' + line + '"',
                fill=(255, 255, 255),
                font=t_font,
            )

    if author:
        a_font = get_font(28)
        bbox = d.textbbox((0, 0), author, font=a_font)
        tw = bbox[2] - bbox[0]
        d.text(
            ((W - tw) // 2, H - 150), author, fill=hex_to_rgb("#CADCFC"), font=a_font
        )

    img.save(out_path)


def render_methodology(html: str, out_path: str) -> None:
    """3 卡片方法论"""
    img = Image.new("RGB", (W, H), (245, 245, 245))
    d = ImageDraw.Draw(img)
    title = extract_text(html, r"<h2>([^<]+)</h2>")
    if title:
        t_font = get_font(72, bold=True)
        bbox = d.textbbox((0, 0), title, font=t_font)
        tw = bbox[2] - bbox[0]
        d.text(((W - tw) // 2, 80), title, fill=hex_to_rgb("#1E2761"), font=t_font)

    # 抽 step
    steps = re.findall(
        r'<div class="method-step">.*?<h3>([^<]+)</h3>.*?<p>([^<]+)</p>',
        html,
        re.DOTALL,
    )
    n = len(steps)
    if n == 0:
        img.save(out_path)
        return
    card_w = 480
    gap = 60
    total_w = n * card_w + (n - 1) * gap
    start_x = (W - total_w) // 2
    for i, (st_title, st_desc) in enumerate(steps):
        cx = start_x + i * (card_w + gap)
        cy = 300
        # 卡片
        d.rectangle(
            [(cx, cy), (cx + card_w, cy + 500)],
            fill=(255, 255, 255),
            outline=(220, 220, 220),
            width=1,
        )
        # 顶部色带
        d.rectangle([(cx, cy), (cx + card_w, cy + 8)], fill=hex_to_rgb("#F96167"))
        # 编号
        num_font = get_font(60, bold=True)
        d.text(
            (cx + 30, cy + 30), f"0{i + 1}", fill=hex_to_rgb("#F96167"), font=num_font
        )
        # 标题
        tt_font = get_font(40, bold=True)
        d.text((cx + 30, cy + 120), st_title, fill=hex_to_rgb("#1E2761"), font=tt_font)
        # 描述(简单换行)
        d_font = get_font(24)
        words = st_desc
        max_w = card_w - 60
        line_y = cy + 200
        cur = ""
        for ch in words:
            test = cur + ch
            bbox = d.textbbox((0, 0), test, font=d_font)
            if bbox[2] - bbox[0] > max_w:
                d.text((cx + 30, line_y), cur, fill=hex_to_rgb("#36454F"), font=d_font)
                line_y += 36
                cur = ch
            else:
                cur = test
        if cur:
            d.text((cx + 30, line_y), cur, fill=hex_to_rgb("#36454F"), font=d_font)
    img.save(out_path)


def render_flow(html: str, out_path: str) -> None:
    """流程图(横向节点)"""
    img = Image.new("RGB", (W, H), (245, 245, 245))
    d = ImageDraw.Draw(img)
    title = extract_text(html, r"<h2>([^<]+)</h2>")
    if title:
        t_font = get_font(64, bold=True)
        bbox = d.textbbox((0, 0), title, font=t_font)
        tw = bbox[2] - bbox[0]
        d.text(((W - tw) // 2, 80), title, fill=hex_to_rgb("#1E2761"), font=t_font)

    nodes = re.findall(r'<div class="flow-node( highlight)?">([^<]+)</div>', html)
    if not nodes:
        img.save(out_path)
        return
    n = len(nodes)
    box_w = 280
    gap = 60
    arrow_w = 50
    total_w = n * box_w + (n - 1) * (gap + arrow_w)
    start_x = (W - total_w) // 2
    cy = H // 2 - 50
    n_font = get_font(32, bold=True)
    a_font = get_font(72, bold=True)
    for i, (highlight, label) in enumerate(nodes):
        cx = start_x + i * (box_w + gap + arrow_w)
        color = hex_to_rgb("#F96167") if highlight else hex_to_rgb("#1E2761")
        d.rectangle([(cx, cy), (cx + box_w, cy + 100)], fill=color)
        bbox = d.textbbox((0, 0), label, font=n_font)
        tw = bbox[2] - bbox[0]
        d.text(
            (cx + (box_w - tw) // 2, cy + 30), label, fill=(255, 255, 255), font=n_font
        )
        # 箭头
        if i < n - 1:
            ax = cx + box_w + gap // 2
            d.text((ax, cy + 20), "→", fill=hex_to_rgb("#1E2761"), font=a_font)
    img.save(out_path)


RENDERERS = {
    "hero_cover": render_hero,
    "chapter_divider": render_chapter,
    "big_quote": render_quote,
    "methodology": render_methodology,
    "flow_diagram": render_flow,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="用 Pillow 把 HTML 渲染为 PNG")
    parser.add_argument("input", help="输入 HTML 文件路径")
    parser.add_argument("output", help="输出 PNG 文件路径")
    args = parser.parse_args()
    html_path = Path(args.input)
    out_path = Path(args.output)
    if not html_path.exists():
        logger.error("%s 不存在", html_path)
        sys.exit(1)
    html = html_path.read_text(encoding="utf-8-sig")
    tmpl = detect_template(html)
    if tmpl == "unknown":
        logger.error("无法识别 HTML 模板类型")
        sys.exit(1)
    RENDERERS[tmpl](html, str(out_path))
    logger.info("已用 Pillow 渲染(%s): %s", tmpl, out_path)


if __name__ == "__main__":
    main()
