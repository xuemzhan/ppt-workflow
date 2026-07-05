#!/usr/bin/env python3
"""故事线骨架生成器:读 outline.md,生成 storyline.md 占位骨架,
便于 AI/作者进一步填充叙事弧、Hook、过渡句、CTA。

用法:
    python build_storyline.py <outline.md> <arc> [output.md]

arc 取值:
    1 = 问题-洞察-方案
    2 = 现状-愿景-路径
    3 = 反共识-证据-新视角
    4 = 时间线-里程碑
    5 = 案例-方法-复用
"""

# IMPORTANT: path setup must come BEFORE any skills.* imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

from skills.shared.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


ARC_OPTIONS = {
    "1": "问题-洞察-方案(决策汇报/季度复盘)",
    "2": "现状-愿景-路径(战略/规划/变革)",
    "3": "反共识-证据-新视角(技术分享/说服)",
    "4": "时间线-里程碑(项目复盘/年度回顾)",
    "5": "案例-方法-复用(最佳实践/培训)",
}


def parse_outline(text):
    pages = []
    for m in re.finditer(r"^###\s+页\s+(\d+):\s+(.+)$", text, re.MULTILINE):
        pages.append({"page": int(m.group(1)), "title": m.group(2).strip()})
    return pages


def make_storyline(theme, arc, pages, audience="通用受众"):
    lines = [
        f"# {theme} — 故事线设计",
        "",
        f"> 叙事弧:{ARC_OPTIONS.get(arc, arc)}",
        f"> 受众:{audience}",
        f"> 生成时间:{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 总页数:{len(pages)}",
        "",
        "---",
        "",
        "## 一、叙事弧概览",
        "",
        "<Hook(15-30s 钩子)>",
        "    ↓",
        "<背景 1-2 页>",
        "    ↓",
        "<核心论证 / 转折>",
        "    ↓",
        "<方案 / 证据 / 洞察>",
        "    ↓",
        "<行动召唤 CTA>",
        "",
        "---",
        "",
        "## 二、逐页故事线",
        "",
    ]

    for i, p in enumerate(pages):
        page_num = p["page"]
        title = p["title"]
        if page_num == 1:
            lines.extend(
                [
                    f"### 页 {page_num}: 封面",
                    f"- **标题**: {title}",
                    '- **演讲者开场**: "<一句话引入主题,说明为何此刻讲>"',
                    "",
                ]
            )
        elif i == 1:
            lines.extend(
                [
                    f"### 页 {page_num}: Hook(钩子页)",
                    "- **标题(自带结论)**: <改写:反直觉数据/对比/问题>",
                    '- **演讲者**: "<完整 15-30s 钩子稿>"',
                    '- **过渡到下一页**: "<为什么下一张幻灯片从这里开始>"',
                    "",
                ]
            )
        elif page_num == len(pages):
            lines.extend(
                [
                    f"### 页 {page_num}: CTA 行动召唤",
                    "- **标题**: <明确可执行的行动>",
                    "- **要点**:",
                    "  - **谁**: <责任人>",
                    "  - **何时**: <deadline>",
                    "  - **做什么**: <具体动作>",
                    '- **演讲者收束**: "<完整的收束稿,呼应 Hook>"',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    f"### 页 {page_num}: {title}",
                    "- **标题(自带结论)**: <改写,把中性描述换成带数字/方向的判断>",
                    "- **要点**:",
                    "  - <要点 1>",
                    "  - <要点 2>",
                    "- **视觉建议**: <图表/对比/数字/案例>",
                    '- **过渡到下一页**: "<因果型/转折型/放大型/收束型/钩子型>"',
                    "",
                ]
            )

    lines.extend(
        [
            "---",
            "",
            "## 三、故事线自检清单",
            "",
            "- [ ] 每页标题都自带结论(中性描述改成带数字/方向的判断)",
            "- [ ] Hook 能在 30 秒内抓住注意力",
            "- [ ] 任意 5 张连续页标题连读,能听懂讲什么",
            "- [ ] 至少 3 处过渡句设计",
            "- [ ] CTA 明确、可执行、有截止时间",
            "- [ ] 整体时长符合场景",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="生成故事线骨架")
    parser.add_argument("outline", help="输入 outline.md 文件路径")
    parser.add_argument(
        "arc",
        choices=["1", "2", "3", "4", "5"],
        help="叙事弧类型: 1=问题-洞察-方案 2=现状-愿景-路径 3=反共识-证据-新视角 4=时间线-里程碑 5=案例-方法-复用",
    )
    parser.add_argument("output", nargs="?", help="输出 markdown 文件路径")
    args = parser.parse_args()
    outline_path = Path(args.outline)
    arc = args.arc
    out_path = Path(args.output) if args.output else None

    text = outline_path.read_text(encoding="utf-8-sig")
    m = re.search(r"^#\s+(.+?)\s+—", text, re.MULTILINE)
    theme = m.group(1) if m else "未命名演示"

    a = re.search(r"受众:(\S+)", text)
    audience = a.group(1) if a else "通用受众"

    pages = parse_outline(text)
    if not pages:
        logger.error("未在 outline.md 中找到 ### 页 N: ... 行")
        sys.exit(1)

    out = make_storyline(theme, arc, pages, audience)
    if out_path:
        out_path.write_text(out, encoding="utf-8")
        logger.info("已写入: %s", out_path)
    else:
        print(out)


if __name__ == "__main__":
    main()
