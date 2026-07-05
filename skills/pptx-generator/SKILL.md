---
name: pptx-generator
description: "PPTX 直接生成器——从零创建、读取、修改、拆分、合并 PPTX 文件。常用工具链:python-pptx 读写 + LibreOffice + Poppler 转图检查。触发词:pptx 生成、创建 PPT、从零做 deck、PPTX 读写、PPTX 拆分合并。"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ppt, pptx, python-pptx, create, modify, deck]
    related_skills: [ppt-workflow-orchestrator, markdown-to-slides, template-layout-deck, powerpoint]
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



# PPTX 直接生成器 (pptx-generator)

> "从零创建 PPT,或者读取、修改、拆分、合并已有的 PPTX 文件。"

## 一、目标

把内容"按页精确"地写入 PPTX 文件,而不是像 Markdown 路径那样自动判断页面类型。适合需要严格控制每页版式、批量处理、有现成 JSON 规格的场景。

## 二、何时使用

- 需要从 JSON 规格精确生成 PPTX(每页指定 type、布局、文本、颜色、位置)
- 需要修改、拆分、合并已有 PPTX
- 需要提取 PPTX 的全部文本/备注/版式信息

## 三、操作规程

### Step 1: 准备 JSON 规格(spec)

```json
{
  "theme": {
    "primary_color": "1E2761",
    "accent_color": "F96167",
    "header_font": "Microsoft YaHei",
    "body_font": "Microsoft YaHei"
  },
  "slides": [
    {
      "type": "title",
      "title": "智能办公套件 V1.0 汇报",
      "subtitle": "2026 年中评审",
      "author": "张三"
    },
    {
      "type": "section",
      "title": "01 项目背景",
      "section_number": "01"
    },
    {
      "type": "bullet",
      "title": "三件事决定了这次升级",
      "bullets": [
        {"text": "WPS 集成需求", "level": 0},
        {"text": "本地搜索痛点", "level": 0},
        {"text": "知识库分散", "level": 0}
      ],
      "note": "演讲时停顿 2 秒,等观众反应。"
    },
    {
      "type": "two_column",
      "title": "对比:升级前 vs 升级后",
      "left": {
        "heading": "升级前",
        "items": ["手动检索 30 分钟", "文档分散在 5 个工具", "无知识沉淀机制"]
      },
      "right": {
        "heading": "升级后",
        "items": ["Everything 秒级检索", "统一 Obsidian Vault", "Markdown 自动归档"]
      }
    },
    {
      "type": "stat",
      "title": "效率提升",
      "stats": [
        {"value": "30min", "label": "→ 5s", "description": "本地文件检索时间"},
        {"value": "80%", "label": "覆盖", "description": "日常办公场景"},
        {"value": "0", "label": "额外费用", "description": "全部基于开源"}
      ]
    },
    {
      "type": "quote",
      "text": "AI 不是替代你,而是放大你",
      "attribution": "—— 项目愿景"
    },
    {
      "type": "thank_you",
      "title": "谢谢",
      "subtitle": "欢迎讨论"
    }
  ]
}
```

### Step 2: 渲染(spec → PPTX)

调用 `scripts/spec_to_pptx.py`,传入 spec.json → 输出 .pptx。

### Step 3: 后续操作(可选)

- **缩略图**: `python -m pptx-tools-thumbnail deck.pptx` 或 LibreOffice 转 PDF 后 pdftoppm
- **文本提取**: `python -c "from pptx import Presentation; ..."` 或 markitdown
- **拆分**: `python scripts/split_pptx.py deck.pptx output_dir`
- **合并**: `python scripts/merge_pptx.py file1.pptx file2.pptx output.pptx`

## 四、支持的页面类型

| type | 用途 | 必填字段 | 选填字段 |
|------|------|----------|----------|
| `title` | 封面 | title | subtitle, author, date |
| `section` | 章节过渡 | title | section_number |
| `bullet` | 项目符号 | title | bullets[], note |
| `two_column` | 左右对比 | title, left, right | |
| `three_column` | 三栏对比 | title, columns[3] | |
| `stat` | 大数字/统计 | title | stats[] |
| `quote` | 引用/金句 | text | attribution |
| `process` | 流程图 | title | steps[] |
| `table` | 表格 | title | headers[], rows[][] |
| `timeline` | 时间线 | title | events[] |
| `image_text` | 图文混排 | title, image_path | text |
| `thank_you` | 封底 | title | subtitle |

## 五、配套脚本

### `scripts/spec_to_pptx.py`

```python
#!/usr/bin/env python3
"""
PPTX 规格生成器:从 JSON spec 精确生成 PPTX
"""
import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN


def hex_to_rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def set_run(run, text, size, bold=False, color=None, font=None, italic=False):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    if font:
        run.font.name = font


def add_title(prs, theme, s):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    fill = blank.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(theme.get("primary_color", "1E2761"))
    tx = blank.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.33), Inches(2))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), s["title"], 54, bold=True,
            color=RGBColor(0xFF, 0xFF, 0xFF), font=theme.get("header_font", "Microsoft YaHei"))
    if s.get("subtitle"):
        stx = blank.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(12.33), Inches(1))
        stf = stx.text_frame
        sp = stf.paragraphs[0]
        sp.alignment = PP_ALIGN.CENTER
        set_run(sp.add_run(), s["subtitle"], 24, color=RGBColor(0xCA, 0xDC, 0xFC),
                font=theme.get("body_font", "Microsoft YaHei"))
    if s.get("author") or s.get("date"):
        atx = blank.shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(12.33), Inches(0.6))
        atf = atx.text_frame
        ap = atf.paragraphs[0]
        ap.alignment = PP_ALIGN.CENTER
        text = " · ".join(filter(None, [s.get("author"), s.get("date")]))
        set_run(ap.add_run(), text, 14, color=RGBColor(0xCA, 0xDC, 0xFC),
                font=theme.get("body_font", "Microsoft YaHei"))


def add_section(prs, theme, s):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    fill = blank.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(theme.get("primary_color", "1E2761"))
    if s.get("section_number"):
        ntx = blank.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.33), Inches(2))
        ntf = ntx.text_frame
        np_ = ntf.paragraphs[0]
        np_.alignment = PP_ALIGN.CENTER
        set_run(np_.add_run(), s["section_number"], 80, bold=True,
                color=hex_to_rgb(theme.get("accent_color", "F96167")),
                font=theme.get("header_font", "Microsoft YaHei"))
    tx = blank.shapes.add_textbox(Inches(0.5), Inches(5.0), Inches(12.33), Inches(1.5))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), s["title"], 36, bold=True,
            color=RGBColor(0xFF, 0xFF, 0xFF), font=theme.get("header_font", "Microsoft YaHei"))


def add_bullet(prs, theme, s):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    # 标题
    tx = blank.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12.33), Inches(1.2))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    set_run(p.add_run(), s["title"], 36, bold=True,
            color=hex_to_rgb(theme.get("primary_color", "1E2761")),
            font=theme.get("header_font", "Microsoft YaHei"))
    bar = blank.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.55), Inches(0.6), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = hex_to_rgb(theme.get("accent_color", "F96167"))
    bar.line.fill.background()

    # 要点
    if s.get("bullets"):
        bx = blank.shapes.add_textbox(Inches(0.7), Inches(2.0), Inches(11.8), Inches(5))
        bf = bx.text_frame
        bf.word_wrap = True
        for i, b in enumerate(s["bullets"]):
            p = bf.paragraphs[0] if i == 0 else bf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            p.space_after = Pt(12)
            indent = "    " * b.get("level", 0)
            set_run(p.add_run(), indent + "• " + b["text"], 22,
                    color=hex_to_rgb("212121"),
                    font=theme.get("body_font", "Microsoft YaHei"))

    # 备注
    if s.get("note"):
        blank.notes_slide.notes_text_frame.text = s["note"]


def add_two_column(prs, theme, s):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    tx = blank.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12.33), Inches(1.2))
    tf = tx.text_frame
    p = tf.paragraphs[0]
    set_run(p.add_run(), s["title"], 32, bold=True,
            color=hex_to_rgb(theme.get("primary_color", "1E2761")),
            font=theme.get("header_font", "Microsoft YaHei"))
    for idx, key in enumerate(["left", "right"]):
        col = s.get(key, {})
        cx = Inches(0.7 + idx * 6.2)
        col_box = blank.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), Inches(5.8), Inches(4.5))
        col_box.fill.solid()
        col_box.fill.fore_color.rgb = hex_to_rgb(
            theme.get("primary_color", "1E2761") if idx == 0 else theme.get("accent_color", "F96167")
        )
        col_box.line.fill.background()
        ctf = col_box.text_frame
        ctf.word_wrap = True
        ch = ctf.paragraphs[0]
        ch.alignment = PP_ALIGN.CENTER
        set_run(ch.add_run(), col.get("heading", ""), 26, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF), font=theme.get("header_font", "Microsoft YaHei"))
        for item in col.get("items", []):
            ip = ctf.add_paragraph()
            ip.alignment = PP_ALIGN.LEFT
            ip.space_before = Pt(8)
            set_run(ip.add_run(), "• " + item, 16,
                    color=RGBColor(0xFF, 0xFF, 0xFF), font=theme.get("body_font", "Microsoft YaHei"))


def add_stat(prs, theme, s):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    tx = blank.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12.33), Inches(1.2))
    tf = tx.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), s["title"], 32, bold=True,
            color=hex_to_rgb(theme.get("primary_color", "1E2761")),
            font=theme.get("header_font", "Microsoft YaHei"))
    stats = s.get("stats", [])
    if not stats:
        return
    width = 12.33 / len(stats)
    for i, st in enumerate(stats):
        cx = Inches(0.5 + i * width)
        box = blank.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), Inches(width - 0.3), Inches(4.5))
        box.fill.solid()
        box.fill.fore_color.rgb = hex_to_rgb(theme.get("secondary_color", "CADCFC"))
        box.line.fill.background()
        btf = box.text_frame
        btf.word_wrap = True
        vp = btf.paragraphs[0]
        vp.alignment = PP_ALIGN.CENTER
        set_run(vp.add_run(), st["value"], 60, bold=True,
                color=hex_to_rgb(theme.get("accent_color", "F96167")),
                font=theme.get("header_font", "Microsoft YaHei"))
        lp = btf.add_paragraph()
        lp.alignment = PP_ALIGN.CENTER
        lp.space_before = Pt(12)
        set_run(lp.add_run(), st.get("label", ""), 18, bold=True,
                color=hex_to_rgb(theme.get("primary_color", "1E2761")),
                font=theme.get("body_font", "Microsoft YaHei"))
        dp = btf.add_paragraph()
        dp.alignment = PP_ALIGN.CENTER
        dp.space_before = Pt(8)
        set_run(dp.add_run(), st.get("description", ""), 14,
                color=hex_to_rgb("212121"), font=theme.get("body_font", "Microsoft YaHei"))


def add_quote(prs, theme, s):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    fill = blank.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(theme.get("secondary_color", "CADCFC"))
    tx = blank.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11), Inches(3))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), '"' + s["text"] + '"', 40, italic=True,
            color=hex_to_rgb(theme.get("primary_color", "1E2761")),
            font=theme.get("header_font", "Microsoft YaHei"))
    if s.get("attribution"):
        atx = blank.shapes.add_textbox(Inches(1), Inches(5.5), Inches(11), Inches(1))
        atf = atx.text_frame
        ap = atf.paragraphs[0]
        ap.alignment = PP_ALIGN.CENTER
        set_run(ap.add_run(), s["attribution"], 18,
                color=hex_to_rgb(theme.get("primary_color", "1E2761")),
                font=theme.get("body_font", "Microsoft YaHei"))


def add_process(prs, theme, s):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    tx = blank.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12.33), Inches(1.2))
    tf = tx.text_frame
    p = tf.paragraphs[0]
    set_run(p.add_run(), s["title"], 32, bold=True,
            color=hex_to_rgb(theme.get("primary_color", "1E2761")),
            font=theme.get("header_font", "Microsoft YaHei"))
    steps = s.get("steps", [])
    if not steps:
        return
    n = len(steps)
    box_w = 12.33 / n
    for i, step in enumerate(steps):
        cx = Inches(0.5 + i * box_w + 0.1)
        # 圆圈编号
        circle = blank.shapes.add_shape(MSO_SHAPE.OVAL, cx + Inches(box_w / 2 - 0.4), Inches(2.0), Inches(0.8), Inches(0.8))
        circle.fill.solid()
        circle.fill.fore_color.rgb = hex_to_rgb(theme.get("accent_color", "F96167"))
        circle.line.fill.background()
        ctf = circle.text_frame
        cp = ctf.paragraphs[0]
        cp.alignment = PP_ALIGN.CENTER
        set_run(cp.add_run(), str(i + 1), 28, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF), font=theme.get("header_font", "Microsoft YaHei"))
        # 标题
        ttx = blank.shapes.add_textbox(cx, Inches(3.0), Inches(box_w - 0.2), Inches(0.8))
        ttf = ttx.text_frame
        ttf.word_wrap = True
        tp = ttf.paragraphs[0]
        tp.alignment = PP_ALIGN.CENTER
        set_run(tp.add_run(), step.get("title", ""), 16, bold=True,
                color=hex_to_rgb(theme.get("primary_color", "1E2761")),
                font=theme.get("header_font", "Microsoft YaHei"))
        # 描述
        dtx = blank.shapes.add_textbox(cx, Inches(3.8), Inches(box_w - 0.2), Inches(2.0))
        dtf = dtx.text_frame
        dtf.word_wrap = True
        dp = dtf.paragraphs[0]
        dp.alignment = PP_ALIGN.CENTER
        set_run(dp.add_run(), step.get("description", ""), 12,
                color=hex_to_rgb("212121"), font=theme.get("body_font", "Microsoft YaHei"))
        # 箭头
        if i < n - 1:
            arrow = blank.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, cx + Inches(box_w - 0.3), Inches(2.32), Inches(0.3), Inches(0.16))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = hex_to_rgb(theme.get("primary_color", "1E2761"))
            arrow.line.fill.background()


def add_table(prs, theme, s):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    tx = blank.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12.33), Inches(1.2))
    tf = tx.text_frame
    p = tf.paragraphs[0]
    set_run(p.add_run(), s["title"], 32, bold=True,
            color=hex_to_rgb(theme.get("primary_color", "1E2761")),
            font=theme.get("header_font", "Microsoft YaHei"))
    headers = s.get("headers", [])
    rows = s.get("rows", [])
    n_cols = len(headers) if headers else (len(rows[0]) if rows else 1)
    n_rows = len(rows) + (1 if headers else 0)
    if n_rows == 0:
        return
    table_shape = blank.shapes.add_table(n_rows, n_cols, Inches(0.5), Inches(2.0), Inches(12.33), Inches(4.5))
    tbl = table_shape.table
    if headers:
        for ci, h in enumerate(headers):
            cell = tbl.cell(0, ci)
            cell.text = h
            for p in cell.text_frame.paragraphs:
                for r in p.runs:
                    r.font.bold = True
                    r.font.size = Pt(16)
                    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    r.font.name = theme.get("header_font", "Microsoft YaHei")
            cell.fill.solid()
            cell.fill.fore_color.rgb = hex_to_rgb(theme.get("primary_color", "1E2761"))
    for ri, row in enumerate(rows):
        excel_row = ri + (1 if headers else 0)
        for ci, val in enumerate(row):
            cell = tbl.cell(excel_row, ci)
            cell.text = str(val)
            for p in cell.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(14)
                    r.font.color.rgb = hex_to_rgb("212121")
                    r.font.name = theme.get("body_font", "Microsoft YaHei")


def add_thank_you(prs, theme, s):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    fill = blank.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(theme.get("primary_color", "1E2761"))
    tx = blank.shapes.add_textbox(Inches(0.5), Inches(3.0), Inches(12.33), Inches(2))
    tf = tx.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), s["title"], 72, bold=True,
            color=RGBColor(0xFF, 0xFF, 0xFF), font=theme.get("header_font", "Microsoft YaHei"))
    if s.get("subtitle"):
        stx = blank.shapes.add_textbox(Inches(0.5), Inches(5.0), Inches(12.33), Inches(1))
        stf = stx.text_frame
        sp = stf.paragraphs[0]
        sp.alignment = PP_ALIGN.CENTER
        set_run(sp.add_run(), s["subtitle"], 24,
                color=RGBColor(0xCA, 0xDC, 0xFC), font=theme.get("body_font", "Microsoft YaHei"))


RENDERERS = {
    "title": add_title,
    "section": add_section,
    "bullet": add_bullet,
    "two_column": add_two_column,
    "three_column": add_two_column,  # 简化复用
    "stat": add_stat,
    "quote": add_quote,
    "process": add_process,
    "table": add_table,
    "thank_you": add_thank_you,
}


def main():
    if len(sys.argv) < 3:
        print("用法: spec_to_pptx.py <spec.json> <output.pptx>")
        sys.exit(1)
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out_path = Path(sys.argv[2])
    theme = spec.get("theme", {})

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    for slide in spec.get("slides", []):
        stype = slide.get("type", "bullet")
        renderer = RENDERERS.get(stype)
        if not renderer:
            print(f"警告:未知类型 {stype},跳过")
            continue
        renderer(prs, theme, slide)

    prs.save(str(out_path))
    print(f"已生成:{out_path} ({len(spec.get('slides', []))} 页)")


if __name__ == "__main__":
    main()
```

### `scripts/split_pptx.py` — 拆分

```python
#!/usr/bin/env python3
"""把一个 PPTX 按页拆成多个单页 PPTX"""
import sys
from pathlib import Path
from pptx import Presentation

if len(sys.argv) < 3:
    print("用法: split_pptx.py <input.pptx> <output_dir>")
    sys.exit(1)

src = Path(sys.argv[1])
out_dir = Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)
prs = Presentation(str(src))
template = Presentation()
template.slide_width = prs.slide_width
template.slide_height = prs.slide_height
for idx, slide in enumerate(prs.slides, 1):
    new_prs = Presentation()
    new_prs.slide_width = prs.slide_width
    new_prs.slide_height = prs.slide_height
    blank_layout = new_prs.slide_layouts[6]
    new_slide = new_prs.slides.add_slide(blank_layout)
    for shape in slide.shapes:
        el = shape.element
        new_slide.shapes._spTree.insert_element_before(el, "p:extLst")
    out_file = out_dir / f"slide_{idx:03d}.pptx"
    new_prs.save(str(out_file))
print(f"已拆分 {len(prs.slides)} 页到 {out_dir}")
```

### `scripts/merge_pptx.py` — 合并

```python
#!/usr/bin/env python3
"""合并多个 PPTX"""
import sys
from pathlib import Path
from pptx import Presentation

if len(sys.argv) < 4:
    print("用法: merge_pptx.py <out.pptx> <in1.pptx> <in2.pptx> [...]")
    sys.exit(1)
out_path = Path(sys.argv[1])
merged = Presentation(str(sys.argv[2]))
for src in sys.argv[3:]:
    prs = Presentation(str(src))
    for slide in prs.slides:
        blank_layout = merged.slide_layouts[6]
        new_slide = merged.slides.add_slide(blank_layout)
        for shape in slide.shapes:
            el = shape.element
            new_slide.shapes._spTree.insert_element_before(el, "p:extLst")
merged.save(str(out_path))
print(f"已合并到 {out_path}")
```

### `scripts/extract_text.py` — 文本提取

```python
#!/usr/bin/env python3
"""提取 PPTX 全部文本(标题 + 正文 + 备注)"""
import sys
from pathlib import Path
from pptx import Presentation

if len(sys.argv) < 2:
    print("用法: extract_text.py <file.pptx>")
    sys.exit(1)
prs = Presentation(sys.argv[1])
for idx, slide in enumerate(prs.slides, 1):
    print(f"\n===== 页 {idx} =====")
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                t = "".join(r.text for r in para.runs)
                if t.strip():
                    print(t)
    if slide.has_notes_slide:
        notes = slide.notes_slide.notes_text_frame.text
        if notes.strip():
            print(f"  [备注] {notes}")
```

## 六、风险评估

🟡 **中风险** —— 主要在本地读写 pptx 文件,但可能调用 LibreOffice/Poppler 转换工具链。

## 七、与上下 Skill 的衔接

- **上游**: `markdown-to-slides` 出初版,或直接由 `ppt-outline-builder` 出的 JSON spec 进入
- **下游**: `template-layout-deck` 在此基础上套用母版;`deck-review-publisher` 做质检