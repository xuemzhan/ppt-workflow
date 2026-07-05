#!/usr/bin/env python3
"""图表渲染器:从 JSON spec 生成 PNG(基于 Pillow,零 matplotlib 依赖)

支持的 type:bar / line / pie / stacked_bar / grouped_bar / table
输出尺寸:1920x1080

特性:
- 数量级自适应:当数据最大值/最小值 > 50 倍,自动切换对数刻度(避免小柱不可见)
- 单系列/多系列自适应布局
- 单位标签智能格式化(整数/小数/科学记数)
"""

# IMPORTANT: path setup must come BEFORE any skills.* imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import argparse
import logging
import math

from skills.shared.fonts import get_font_path
from skills.shared.logging_config import setup_logging
from skills.shared.utils import load_json

setup_logging()
logger = logging.getLogger(__name__)

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG = (255, 255, 255)
INK = (33, 33, 33)
SUB = (107, 107, 107)
PRIMARY = (30, 39, 97)
ACCENT = (249, 97, 103)
PALETTE = [PRIMARY, ACCENT, (44, 95, 45), (151, 188, 98), (6, 90, 130), (184, 80, 66)]

# 数量级阈值:当数据最大值/最小值超过此倍数,自动切换为对数刻度
MAGNITUDE_LOG_THRESHOLD = 50


def is_log_needed(values):
    """判断是否需要用对数刻度:所有正值 且 max/min > 阈值"""
    pos = [v for v in values if v > 0]
    if len(pos) < 2:
        return False
    return max(pos) / max(min(pos), 1e-9) > MAGNITUDE_LOG_THRESHOLD


def get_font(size, bold=False):
    """Get a Pillow ImageFont using shared/fonts for cross-platform path discovery."""
    candidates_bold = ["msyhbd.ttc", "PingFang.ttc", "DejaVuSans-Bold.ttf"]
    candidates_reg = ["msyh.ttc", "PingFang.ttc", "DejaVuSans.ttf"]
    # Try preferred font names in order
    for name in candidates_bold if bold else candidates_reg:
        try:
            path = get_font_path(name)
            if path and path != "PIL_DEFAULT":
                return ImageFont.truetype(path, size)
        except Exception:
            continue
    # Fallback: try shared's generic selection
    try:
        path = get_font_path()
        if path and path != "PIL_DEFAULT":
            return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default()


def fmt_value(v, unit):
    """数值标签格式:大数取整,小数保留 2-3 位"""
    if v >= 100:
        s = f"{int(v)}"
    elif v >= 1:
        s = f"{v:.1f}"
    elif v >= 0.01:
        s = f"{v:.2f}"
    else:
        s = f"{v:.3f}"
    return f"{s}{unit}"


def fmt_axis(v, unit):
    """Y 轴刻度标签"""
    if v >= 1000:
        return f"{int(v / 1000)}k{unit}"
    if v >= 1:
        return f"{int(v)}{unit}"
    if v >= 0.01:
        return f"{v:.2f}{unit}"
    return f"{v:.3f}{unit}"


def draw_bar(spec, out_path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title = spec.get("title", "")
    subtitle = spec.get("subtitle", "")
    data = spec["data"]
    cats = data["categories"]
    series = data["series"]
    unit = spec.get("unit", "")
    highlight = spec.get("highlight", "")

    d.text((80, 60), title, fill=PRIMARY, font=get_font(48, bold=True))
    if subtitle:
        d.text((80, 130), subtitle, fill=SUB, font=get_font(24))

    chart_x0, chart_y0 = 100, 240
    chart_w, chart_h = W - 200, H - 380

    all_vals = [v for s in series for v in s["values"]]
    log_mode = is_log_needed(all_vals)

    if log_mode:
        import math

        pos = [v for v in all_vals if v > 0]
        log_min = math.floor(math.log10(min(pos)))
        log_max = math.ceil(math.log10(max(pos)))
        # 标题加 [对数刻度] 提示
        d.text(
            (80, 1050),
            "[对数刻度 · Y 轴按 10^n 缩放]",
            fill=(180, 60, 60),
            font=get_font(20),
        )
        n_grid = log_max - log_min
        for i in range(n_grid + 1):
            y = chart_y0 + chart_h - int(chart_h * i / max(n_grid, 1))
            d.line(
                [(chart_x0 + 80, y), (chart_x0 + chart_w, y)],
                fill=(220, 220, 220),
                width=1,
            )
            grid_val = 10 ** (log_min + i)
            d.text(
                (chart_x0, y - 12),
                fmt_axis(grid_val, unit),
                fill=SUB,
                font=get_font(18),
            )

        def v_to_h(v):
            if v <= 0:
                v = 10**log_min
            lv = math.log10(v)
            return int(chart_h * (lv - log_min) / max(log_max - log_min, 1))
    else:
        max_v = max(all_vals) * 1.15 if all_vals else 1
        n_grid = 5
        for i in range(n_grid + 1):
            y = chart_y0 + chart_h - int(chart_h * i / n_grid)
            d.line(
                [(chart_x0 + 80, y), (chart_x0 + chart_w, y)],
                fill=(220, 220, 220),
                width=1,
            )
            val = max_v * i / n_grid
            d.text((chart_x0, y - 12), fmt_axis(val, unit), fill=SUB, font=get_font(18))

        def v_to_h(v):
            return int(chart_h * v / max_v)

    if len(series) == 1:
        n = len(cats)
        slot_w = (chart_w - 80) / n
        bar_w = slot_w * 0.5
        for i, (cat, v) in enumerate(zip(cats, series[0]["values"])):
            x_center = chart_x0 + 80 + slot_w * (i + 0.5)
            x0 = x_center - bar_w / 2
            bar_h = v_to_h(v)
            bar_h = max(bar_h, 4)  # 即使 v 很小,也保留 4px 高度,便于标注
            y0 = chart_y0 + chart_h - bar_h
            color = ACCENT if cat == highlight else PRIMARY
            d.rectangle([(x0, y0), (x0 + bar_w, chart_y0 + chart_h)], fill=color)
            d.text(
                (x0, y0 - 30),
                fmt_value(v, unit),
                fill=INK,
                font=get_font(22, bold=True),
            )
            d.text(
                (x_center - 60, chart_y0 + chart_h + 10),
                cat,
                fill=INK,
                font=get_font(22),
            )
    else:
        n = len(cats)
        slot_w = (chart_w - 80) / n
        bar_w = slot_w * 0.35
        for i, cat in enumerate(cats):
            x_center = chart_x0 + 80 + slot_w * (i + 0.5)
            for j, s in enumerate(series):
                v = s["values"][i]
                x0 = x_center - bar_w + j * bar_w
                bar_h = v_to_h(v)
                bar_h = max(bar_h, 4)
                y0 = chart_y0 + chart_h - bar_h
                color = PALETTE[j % len(PALETTE)]
                d.rectangle(
                    [(x0, y0), (x0 + bar_w - 4, chart_y0 + chart_h)], fill=color
                )
                d.text(
                    (x0, y0 - 28),
                    fmt_value(v, unit),
                    fill=INK,
                    font=get_font(18, bold=True),
                )
            d.text(
                (x_center - 60, chart_y0 + chart_h + 10),
                cat,
                fill=INK,
                font=get_font(20),
            )

        legend_y = chart_y0 + chart_h + 60
        legend_x = chart_x0 + 100
        for j, s in enumerate(series):
            color = PALETTE[j % len(PALETTE)]
            d.rectangle(
                [(legend_x, legend_y), (legend_x + 24, legend_y + 24)], fill=color
            )
            d.text((legend_x + 32, legend_y), s["name"], fill=INK, font=get_font(20))
            legend_x += 200

    interp = spec.get("interpretation", "")
    if interp:
        d.text((80, H - 100), "▎ " + interp, fill=PRIMARY, font=get_font(28, bold=True))

    img.save(out_path)


def draw_line(spec, out_path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title = spec.get("title", "")
    data = spec["data"]
    cats = data["categories"]
    series = data["series"]
    unit = spec.get("unit", "")

    d.text((80, 60), title, fill=PRIMARY, font=get_font(48, bold=True))
    if spec.get("subtitle"):
        d.text((80, 130), spec["subtitle"], fill=SUB, font=get_font(24))

    chart_x0, chart_y0 = 100, 240
    chart_w, chart_h = W - 200, H - 380

    all_vals = [v for s in series for v in s["values"]]
    log_mode = is_log_needed(all_vals)

    if log_mode:
        import math

        pos = [v for v in all_vals if v > 0]
        log_min = math.floor(math.log10(min(pos)))
        log_max = math.ceil(math.log10(max(pos)))
        d.text(
            (80, 1050),
            "[对数刻度 · Y 轴按 10^n 缩放]",
            fill=(180, 60, 60),
            font=get_font(20),
        )
        n_grid = log_max - log_min
        for i in range(n_grid + 1):
            y = chart_y0 + chart_h - int(chart_h * i / max(n_grid, 1))
            d.line(
                [(chart_x0 + 80, y), (chart_x0 + chart_w, y)],
                fill=(220, 220, 220),
                width=1,
            )
            grid_val = 10 ** (log_min + i)
            d.text(
                (chart_x0, y - 12),
                fmt_axis(grid_val, unit),
                fill=SUB,
                font=get_font(18),
            )

        def v_to_y(v):
            if v <= 0:
                v = 10**log_min
            lv = math.log10(v)
            return (
                chart_y0
                + chart_h
                - int(chart_h * (lv - log_min) / max(log_max - log_min, 1))
            )
    else:
        max_v = max(all_vals) * 1.15 if all_vals else 1
        min_v = min(all_vals, default=0) * 0.85
        n_grid = 5
        for i in range(n_grid + 1):
            y = chart_y0 + chart_h - int(chart_h * i / n_grid)
            d.line(
                [(chart_x0 + 80, y), (chart_x0 + chart_w, y)],
                fill=(220, 220, 220),
                width=1,
            )
            val = min_v + (max_v - min_v) * i / n_grid
            d.text((chart_x0, y - 12), fmt_axis(val, unit), fill=SUB, font=get_font(18))

        def v_to_y(v):
            return (
                chart_y0
                + chart_h
                - int(chart_h * (v - min_v) / max(max_v - min_v, 1e-9))
            )

    n = len(cats)
    step = (chart_w - 80) / max(n - 1, 1)
    for j, s in enumerate(series):
        color = PALETTE[j % len(PALETTE)]
        points = []
        for i, v in enumerate(s["values"]):
            x = chart_x0 + 80 + step * i
            y = v_to_y(v)
            points.append((x, y))
        if len(points) >= 2:
            d.line(points, fill=color, width=4)
        for i, (x, y) in enumerate(points):
            d.ellipse([(x - 8, y - 8), (x + 8, y + 8)], fill=color)
            d.text(
                (x - 20, y - 36),
                fmt_value(s["values"][i], unit),
                fill=INK,
                font=get_font(18, bold=True),
            )

    for i, cat in enumerate(cats):
        x = chart_x0 + 80 + step * i
        d.text((x - 40, chart_y0 + chart_h + 10), cat, fill=INK, font=get_font(20))

    legend_y = chart_y0 + chart_h + 60
    legend_x = chart_x0 + 100
    for j, s in enumerate(series):
        color = PALETTE[j % len(PALETTE)]
        d.line(
            [(legend_x, legend_y + 12), (legend_x + 24, legend_y + 12)],
            fill=color,
            width=4,
        )
        d.text((legend_x + 32, legend_y), s["name"], fill=INK, font=get_font(20))
        legend_x += 200

    interp = spec.get("interpretation", "")
    if interp:
        d.text((80, H - 100), "▎ " + interp, fill=PRIMARY, font=get_font(28, bold=True))

    img.save(out_path)


def draw_pie(spec, out_path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title = spec.get("title", "")
    data = spec["data"]
    cats = data["categories"]
    series = data["series"]
    unit = spec.get("unit", "%")

    d.text((80, 60), title, fill=PRIMARY, font=get_font(48, bold=True))

    values = series[0]["values"]
    total = sum(values)

    cx, cy = 600, 600
    r = 320
    angle_start = -90
    for i, (cat, v) in enumerate(zip(cats, values)):
        sweep = v / total * 360
        color = PALETTE[i % len(PALETTE)]
        d.pieslice(
            [(cx - r, cy - r), (cx + r, cy + r)],
            angle_start,
            angle_start + sweep,
            fill=color,
        )
        mid_angle = (angle_start + angle_start + sweep) / 2
        lx = cx + r * 0.7 * math.cos(math.radians(mid_angle))
        ly = cy + r * 0.7 * math.sin(math.radians(mid_angle))
        pct = v / total * 100
        d.text(
            (lx - 30, ly - 12),
            f"{pct:.0f}{unit}",
            fill=(255, 255, 255),
            font=get_font(28, bold=True),
        )
        angle_start += sweep

    legend_x = 1100
    legend_y = 280
    for i, (cat, v) in enumerate(zip(cats, values)):
        color = PALETTE[i % len(PALETTE)]
        d.rectangle([(legend_x, legend_y), (legend_x + 30, legend_y + 30)], fill=color)
        d.text(
            (legend_x + 44, legend_y + 2),
            f"{cat}: {v}{unit}",
            fill=INK,
            font=get_font(26),
        )
        legend_y += 60

    interp = spec.get("interpretation", "")
    if interp:
        d.text((80, H - 100), "▎ " + interp, fill=PRIMARY, font=get_font(28, bold=True))

    img.save(out_path)


def draw_table(spec, out_path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title = spec.get("title", "")
    headers = spec["data"].get("headers", [])
    rows = spec["data"].get("rows", [])
    unit = spec.get("unit", "")

    d.text((80, 60), title, fill=PRIMARY, font=get_font(48, bold=True))

    n_cols = len(headers) if headers else (len(rows[0]) if rows else 1)
    n_rows = len(rows) + (1 if headers else 0)
    if n_rows == 0:
        img.save(out_path)
        return

    table_x0, table_y0 = 100, 200
    table_w = W - 200
    col_w = table_w / n_cols
    row_h = min(80, (H - 360) / n_rows)

    if headers:
        d.rectangle(
            [(table_x0, table_y0), (table_x0 + table_w, table_y0 + row_h)], fill=PRIMARY
        )
        for ci, h in enumerate(headers):
            cx = table_x0 + col_w * ci + col_w / 2
            d.text(
                (cx - 80, table_y0 + 18),
                str(h),
                fill=(255, 255, 255),
                font=get_font(24, bold=True),
            )
        cur_y = table_y0 + row_h
    else:
        cur_y = table_y0

    for ri, row in enumerate(rows):
        if ri % 2 == 0:
            d.rectangle(
                [(table_x0, cur_y), (table_x0 + table_w, cur_y + row_h)],
                fill=(245, 245, 245),
            )
        for ci, val in enumerate(row):
            cx = table_x0 + col_w * ci + 20
            text = (
                f"{val}{unit}"
                if ci > 0 and unit and isinstance(val, (int, float))
                else str(val)
            )
            d.text((cx, cur_y + 18), text, fill=INK, font=get_font(22))
        d.line(
            [(table_x0, cur_y + row_h), (table_x0 + table_w, cur_y + row_h)],
            fill=(220, 220, 220),
            width=1,
        )
        cur_y += row_h

    interp = spec.get("interpretation", "")
    if interp:
        d.text(
            (80, cur_y + 40), "▎ " + interp, fill=PRIMARY, font=get_font(28, bold=True)
        )

    img.save(out_path)


RENDERERS = {
    "bar": draw_bar,
    "grouped_bar": draw_bar,
    "stacked_bar": draw_bar,
    "line": draw_line,
    "pie": draw_pie,
    "table": draw_table,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="从 JSON spec 生成图表 PNG")
    parser.add_argument("spec", help="图表 JSON spec 文件路径")
    parser.add_argument("output", help="输出 PNG 文件路径")
    args = parser.parse_args()
    spec = load_json(Path(args.spec))
    out_path = Path(args.output)
    ctype = spec.get("type", "bar")
    renderer = RENDERERS.get(ctype)
    if not renderer:
        raise ValueError(f"未知图表类型: {ctype}")
    renderer(spec, out_path)
    logger.info("已生成图表: %s", out_path)


if __name__ == "__main__":
    main()
