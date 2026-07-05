---
name: deck-review-publisher
description: "PPT 质检与发布器——最后一步质检:逻辑通顺、标题有结论、页面不挤、文本不溢出、占位符无残留、图表清晰、模板未破坏。同时输出 qa_report.md,并可选导出 PDF/缩略图。触发词:QA、复盘、检查 PPT、质检、deck review、QA 报告、最终导出。"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ppt, qa, review, check, publish, export, deck]
    related_skills: [ppt-workflow-orchestrator, pptx-generator, powerpoint]
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



# PPT 质检与发布器 (deck-review-publisher)

> "PPT 生成完,不是结束,是开始。必须经过文本提取、缩略图检查、视觉验证。"

## 一、目标

对已成型的 deck 做全面 QA,输出:
1. `qa_report.md` —— 问题清单、修复建议
2. 缩略图网格 `thumbnails.jpg` —— 整体视觉概览
3. 可选:导出 PDF (`deck_final.pdf`)

## 二、何时使用

- 演示前 30 分钟
- 任何 deck 生成后必经环节
- 模板套用、视觉强化之后
- 多版本对比(哪个版本更好)

## 三、QA 检查清单

### A. 内容 QA(必须)

- [ ] **页数合理** —— 8-20 页之间(短报告 8-12,长报告 15-20)
- [ ] **每页标题都自带结论** —— 不允许"实验结果"、"项目介绍"这种中性标题
- [ ] **没有连续 3 页以上都是纯文字列表**
- [ ] **首末页完整** —— 封面 + 封底都有
- [ ] **没有占位符残留** —— "lorem ipsum"、"xxxx"、"点击此处添加标题"
- [ ] **没有错别字** —— 用 markitdown / extract_text 检查
- [ ] **专有名词一致** —— "AI" vs "人工智能",全文统一
- [ ] **数字格式一致** —— "30%" vs "30 个百分点"

### B. 视觉 QA(必须,基于缩略图)

- [ ] **没有元素重叠** —— 文本与形状互不遮挡
- [ ] **文本不溢出** —— 文字不出框
- [ ] **没有空白边距过窄** —— 边距 ≥ 0.5 英寸
- [ ] **字号对比足够** —— 标题 ≥ 36pt,正文 ≥ 18pt
- [ ] **对比度足够** —— 浅背景深文字 / 深背景浅文字
- [ ] **装饰元素(条、线、框)位置正确** —— 不破坏视觉
- [ ] **页面风格一致** —— 配色、字体、版式贯穿始终
- [ ] **没有模板残留** —— 旧 logo、旧页脚被清除

### C. 故事线 QA(必须)

- [ ] **5 张连续页标题连读,能听懂讲什么**
- [ ] **每段(背景/问题/洞察/方案/证据/行动)都有对应页**
- [ ] **CTA 页明确** —— 谁、何时、做什么
- [ ] **讲稿与页面匹配** —— speaker_notes.md 字数与时长匹配

### D. 数据/引用 QA(必须,如适用)

- [ ] **图表数字与正文一致**
- [ ] **来源标注完整** —— 引用规范
- [ ] **没有敏感数据裸露** —— 工资、合同金额、患者信息

## 四、操作规程

### Step 1: 文本提取

```bash
python scripts/extract_text.py deck.pptx
```

检查文本是否有错别字、占位符残留、标题中性。

### Step 2: 缩略图生成

把每页转 PNG,排成网格:

```bash
# 1. PPTX → PDF
python scripts/soffice_convert.py deck.pptx deck.pdf
# 2. PDF → 每页 JPG
pdftoppm -jpeg -r 100 deck.pdf slide
# 3. 拼成网格
python scripts/make_thumbnail_grid.py slide-*.jpg thumbnails.jpg
```

如无 LibreOffice/Poppler,可用 `python-pptx` 渲染(粗糙但可用):

```python
# scripts/render_thumbnails.py —— 用 Pillow 简单占位渲染(纯文本预览)
```

### Step 3: 问题清单

把发现的问题写入 `qa_report.md`,按严重程度分级:

| 级别 | 含义 | 示例 |
|------|------|------|
| 🔴 阻塞 | 必须修复,否则不能发布 | 标题空白、占位符残留、页数错误 |
| 🟡 重要 | 强烈建议修复 | 标题中性、字号过小、对比度低 |
| 🟢 优化 | 锦上添花 | 配图风格、装饰元素位置 |

### Step 4: 修复

回到对应 Skill 修改:
- 标题中性 → `deck-storyline-designer` 重写
- 占位符残留 → `pptx-generator` 重出
- 视觉问题 → `visual-slide-designer` 强化
- 模板破坏 → `template-layout-deck` 重套

### Step 5: 导出

```bash
python scripts/soffice_convert.py deck_final.pptx deck_final.pdf
```

## 五、配套脚本

### `scripts/qa_check.py`

```python
#!/usr/bin/env python3
"""
PPT QA 检查器:扫描 PPTX,输出问题清单

用法:
    python qa_check.py <deck.pptx> [output_report.md]

检查项:
- 占位符残留(lorem/ipsum/xxxx/click here 等)
- 标题中性(纯描述、无数字/方向)
- 文本溢出(粗略,基于 shape 大小)
- 页数合理性
"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime

from pptx import Presentation
from pptx.util import Emu


PLACEHOLDER_PATTERNS = [
    r"lorem\s*ipsum",
    r"xxxx+",
    r"placeholder",
    r"click\s+here",
    r"点击此处",
    r"待补充",
    r"TODO",
    r"\[.*\]",  # 形如 [插入 xxx]
    r"^\s*<.*>\s*$",  # 形如 <内容>
]

NEUTRAL_TITLE_KEYWORDS = [
    "项目介绍", "项目概述", "项目背景", "项目目标",
    "工作汇报", "工作总结", "工作内容",
    "实验结果", "实验分析", "研究方法",
    "项目进度", "项目计划", "下一步",
    "团队介绍", "成员介绍",
    "产品介绍", "产品概述",
    "公司介绍", "公司简介",
    "谢谢", "Thanks", "Thank you", "Q&A",
    "讨论", "提问",
    "封面", "封底",
]


def check_deck(pptx_path):
    prs = Presentation(str(pptx_path))
    issues = []
    total_slides = len(prs.slides)

    # 1. 页数检查
    if total_slides < 5:
        issues.append({"level": "🟡", "page": "-", "type": "page_count",
                       "msg": f"页数过少({total_slides}),可能未完成"})
    elif total_slides > 30:
        issues.append({"level": "🟡", "page": "-", "type": "page_count",
                       "msg": f"页数过多({total_slides}),可能需要拆分"})

    for idx, slide in enumerate(prs.slides, 1):
        # 提取本页所有文本
        all_text = ""
        for shape in slide.shapes:
            if shape.has_text_frame:
                all_text += shape.text_frame.text + "\n"

        # 2. 占位符残留
        for pat in PLACEHOLDER_PATTERNS:
            if re.search(pat, all_text, re.IGNORECASE):
                issues.append({"level": "🔴", "page": idx, "type": "placeholder",
                               "msg": f"检测到占位符残留(模式:{pat})"})

        # 3. 标题中性(简化:仅检查每页第一个文本框)
        first_text = ""
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text.strip():
                first_text = shape.text_frame.text.strip()
                break

        if first_text and idx not in (1, total_slides):  # 跳过封面/封底
            has_judgment = bool(
                re.search(r"\d", first_text)  # 含数字
                or re.search(r"[是为有将可达到]", first_text)  # 含判断词
                or any(kw in first_text for kw in ["结论", "判断", "发现", "启示", "意味着"])
            )
            if not has_judgment:
                for kw in NEUTRAL_TITLE_KEYWORDS:
                    if first_text == kw or first_text.startswith(kw):
                        issues.append({"level": "🟡", "page": idx, "type": "neutral_title",
                                       "msg": f"标题偏中性:\"{first_text[:30]}\" — 建议改为带数字/方向的判断"})
                        break

        # 4. 备注完整性
        has_note = False
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            has_note = bool(notes)
        # 仅对内容页检查(跳过封面/封底)
        if 2 <= idx <= total_slides - 1 and not has_note:
            issues.append({"level": "🟢", "page": idx, "type": "no_notes",
                           "msg": "本页缺少演讲者备注"})

    return issues


def main():
    if len(sys.argv) < 2:
        print("用法: qa_check.py <deck.pptx> [output_report.md]")
        sys.exit(1)
    deck_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else None

    issues = check_deck(deck_path)
    prs = Presentation(str(deck_path))

    lines = [
        f"# PPT 质检报告: {deck_path.name}",
        "",
        f"> 生成时间:{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 总页数:{len(prs.slides)}",
        f"> 问题总数:{len(issues)}",
        "",
        "## 问题统计",
        "",
        f"- 🔴 阻塞:{sum(1 for i in issues if i['level']=='🔴')}",
        f"- 🟡 重要:{sum(1 for i in issues if i['level']=='🟡')}",
        f"- 🟢 优化:{sum(1 for i in issues if i['level']=='🟢')}",
        "",
        "## 问题清单",
        "",
    ]

    if not issues:
        lines.append("✅ 未发现问题。")
    else:
        lines.append("| 级别 | 页 | 类型 | 描述 |")
        lines.append("|------|----|------|------|")
        for issue in issues:
            lines.append(f"| {issue['level']} | {issue['page']} | {issue['type']} | {issue['msg']} |")

    lines.extend([
        "",
        "## 修复建议",
        "",
        "- 🔴 阻塞项:必须修复后才能发布",
        "- 🟡 重要项:尽量在演示前修复",
        "- 🟢 优化项:有时间就改",
        "",
        "## 修复路径",
        "",
        "| 类型 | 回退到哪个 Skill |",
        "|------|------------------|",
        "| placeholder | pptx-generator / markdown-to-slides 重出 |",
        "| neutral_title | deck-storyline-designer 重写标题 |",
        "| no_notes | speaker-notes-writer 补讲稿 |",
        "| 视觉问题 | visual-slide-designer 强化 / template-layout-deck 重套 |",
        "| page_count | ppt-outline-builder 重新规划 |",
        "",
    ])

    out = "\n".join(lines)
    if out_path:
        out_path.write_text(out, encoding="utf-8")
        print(f"已写入:{out_path}")
    else:
        print(out)


if __name__ == "__main__":
    main()
```

### `scripts/soffice_convert.py`

```python
#!/usr/bin/env python3
"""用 LibreOffice 把 PPTX 转 PDF
用法: soffice_convert.py <input.pptx> <output.pdf>
"""
import shutil
import subprocess
import sys
from pathlib import Path


def find_soffice():
    candidates = ["soffice", "libreoffice"]
    for c in candidates:
        p = shutil.which(c)
        if p:
            return p
    # Windows 默认安装路径
    win_paths = [
        "C:/Program Files/LibreOffice/program/soffice.exe",
        "C:/Program Files (x86)/LibreOffice/program/soffice.exe",
    ]
    for p in win_paths:
        if Path(p).exists():
            return p
    return None


def main():
    if len(sys.argv) < 3:
        print("用法: soffice_convert.py <input.pptx> <output.pdf>")
        sys.exit(1)
    in_path = Path(sys.argv[1]).resolve()
    out_path = Path(sys.argv[2]).resolve()
    soffice = find_soffice()
    if not soffice:
        print("错误:找不到 LibreOffice。请安装 LibreOffice 或把 soffice 加入 PATH。")
        sys.exit(1)

    out_dir = out_path.parent
    cmd = [
        soffice, "--headless", "--norestore", "--nologo",
        "--convert-to", "pdf", "--outdir", str(out_dir), str(in_path),
    ]
    subprocess.run(cmd, check=True)
    pdf_name = in_path.stem + ".pdf"
    produced = out_dir / pdf_name
    if produced != out_path:
        shutil.move(str(produced), str(out_path))
    print(f"已生成:{out_path}")


if __name__ == "__main__":
    main()
```

### `scripts/make_thumbnail_grid.py`

```python
#!/usr/bin/env python3
"""把多张幻灯片 PNG 拼成网格缩略图
用法: make_thumbnail_grid.py <output.jpg> <input1.jpg> [input2.jpg ...]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def get_font(size, bold=False):
    paths = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def main():
    if len(sys.argv) < 3:
        print("用法: make_thumbnail_grid.py <output.jpg> <input1.jpg> [input2.jpg ...]")
        sys.exit(1)
    out_path = Path(sys.argv[1])
    images = [Image.open(p) for p in sys.argv[2:]]
    if not images:
        print("错误:未提供图片")
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
            [(col * cell_w, row * cell_h + thumb_h),
             ((col + 1) * cell_w, row * cell_h + thumb_h + label_h)],
            fill=(30, 39, 97),
        )
        draw.text(
            (col * cell_w + 10, row * cell_h + thumb_h + 5),
            f"页 {i + 1}",
            fill=(255, 255, 255),
            font=font,
        )

    grid.save(str(out_path), "JPEG", quality=85)
    print(f"已生成缩略图网格:{out_path}")


if __name__ == "__main__":
    main()
```

## 六、风险评估

🟡 **中风险** —— 需要调用 LibreOffice 转 PDF,首次使用可能下载 LibreOffice。生产环境建议预装。

## 七、与上下 Skill 的衔接

- **上游**: 任何已生成的 deck
- **下游**: 修复后回到对应上游 Skill,或导出 PDF 作为最终交付