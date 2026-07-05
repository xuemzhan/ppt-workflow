#!/usr/bin/env python3
"""把多张幻灯片 PNG 拼成网格缩略图
用法: make_thumbnail_grid.py <output.jpg> <input1.jpg> [input2.jpg ...]
"""

# IMPORTANT: path setup must come BEFORE any skills.* imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import argparse
import logging

from skills.shared.fonts import get_font_path
from skills.shared.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

from PIL import Image, ImageDraw, ImageFont


def get_font(size, bold=False):
    """Get a Pillow ImageFont using shared/fonts for cross-platform path discovery."""
    candidates_bold = ["msyhbd.ttc", "PingFang.ttc", "DejaVuSans-Bold.ttf"]
    candidates_reg = ["msyh.ttc", "PingFang.ttc", "DejaVuSans.ttf"]
    for name in candidates_bold if bold else candidates_reg:
        try:
            path = get_font_path(name)
            if path and path != "PIL_DEFAULT":
                return ImageFont.truetype(path, size)
        except Exception:
            continue
    try:
        path = get_font_path()
        if path and path != "PIL_DEFAULT":
            return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default()


def main() -> None:
    parser = argparse.ArgumentParser(description="把多张幻灯片图拼成网格缩略图")
    parser.add_argument("output", help="输出 JPG/PNG 文件路径")
    parser.add_argument("images", nargs="+", help="输入图片文件路径")
    args = parser.parse_args()
    out_path = Path(args.output)
    images = [Image.open(p) for p in args.images]
    if not images:
        logger.error("未提供图片")
        sys.exit(1)

    cols = 4
    rows = (len(images) + cols - 1) // cols
    thumb_w = 480
    thumb_h = int(thumb_w * 9 / 16)
    label_h = 32
    cell_w = thumb_w
    cell_h = thumb_h + label_h

    grid = Image.new("RGB", (cols * cell_w, rows * cell_h), (240, 240, 240))
    draw = ImageDraw.Draw(grid)
    font = get_font(20, bold=True)

    for i, img in enumerate(images):
        row = i // cols
        col = i % cols
        thumb = img.copy()
        thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x_offset = col * cell_w + (thumb_w - thumb.width) // 2
        y_offset = row * cell_h
        grid.paste(thumb, (x_offset, y_offset))
        draw.rectangle(
            [
                (col * cell_w, row * cell_h + thumb_h),
                ((col + 1) * cell_w, row * cell_h + thumb_h + label_h),
            ],
            fill=(30, 39, 97),
        )
        draw.text(
            (col * cell_w + 10, row * cell_h + thumb_h + 5),
            f"页 {i + 1}",
            fill=(255, 255, 255),
            font=font,
        )

    grid.save(str(out_path), "JPEG", quality=85)
    logger.info("已生成缩略图网格: %s", out_path)


if __name__ == "__main__":
    main()
