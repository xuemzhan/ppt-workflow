---
name: markdown-to-slides
description: "Markdown 转幻灯片——一个 Markdown 源文件,通过 python-pptx / Pandoc / Marp / Beamer 转成 PPTX/PDF/HTML。优势:版本管理、改动方便、批量生成。触发词:markdown 转 PPT、md 转幻灯片、Marp、Pandoc、slides.md 转 pptx。"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ppt, markdown, pandoc, marp, beamer, conversion, deck]
    related_skills: [ppt-workflow-orchestrator, deck-storyline-designer, pptx-generator]
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



# Markdown 转幻灯片 (markdown-to-slides)

> "一个 Markdown 源文件,可输出 PDF / PPTX / HTML。版本管理、改动方便、批量生成。"

## 一、目标

把带叙事弧的 `slides.md` 或 `storyline.md` 转换为可分发的幻灯片文件。本 Skill 默认走 `python-pptx` 路径(零依赖、可控、跨平台),并保留可选的 Pandoc / Marp / Beamer 路径供高级用户使用。

## 二、何时使用

- storyline.md 已经定型,需要先出"原型版"快速检视效果
- 同一份内容要做成多份不同格式(PDF 给阅读者、PPTX 给汇报者、HTML 内嵌网页)
- 内容需要版本管理(Git)、需要后续微调

## 三、支持的工具链

| 工具 | 输出 | 优势 | 劣势 |
|------|------|------|------|
| **python-pptx** ✅ 默认 | .pptx | 跨平台、零外部依赖、可二次编辑 | 样式受限于 pptx 能力 |
| **Pandoc + Beamer** | .pdf, .pptx | 学术场景强、模板生态丰富 | 需要 LaTeX 环境 |
| **Marp** | .html, .pdf | 一份 MD 出幻灯片+讲稿 | PPTX 输出为图片,不可编辑 |
| **revealjs / Slidev** | .html | 视觉效果强、动效丰富 | 不是 PPT 格式 |

## 四、操作规程(默认 python-pptx 路径)

### Step 1: 解析 Markdown

读取 slides.md,识别以下结构:

```markdown
# 主题

<!-- _class: cover -->

## 这是第一张幻灯片的标题

- 要点 1
- 要点 2

---

## 这是第二张幻灯片的标题

> 单行重点(speaker note / quote)

- 要点 A
- 要点 B
```

支持以下标记:

| 标记 | 含义 |
|------|------|
| `# 标题` | 演示主题(只取第一个) |
| `---` | 分页符 |
| `## 子标题` | 幻灯片标题 |
| `- 文本` | 项目符号 |
| `> 文本` | 引用/重点框 |
| `**粗体**` | 关键强调 |
| `\`数字\`` | 大数字展示 |
| `<!-- _class: ... -->` | 页面类型提示 |
| `<!-- _backgroundColor: ... -->` | 背景色提示 |

### Step 2: 确定页面类型

根据内容自动判断页面类型:

| 类型 | 触发特征 | 视觉模板 |
|------|----------|----------|
| 封面 (cover) | 第一页 | 居中大字标题 + 副标题 |
| 内容 (content) | 含 ≥3 个要点 | 标题 + 项目符号 |
| 钩子 (hook) | 含反直觉数字 | 大数字 + 标签 |
| 大数字 (stat) | 单个 `数字` + 标签 | 60-72pt 数字 |
| 对比 (compare) | 含 "vs"、"对比"、"vs." | 左右两栏 |
| 时间线 (timeline) | 含"阶段"、"Q1/Q2/Q3/Q4" | 时间轴 |
| 引用 (quote) | 整页 `>` 块 | 居中大字号 |
| 封底 (closing) | 末页 | 居中"谢谢/讨论" |

### Step 3: 应用样式

从 `template_profile.json` 读取配色、字体、对齐方式。默认配置:

```json
{
  "primary_color": "1E2761",
  "secondary_color": "CADCFC",
  "accent_color": "F96167",
  "header_font": "Microsoft YaHei",
  "body_font": "Microsoft YaHei",
  "slide_size": "16:9"
}
```

### Step 4: 生成 PPTX

调用 python-pptx 写出文件。

### Step 5: 生成 PDF/HTML(可选)

```bash
# PDF(需要 LibreOffice)
soffice --headless --convert-to pdf deck_draft.pptx

# HTML(Marp 路径)
marp slides.md --html --output slides.html
```

## 五、配套脚本

### `scripts/md_to_pptx.py`

```python
#!/usr/bin/env python3
"""
Markdown → PPTX 转换器(零外部依赖,基于 python-pptx)

用法:
    python md_to_pptx.py <input.md> <output.pptx> [template_profile.json]

支持语法:
    # 主题
    --- 分页
    ## 标题
    - 要点
    > 引用
    `数字`  大数字
    **粗体**
    <!-- _class: cover|hook|stat|compare|timeline|quote|closing -->
"""
import json
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR


# 默认配色:午夜高管(Midnight Executive)
DEFAULT_THEME = {
    "primary_color": "1E2761",
    "secondary_color": "CADCFC",
    "accent_color": "F96167",
    "text_dark": "212121",
    "text_light": "FFFFFF",
    "header_font": "Microsoft YaHei",
    "body_font": "Microsoft YaHei",
    "slide_size": "16:9",
}


def hex_to_rgb(hex_str):
    h = hex_str.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def parse_md_slides(md_text):
    """把 markdown 切成幻灯片列表"""
    # 第一个 # 标题作为演示主题(可选)
    theme_match = re.match(r"^#\s+(.+)$", md_text.split("\n", 1)[0] if md_text else "")
    theme = theme_match.group(1).strip() if theme_match else "未命名演示"

    # 去掉第一个 H1
    body = re.sub(r"^#\s+.+\n", "", md_text, count=1)

    # 按 --- 切分页
    raw_pages = re.split(r"^---\s*$", body, flags=re.MULTILINE)

    slides = []
    for raw in raw_pages:
        raw = raw.strip()
        if not raw:
            continue
        slide = parse_one_slide(raw)
        slides.append(slide)
    return theme, slides


def parse_one_slide(raw):
    """解析单页 markdown"""
    slide = {
        "title": "",
        "points": [],
        "quote": None,
        "stat": None,
        "class_hint": None,
        "bg_hint": None,
    }
    lines = raw.split("\n")
    for line in lines:
        s = line.rstrip()
        # HTML 注释 class 提示
        m = re.match(r"<!--\s*_class:\s*(\S+)\s*-->", s)
        if m:
            slide["class_hint"] = m.group(1)
            continue
        m = re.match(r"<!--\s*_backgroundColor:\s*(\S+)\s*-->", s)
        if m:
            slide["bg_hint"] = m.group(1)
            continue
        # 标题
        m = re.match(r"^##\s+(.+)$", s)
        if m:
            slide["title"] = m.group(1).strip()
            continue
        # 项目符号
        m = re.match(r"^[-*]\s+(.+)$", s)
        if m:
            slide["points"].append(m.group(1).strip())
            continue
        # 引用
        m = re.match(r"^>\s+(.+)$", s)
        if m:
            slide["quote"] = m.group(1).strip()
            continue
        # 大数字
        m = re.match(r"^`(\d[\d,.]*)\`\s*(.*)$", s)
        if m:
            slide["stat"] = {"number": m.group(1), "label": m.group(2).strip()}
            continue
        # 普通段落
        if s and not slide["title"]:
            slide["title"] = s
        elif s:
            slide["points"].append(s)
    return slide


def detect_class(slide, idx, total):
    """根据内容自动判断页面类型"""
    if slide.get("class_hint"):
        return slide["class_hint"]
    if idx == 0:
        return "cover"
    if idx == total - 1:
        return "closing"
    if slide.get("stat"):
        return "stat"
    if slide.get("quote") and not slide.get("points"):
        return "quote"
    if len(slide.get("points", [])) == 2 and any(
        kw in " ".join(slide["points"]).lower() for kw in ["vs", "对比", " vs ", " 对比 "]
    ):
        return "compare"
    if any(re.search(r"Q[1-4]|阶段|\d{4}年", p) for p in slide.get("points", [])):
        return "timeline"
    return "content"


def add_cover(prs, theme_cfg, slide):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    fill = blank.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(theme_cfg["primary_color"])

    tx = blank.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.33), Inches(2))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = slide["title"]
    r.font.size = Pt(54)
    r.font.bold = True
    r.font.color.rgb = hex_to_rgb(theme_cfg["text_light"])
    r.font.name = theme_cfg["header_font"]

    if slide.get("points"):
        sub = blank.shapes.add_textbox(Inches(0.5), Inches(5), Inches(12.33), Inches(1))
        sf = sub.text_frame
        sf.word_wrap = True
        sp = sf.paragraphs[0]
        sp.alignment = PP_ALIGN.CENTER
        sr = sp.add_run()
        sr.text = slide["points"][0]
        sr.font.size = Pt(20)
        sr.font.color.rgb = hex_to_rgb(theme_cfg["secondary_color"])
        sr.font.name = theme_cfg["body_font"]


def add_content(prs, theme_cfg, slide):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    # 标题
    tx = blank.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12.33), Inches(1.2))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = slide["title"]
    r.font.size = Pt(36)
    r.font.bold = True
    r.font.color.rgb = hex_to_rgb(theme_cfg["primary_color"])
    r.font.name = theme_cfg["header_font"]

    # 分隔装饰条(避免使用标题下划线 → 用色块)
    bar = blank.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.55), Inches(0.6), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = hex_to_rgb(theme_cfg["accent_color"])
    bar.line.fill.background()

    # 要点
    if slide["points"]:
        bx = blank.shapes.add_textbox(Inches(0.7), Inches(2.0), Inches(11.8), Inches(5))
        bf = bx.text_frame
        bf.word_wrap = True
        for i, point in enumerate(slide["points"]):
            p = bf.paragraphs[0] if i == 0 else bf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            p.space_after = Pt(10)
            # 处理粗体
            segments = re.split(r"(\*\*[^*]+\*\*)", point)
            for seg in segments:
                if seg.startswith("**") and seg.endswith("**"):
                    r = p.add_run()
                    r.text = seg[2:-2]
                    r.font.bold = True
                    r.font.color.rgb = hex_to_rgb(theme_cfg["accent_color"])
                elif seg:
                    r = p.add_run()
                    r.text = seg
                r.font.size = Pt(20)
                r.font.name = theme_cfg["body_font"]
                r.font.color.rgb = hex_to_rgb(theme_cfg["text_dark"])


def add_stat(prs, theme_cfg, slide):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    fill = blank.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(theme_cfg["primary_color"])

    # 大数字
    if slide.get("stat"):
        tx = blank.shapes.add_textbox(Inches(0.5), Inches(2.0), Inches(12.33), Inches(3))
        tf = tx.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = slide["stat"]["number"]
        r.font.size = Pt(96)
        r.font.bold = True
        r.font.color.rgb = hex_to_rgb(theme_cfg["accent_color"])
        r.font.name = theme_cfg["header_font"]

        # 标签
        lx = blank.shapes.add_textbox(Inches(0.5), Inches(5.0), Inches(12.33), Inches(1.5))
        lf = lx.text_frame
        lp = lf.paragraphs[0]
        lp.alignment = PP_ALIGN.CENTER
        lr = lp.add_run()
        lr.text = slide["stat"]["label"] or slide.get("title", "")
        lr.font.size = Pt(28)
        lr.font.color.rgb = hex_to_rgb(theme_cfg["text_light"])
        lr.font.name = theme_cfg["body_font"]


def add_quote(prs, theme_cfg, slide):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    fill = blank.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(theme_cfg["secondary_color"])

    tx = blank.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11), Inches(3))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = '"' + (slide.get("quote") or slide.get("title", "")) + '"'
    r.font.size = Pt(40)
    r.font.italic = True
    r.font.color.rgb = hex_to_rgb(theme_cfg["primary_color"])
    r.font.name = theme_cfg["header_font"]


def add_compare(prs, theme_cfg, slide):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    # 标题
    tx = blank.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12.33), Inches(1.2))
    tf = tx.text_frame
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = slide["title"]
    r.font.size = Pt(32)
    r.font.bold = True
    r.font.color.rgb = hex_to_rgb(theme_cfg["primary_color"])
    r.font.name = theme_cfg["header_font"]

    if len(slide["points"]) >= 2:
        left_text = slide["points"][0]
        right_text = slide["points"][1]
    else:
        left_text, right_text = "", ""

    # 左栏
    lb = blank.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(2.0), Inches(5.8), Inches(4.5))
    lb.fill.solid()
    lb.fill.fore_color.rgb = hex_to_rgb(theme_cfg["primary_color"])
    lb.line.fill.background()
    ltx = lb.text_frame
    ltx.word_wrap = True
    lp = ltx.paragraphs[0]
    lp.alignment = PP_ALIGN.CENTER
    lr = lp.add_run()
    lr.text = left_text
    lr.font.size = Pt(24)
    lr.font.color.rgb = hex_to_rgb(theme_cfg["text_light"])
    lr.font.name = theme_cfg["body_font"]

    # 右栏
    rb = blank.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.83), Inches(2.0), Inches(5.8), Inches(4.5))
    rb.fill.solid()
    rb.fill.fore_color.rgb = hex_to_rgb(theme_cfg["accent_color"])
    rb.line.fill.background()
    rtx = rb.text_frame
    rtx.word_wrap = True
    rp = rtx.paragraphs[0]
    rp.alignment = PP_ALIGN.CENTER
    rr = rp.add_run()
    rr.text = right_text
    rr.font.size = Pt(24)
    rr.font.color.rgb = hex_to_rgb(theme_cfg["text_light"])
    rr.font.name = theme_cfg["body_font"]


def add_timeline(prs, theme_cfg, slide):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    # 标题
    tx = blank.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12.33), Inches(1.2))
    tf = tx.text_frame
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = slide["title"]
    r.font.size = Pt(32)
    r.font.bold = True
    r.font.color.rgb = hex_to_rgb(theme_cfg["primary_color"])
    r.font.name = theme_cfg["header_font"]

    # 时间线轴
    line = blank.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(3.6), Inches(12.33), Inches(0.06))
    line.fill.solid()
    line.fill.fore_color.rgb = hex_to_rgb(theme_cfg["primary_color"])
    line.line.fill.background()

    points = slide.get("points", [])
    n = max(len(points), 1)
    step = 12.33 / max(n, 1)
    for i, p_text in enumerate(points):
        cx = Inches(0.5 + step * (i + 0.5))
        # 圆点
        dot = blank.shapes.add_shape(MSO_SHAPE.OVAL, cx - Inches(0.15), Inches(3.45), Inches(0.3), Inches(0.3))
        dot.fill.solid()
        dot.fill.fore_color.rgb = hex_to_rgb(theme_cfg["accent_color"])
        dot.line.fill.background()
        # 标签
        ltx = blank.shapes.add_textbox(cx - Inches(step / 2), Inches(2.0), Inches(step), Inches(1.3))
        ltf = ltx.text_frame
        ltf.word_wrap = True
        lp = ltf.paragraphs[0]
        lp.alignment = PP_ALIGN.CENTER
        lr = lp.add_run()
        lr.text = p_text[:30]
        lr.font.size = Pt(14)
        lr.font.bold = True
        lr.font.color.rgb = hex_to_rgb(theme_cfg["primary_color"])
        lr.font.name = theme_cfg["body_font"]


def add_closing(prs, theme_cfg, slide):
    blank = prs.slides.add_slide(prs.slide_layouts[6])
    fill = blank.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(theme_cfg["primary_color"])

    tx = blank.shapes.add_textbox(Inches(0.5), Inches(3.0), Inches(12.33), Inches(2))
    tf = tx.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = slide["title"] or "谢谢"
    r.font.size = Pt(60)
    r.font.bold = True
    r.font.color.rgb = hex_to_rgb(theme_cfg["text_light"])
    r.font.name = theme_cfg["header_font"]

    if slide.get("points"):
        stx = blank.shapes.add_textbox(Inches(0.5), Inches(5.0), Inches(12.33), Inches(2))
        stf = stx.text_frame
        for i, pt_text in enumerate(slide["points"]):
            sp = stf.paragraphs[0] if i == 0 else stf.add_paragraph()
            sp.alignment = PP_ALIGN.CENTER
            sr = sp.add_run()
            sr.text = pt_text
            sr.font.size = Pt(18)
            sr.font.color.rgb = hex_to_rgb(theme_cfg["secondary_color"])
            sr.font.name = theme_cfg["body_font"]


RENDERERS = {
    "cover": add_cover,
    "content": add_content,
    "hook": add_content,  # hook 也用 content 渲染,但强调样式
    "stat": add_stat,
    "quote": add_quote,
    "compare": add_compare,
    "timeline": add_timeline,
    "closing": add_closing,
}


def main():
    if len(sys.argv) < 3:
        print("用法: md_to_pptx.py <input.md> <output.pptx> [template_profile.json]")
        sys.exit(1)
    md_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    theme_cfg = dict(DEFAULT_THEME)
    if len(sys.argv) >= 4:
        prof = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
        theme_cfg.update(prof)

    md_text = md_path.read_text(encoding="utf-8")
    theme, slides = parse_md_slides(md_text)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    for idx, slide in enumerate(slides):
        cls = detect_class(slide, idx, len(slides))
        renderer = RENDERERS.get(cls, add_content)
        renderer(prs, theme_cfg, slide)

    prs.save(str(out_path))
    print(f"已生成:{out_path} ({len(slides)} 页)")


if __name__ == "__main__":
    main()
```

## 六、Marp 路径(可选)

`slides.md` 顶部加上 front-matter:

```markdown
---
marp: true
theme: default
paginate: true
backgroundColor: #1E2761
color: #FFFFFF
---

# 主题名

副标题

---

## 第一页标题

- 要点 1
- 要点 2
```

生成命令:

```bash
npx -y @marp-team/marp-cli slides.md --pptx -o deck.pptx
npx -y @marp-team/marp-cli slides.md --pdf -o deck.pdf
```

## 七、Pandoc 路径(可选)

```bash
pandoc slides.md -t beamer -o deck.pdf
pandoc slides.md -t pptx -o deck.pptx --reference-doc=template.pptx
```

## 八、风险评估

🟡 **中风险** —— 默认路径只读输入 md、写一个 pptx,但 Marp/Pandoc 会调用外部工具链,可能从网络下载依赖。

⚠️ **数据脱敏**:输入 slides.md 中的敏感数据(姓名/合同金额/工资)会被直接写入 PPTX。生成前请评估是否需要脱敏。

## 九、与上下 Skill 的衔接

- **上游**: `deck-storyline-designer` 输出 `storyline.md` → 转化为 `slides.md`(人工或 AI 协助)
- **下游**: `pptx-generator` 进一步加工(替换占位符、调版式),或 `template-layout-deck` 套正式模板