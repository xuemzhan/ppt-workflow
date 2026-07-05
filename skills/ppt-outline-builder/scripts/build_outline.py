#!/usr/bin/env python3
"""PPT 大纲生成器 - 辅助生成符合 CCISEA 框架的 outline.md

用法:
    python build_outline.py <slides.json> [output.md]

slides.json 格式:
{
  "theme": "主题",
  "audience": "受众",
  "scenario": "场景",
  "slides": [
    {
      "section": "context|challenge|insight|solution|evidence|action",
      "title": "标题(自带结论)",
      "points": ["要点1", "要点2"],
      "evidence": "数据/案例/对比/引文/图表",
      "chart_needed": true,
      "chart_type": "柱状图",
      "viz_type": "流程图/金句页/时间线/对比栏/大数字/无",
      "source": "来源文件名",
      "minutes": 1
    }
  ]
}
"""

# IMPORTANT: path setup must come BEFORE any skills.* imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from skills.shared.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


CCISEA_TEMPLATE = {
    "context": {"label": "背景", "min_pages": 1, "max_pages": 2},
    "challenge": {"label": "问题", "min_pages": 1, "max_pages": 2},
    "insight": {"label": "洞察", "min_pages": 2, "max_pages": 3},
    "solution": {"label": "方案", "min_pages": 2, "max_pages": 4},
    "evidence": {"label": "证据", "min_pages": 2, "max_pages": 3},
    "action": {"label": "行动", "min_pages": 1, "max_pages": 2},
}


def make_outline(theme, audience, scenario, slides):
    total = len(slides) + 2
    lines = [
        f"# {theme} - 演示大纲",
        "",
        f"> 受众:{audience}",
        f"> 场景:{scenario}",
        f"> 生成时间:{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 总页数:{total} (含封面/封底)",
        "",
        "---",
        "",
        "## 一、整体结构(CCISEA)",
        "",
        "| 段落 | 页码范围 | 主要论证 |",
        "|------|---------|----------|",
    ]

    by_section = {}
    for i, s in enumerate(slides, start=2):
        by_section.setdefault(s["section"], []).append((i, s))

    for sec_key, sec_info in CCISEA_TEMPLATE.items():
        if sec_key in by_section:
            page_nums = [str(p[0]) for p in by_section[sec_key]]
            titles = "; ".join(p[1]["title"][:30] for p in by_section[sec_key])
            lines.append(f"| {sec_info['label']} | {', '.join(page_nums)} | {titles} |")

    lines.extend(["", "---", "", "## 二、逐页大纲", ""])
    lines.append("### 页 1: 封面")
    lines.append("- 段落: 封面")
    lines.append(f"- 标题: {theme}")
    lines.append(f"- 副标题: {audience} · {scenario}")
    lines.append("- 时长: 0.5")
    lines.append("")

    for i, s in enumerate(slides, start=2):
        sec_label = CCISEA_TEMPLATE[s["section"]]["label"]
        lines.append(f"### 页 {i}: {s['title']}")
        lines.append(f"- 段落: {sec_label}")
        lines.append(f"- 标题结论: {s['title']}")
        lines.append("- 核心要点:")
        for p in s.get("points", []):
            lines.append(f"  - {p}")
        lines.append(f"- 证据类型: {s.get('evidence', '文字')}")
        if s.get("chart_needed"):
            lines.append(f"- 图表需求: 是, {s.get('chart_type', '')}")
        else:
            lines.append("- 图表需求: 否")
        lines.append(f"- 可视化需求: {s.get('viz_type', '无')}")
        lines.append(f"- 来源: {s.get('source', '-')}")
        lines.append(f"- 预计时长: {s.get('minutes', 1)} 分钟")
        lines.append("")

    cover_end = len(slides) + 2
    lines.append(f"### 页 {cover_end}: 封底/讨论")
    lines.append("- 段落: 行动")
    lines.append("- 标题结论: 谢谢讨论 - 下一步行动待确认")
    lines.append("- 核心要点:")
    lines.append("  - 收集反馈")
    lines.append("  - 列出待办责任人")
    lines.append("  - 约定下次同步时间")
    lines.append("- 时长: 2")
    lines.append("")

    lines.extend(["---", "", "## 三、自检清单", ""])
    checks = [
        (
            "每页标题都是结论",
            all(s.get("title", "").strip() and len(s["title"]) > 4 for s in slides),
        ),
        ("总页数在 8-16 之间", 6 <= len(slides) <= 14),
        (
            "每段(背景/问题/...)至少有一页",
            all(k in by_section for k in CCISEA_TEMPLATE),
        ),
        ("至少 2 页有图表需求", sum(1 for s in slides if s.get("chart_needed")) >= 2),
        ("行动页存在", "action" in by_section),
    ]
    for label, ok in checks:
        lines.append(f"- [{'x' if ok else ' '}] {label}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 PPT 大纲")
    parser.add_argument("input", help="输入 slides.json 文件路径")
    parser.add_argument("output", nargs="?", help="输出 markdown 文件路径")
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    theme = data.get("theme", "未命名演示")
    audience = data.get("audience", "通用受众")
    scenario = data.get("scenario", "通用场景")
    slides = data["slides"]
    out = make_outline(theme, audience, scenario, slides)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        logger.info("已写入: %s", args.output)
    else:
        print(out)


if __name__ == "__main__":
    main()
