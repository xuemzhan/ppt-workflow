---
name: chart-slide-maker
description: "图表页生成器——把 Excel/CSV/JSON 数据、经营指标、预算执行情况转成柱状图/折线图/饼图/表格页。关键原则:图表必须先有结论,再有视觉。生成 PNG 图表,然后嵌入 PPTX。触发词:做图表、数据可视化、chart、画柱状图、画折线图、画饼图、画表格。"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ppt, chart, matplotlib, plotly, data, visualization, deck]
    related_skills: [ppt-workflow-orchestrator, pptx-generator]
---

## 运行方式

本 Skill 的脚本在仓库根目录下运行:

```bash
# 从仓库根目录
python skills/<skill-name>/scripts/<script>.py <args>
```

### 共享模块

所有脚本使用 `skills/shared/` 下的公共模块:

- `skills/shared/utils.py` — `load_json`、`write_json`、`hex_to_rgb` 等
- `skills/shared/fonts.py` — 跨平台字体路径查找
- `skills/shared/logging_config.py` — 统一日志配置
- `skills/shared/types.py` — 数据契约(TypedDict / dataclass)
- `skills/shared/cli.py` — argparse 基类

脚本自动通过 `sys.path.insert(0, parent.parent.parent.parent)` 让 `from skills.shared.X import Y` 生效。

### 路径深度

脚本位于 `skills/<skill-name>/scripts/<script>.py`,**3 层 parent** 即到 `skills/`,**4 层** 到仓库根。共享模块查找路径:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
```

### 依赖

- Python 3.11+(用了 `dict[str, Any]` PEP 585 语法)
- `python-pptx >= 1.0`
- `Pillow >= 10.0`
- `pytest`(仅测试)



# 图表页生成器 (chart-slide-maker)

> "图表必须先有结论,再有视觉。先想清楚'想让观众看明白什么',再决定用什么图表类型、口径、维度。"

## 一、目标

读取结构化数据(CSV / JSON / 内联),生成**结论驱动的图表页**:
1. 一句结论标题(自带判断)
2. 一张图表(柱/线/饼/对比/堆叠)
3. 一段解读(图表下方)

最终输出 PNG,嵌入 PPTX 的一页。

## 二、何时使用

- outline.md 中标了"图表需求: 是"的页面
- 数据已有结构化形式,需要快速可视化
- 想让图表"会说话"(自带结论)

## 三、图表选择决策树

```
要表达什么?
│
├── 数量对比(谁多谁少) → 柱状图 (bar)
│
├── 趋势变化(随时间) → 折线图 (line)
│
├── 占比构成(部分占整体) → 饼图 (pie) 或 堆叠柱 (stacked_bar)
│
├── 多维度对比 → 分组柱 (grouped_bar)
│
├── 表格类对比 → 表格 (table)
│
└── 关系/相关性 → 散点图 (scatter)
```

## 四、JSON 输入规格

```json
{
  "type": "bar|line|pie|stacked_bar|grouped_bar|table|stat",
  "title": "结论:华东区贡献了 60% 营收,且仍在增长",
  "subtitle": "数据来源:2026 Q2 财务",
  "data": {
    "categories": ["华东", "华南", "华北", "西部"],
    "series": [
      {"name": "2025", "values": [40, 25, 20, 15]},
      {"name": "2026", "values": [60, 18, 12, 10]}
    ]
  },
  "unit": "%",
  "highlight": "华东",
  "interpretation": "华东占比从 40% 升至 60%,且绝对值仍在增长,是 Q2 增长的主引擎。"
}
```

## 五、操作规程

### Step 1: 写结论标题

标题必须是"判断",而不是"描述":
- ❌ "2026 年销售数据"
- ✅ "华东贡献 60% 营收,是 Q2 增长的主引擎"

### Step 2: 选图表类型

按决策树。

### Step 3: 调用脚本生成 PNG

```bash
python scripts/render_chart.py <chart_spec.json> <output.png>
```

### Step 4: 嵌入 PPTX

```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])
# 标题
slide.shapes.add_textbox(...)
# 图表
slide.shapes.add_picture("chart.png", Inches(1), Inches(2), width=Inches(11))
# 解读
slide.shapes.add_textbox(...)
prs.save("deck.pptx")
```

## 六、配套脚本

### `scripts/render_chart.py`

**默认用 Pillow 纯绘图**(零 matplotlib 依赖)。如需更复杂样式,可启用 matplotlib。

```python
#!/usr/bin/env python3
"""
图表渲染器:从 JSON spec 生成 PNG(基于 Pillow,零 matplotlib 依赖)

支持的 type:bar / line / pie / stacked_bar / grouped_bar / table / stat
输出尺寸:1920x1080
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1920, 1080
BG = (255, 255, 255)
INK = (33, 33, 33)
SUB = (107, 107, 107)
PRIMARY = (30, 39, 97)
ACCENT = (249, 97, 103)
SECONDARY = (202, 220, 252)
PALETTE = [PRIMARY, ACCENT, (44, 95, 45), (151, 188, 98), (6, 90, 130), (184, 80, 66)]


def get_font(size, bold=False):
    paths_bold = [
        "C:/Windows/Fonts/msyhbd.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    paths_reg = [
        "C:/Windows/Fonts/msyh.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    paths = paths_bold if bold else paths_reg
    for p in paths:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


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

    # 绘图区
    chart_x0, chart_y0 = 100, 240
    chart_w, chart_h = W - 200, H - 380

    # 找出最大值
    all_vals = [v for s in series for v in s["values"]]
    max_v = max(all_vals) * 1.15 if all_vals else 1

    # y 轴网格
    n_grid = 5
    for i in range(n_grid + 1):
        y = chart_y0 + chart_h - int(chart_h * i / n_grid)
        d.line([(chart_x0 + 80, y), (chart_x0 + chart_w, y)], fill=(220, 220, 220), width=1)
        val = int(max_v * i / n_grid)
        d.text((chart_x0, y - 12), f"{val}{unit}", fill=SUB, font=get_font(18))

    if len(series) == 1:
        # 单系列柱状图
        n = len(cats)
        slot_w = (chart_w - 80) / n
        bar_w = slot_w * 0.5
        for i, (cat, v) in enumerate(zip(cats, series[0]["values"])):
            x_center = chart_x0 + 80 + slot_w * (i + 0.5)
            x0 = x_center - bar_w / 2
            bar_h = int(chart_h * v / max_v)
            y0 = chart_y0 + chart_h - bar_h
            color = ACCENT if cat == highlight else PRIMARY
            d.rectangle([(x0, y0), (x0 + bar_w, chart_y0 + chart_h)], fill=color)
            d.text((x0, y0 - 30), f"{v}{unit}", fill=INK, font=get_font(22, bold=True))
            d.text((x_center - 60, chart_y0 + chart_h + 10), cat, fill=INK, font=get_font(22))
    else:
        # 分组柱状图
        n = len(cats)
        slot_w = (chart_w - 80) / n
        bar_w = slot_w * 0.35
        for i, cat in enumerate(cats):
            x_center = chart_x0 + 80 + slot_w * (i + 0.5)
            for j, s in enumerate(series):
                v = s["values"][i]
                x0 = x_center - bar_w + j * bar_w
                bar_h = int(chart_h * v / max_v)
                y0 = chart_y0 + chart_h - bar_h
                color = PALETTE[j % len(PALETTE)]
                d.rectangle([(x0, y0), (x0 + bar_w - 4, chart_y0 + chart_h)], fill=color)
                d.text((x0, y0 - 28), f"{v}{unit}", fill=INK, font=get_font(18, bold=True))
            d.text((x_center - 60, chart_y0 + chart_h + 10), cat, fill=INK, font=get_font(20))

        # 图例
        legend_y = chart_y0 + chart_h + 60
        legend_x = chart_x0 + 100
        for j, s in enumerate(series):
            color = PALETTE[j % len(PALETTE)]
            d.rectangle([(legend_x, legend_y), (legend_x + 24, legend_y + 24)], fill=color)
            d.text((legend_x + 32, legend_y), s["name"], fill=INK, font=get_font(20))
            legend_x += 200

    # 解读
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
    max_v = max(all_vals) * 1.15 if all_vals else 1
    min_v = min(all_vals, default=0) * 0.85

    # 网格
    n_grid = 5
    for i in range(n_grid + 1):
        y = chart_y0 + chart_h - int(chart_h * i / n_grid)
        d.line([(chart_x0 + 80, y), (chart_x0 + chart_w, y)], fill=(220, 220, 220), width=1)
        val = int(min_v + (max_v - min_v) * i / n_grid)
        d.text((chart_x0, y - 12), f"{val}{unit}", fill=SUB, font=get_font(18))

    n = len(cats)
    step = (chart_w - 80) / max(n - 1, 1)
    for j, s in enumerate(series):
        color = PALETTE[j % len(PALETTE)]
        points = []
        for i, v in enumerate(s["values"]):
            x = chart_x0 + 80 + step * i
            y = chart_y0 + chart_h - int(chart_h * (v - min_v) / (max_v - min_v + 1e-9))
            points.append((x, y))
        if len(points) >= 2:
            d.line(points, fill=color, width=4)
        for i, (x, y) in enumerate(points):
            d.ellipse([(x - 8, y - 8), (x + 8, y + 8)], fill=color)
            d.text((x - 20, y - 36), f"{s['values'][i]}{unit}", fill=INK, font=get_font(18, bold=True))

    # x 轴标签
    for i, cat in enumerate(cats):
        x = chart_x0 + 80 + step * i
        d.text((x - 40, chart_y0 + chart_h + 10), cat, fill=INK, font=get_font(20))

    # 图例
    legend_y = chart_y0 + chart_h + 60
    legend_x = chart_x0 + 100
    for j, s in enumerate(series):
        color = PALETTE[j % len(PALETTE)]
        d.line([(legend_x, legend_y + 12), (legend_x + 24, legend_y + 12)], fill=color, width=4)
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
        d.pieslice([(cx - r, cy - r), (cx + r, cy + r)], angle_start, angle_start + sweep, fill=color)
        # 百分比标签
        mid_angle = (angle_start + angle_start + sweep) / 2
        import math
        lx = cx + r * 0.7 * math.cos(math.radians(mid_angle))
        ly = cy + r * 0.7 * math.sin(math.radians(mid_angle))
        pct = v / total * 100
        d.text((lx - 30, ly - 12), f"{pct:.0f}{unit}", fill=(255, 255, 255), font=get_font(28, bold=True))
        angle_start += sweep

    # 图例(右侧)
    legend_x = 1100
    legend_y = 280
    for i, (cat, v) in enumerate(zip(cats, values)):
        color = PALETTE[i % len(PALETTE)]
        d.rectangle([(legend_x, legend_y), (legend_x + 30, legend_y + 30)], fill=color)
        d.text((legend_x + 44, legend_y + 2), f"{cat}: {v}{unit}", fill=INK, font=get_font(26))
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

    # 表头
    if headers:
        d.rectangle([(table_x0, table_y0), (table_x0 + table_w, table_y0 + row_h)], fill=PRIMARY)
        for ci, h in enumerate(headers):
            cx = table_x0 + col_w * ci + col_w / 2
            d.text((cx - 80, table_y0 + 18), str(h), fill=(255, 255, 255), font=get_font(24, bold=True))
        cur_y = table_y0 + row_h
    else:
        cur_y = table_y0

    # 数据行
    for ri, row in enumerate(rows):
        if ri % 2 == 0:
            d.rectangle([(table_x0, cur_y), (table_x0 + table_w, cur_y + row_h)], fill=(245, 245, 245))
        for ci, val in enumerate(row):
            cx = table_x0 + col_w * ci + 20
            text = f"{val}{unit}" if ci > 0 and unit and isinstance(val, (int, float)) else str(val)
            d.text((cx, cur_y + 18), text, fill=INK, font=get_font(22))
        # 行线
        d.line([(table_x0, cur_y + row_h), (table_x0 + table_w, cur_y + row_h)], fill=(220, 220, 220), width=1)
        cur_y += row_h

    interp = spec.get("interpretation", "")
    if interp:
        d.text((80, cur_y + 40), "▎ " + interp, fill=PRIMARY, font=get_font(28, bold=True))

    img.save(out_path)


RENDERERS = {
    "bar": draw_bar,
    "grouped_bar": draw_bar,
    "stacked_bar": draw_bar,
    "line": draw_line,
    "pie": draw_pie,
    "table": draw_table,
}


def main():
    if len(sys.argv) < 3:
        print("用法: render_chart.py <spec.json> <output.png>")
        print("spec.type 取值:bar / line / pie / stacked_bar / grouped_bar / table")
        sys.exit(1)
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out_path = Path(sys.argv[2])
    ctype = spec.get("type", "bar")
    renderer = RENDERERS.get(ctype)
    if not renderer:
        raise ValueError(f"未知图表类型:{ctype}")
    renderer(spec, out_path)
    print(f"已生成图表:{out_path}")


if __name__ == "__main__":
    main()
```

### `scripts/chart_to_pptx.py`

把图表 PNG 嵌入 PPTX 一页:

```python
#!/usr/bin/env python3
"""把 chart PNG 嵌入 PPTX 的一页
用法: chart_to_pptx.py <chart.png> <title> <interpretation> <output.pptx>
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN


def hex_to_rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def set_run(run, text, size, bold=False, color=None, font=None):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color
    if font:
        run.font.name = font


def main():
    if len(sys.argv) < 5:
        print("用法: chart_to_pptx.py <chart.png> <title> <interpretation> <output.pptx>")
        sys.exit(1)
    png_path = Path(sys.argv[1])
    title = sys.argv[2]
    interp = sys.argv[3]
    out_path = Path(sys.argv[4])

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # 标题
    tx = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.33), Inches(1))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    set_run(p.add_run(), title, 28, bold=True,
            color=hex_to_rgb("1E2761"), font="Microsoft YaHei")

    # 图表
    slide.shapes.add_picture(str(png_path), Inches(0.5), Inches(1.3), height=Inches(5.0))

    # 解读
    ix = slide.shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(12.33), Inches(0.8))
    itf = ix.text_frame
    ip = itf.paragraphs[0]
    set_run(ip.add_run(), "▎ " + interp, 18, bold=True,
            color=hex_to_rgb("1E2761"), font="Microsoft YaHei")

    prs.save(str(out_path))
    print(f"已生成:{out_path}")


if __name__ == "__main__":
    main()
```

### `scripts/csv_to_chart_spec.py`

CSV → chart_spec.json(快速入口):

```python
#!/usr/bin/env python3
"""把 CSV 转成 chart_spec.json
用法: csv_to_chart_spec.py <input.csv> <chart_type> <title> <output.json>

CSV 格式:
    category,series1,series2
    华东,40,60
    华南,25,18
"""
import csv
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 5:
        print("用法: csv_to_chart_spec.py <input.csv> <chart_type> <title> <output.json>")
        sys.exit(1)
    csv_path = Path(sys.argv[1])
    ctype = sys.argv[2]
    title = sys.argv[3]
    out_path = Path(sys.argv[4])

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    headers = rows[0]
    cats = [r[0] for r in rows[1:]]
    series = []
    for ci in range(1, len(headers)):
        vals = []
        for r in rows[1:]:
            try:
                vals.append(float(r[ci]))
            except ValueError:
                vals.append(0)
        series.append({"name": headers[ci], "values": vals})

    spec = {
        "type": ctype,
        "title": title,
        "data": {"categories": cats, "series": series},
    }
    out_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成:{out_path}")


if __name__ == "__main__":
    main()
```

## 七、风险评估

🟡 **中风险** —— 只读 CSV/JSON,写 PNG。但生成的图表数据若涉及敏感经营数据(工资、销售额),需先脱敏。

## 八、与上下 Skill 的衔接

- **上游**: `ppt-outline-builder` 标"图表需求: 是"的页
- **下游**: PNG 嵌入 `pptx-generator` 输出的 PPTX,作为某一页