#!/usr/bin/env python3
"""学术大纲生成器:按学术 PPT 标准结构生成 outline.md

用法: build_academic_outline.py <thesis|midterm|review> <title> [output.md]
"""

# IMPORTANT: path setup must come BEFORE any skills.* imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from skills.shared.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


TEMPLATES = {
    "thesis": {
        "name": "论文答辩(15 分钟)",
        "sections": [
            ("标题 + 核心论点", 1),
            ("背景与动机", 2),
            ("已有方法局限", 1),
            ("本文方法", 3),
            ("实验结果", 4),
            ("讨论与局限", 1),
            ("结论与未来工作", 1),
            ("Q&A", 1),
        ],
    },
    "midterm": {
        "name": "课题中期汇报(20 分钟)",
        "sections": [
            ("课题基本信息", 1),
            ("课题目标", 1),
            ("当前进展总览", 1),
            ("已完成工作", 2),
            ("进行中工作", 2),
            ("关键技术路线", 1),
            ("阶段性结论", 1),
            ("问题与对策", 1),
            ("下阶段计划", 1),
            ("Q&A", 1),
        ],
    },
    "review": {
        "name": "文献综述(30 分钟)",
        "sections": [
            ("主题与范围", 1),
            ("检索策略", 1),
            ("领域地图", 1),
            ("方法 A 综述", 3),
            ("方法 B 综述", 3),
            ("方法 C 综述", 3),
            ("横向对比", 1),
            ("研究 gap", 1),
            ("未来方向", 1),
            ("参考文献", 1),
        ],
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description="生成学术汇报大纲")
    parser.add_argument(
        "template", choices=["thesis", "midterm", "review"], help="模板类型"
    )
    parser.add_argument("title", help="汇报标题")
    parser.add_argument("output", nargs="?", help="输出 markdown 文件路径")
    args = parser.parse_args()
    template = args.template
    title = args.title
    out_path = Path(args.output) if args.output else None

    if template not in TEMPLATES:
        logger.error("未知模板: %s, 可选: %s", template, ",".join(TEMPLATES.keys()))
        sys.exit(1)

    tmpl = TEMPLATES[template]
    lines = [
        f"# {title} — 学术汇报大纲",
        "",
        f"> 模板:{tmpl['name']}",
        f"> 生成时间:{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 一、核心论点(一句话)",
        "",
        "> <请用一句话回答:如果观众只能记住一件事,那是什么?>",
        "",
        "---",
        "",
        "## 二、整体结构",
        "",
        "| 段落 | 页数范围 |",
        "|------|---------|",
    ]

    page = 1
    for sec_name, sec_pages in tmpl["sections"]:
        page_range = f"{page}-{page + sec_pages - 1}" if sec_pages > 1 else str(page)
        lines.append(f"| {sec_name} | {page_range} |")
        page += sec_pages

    lines.append("")
    lines.append(f"**总页数:{page - 1}**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 三、逐页大纲(每页一个洞察)")
    lines.append("")

    page = 1
    for sec_name, sec_pages in tmpl["sections"]:
        for i in range(sec_pages):
            suffix = " - " + str(i + 1) if sec_pages > 1 else ""
            lines.append(f"### 页 {page}: {sec_name}{suffix}")
            lines.append(f"- **段落**:{sec_name}")
            lines.append("- **标题(自带结论)**: <此页的核心发现/判断>")
            lines.append("- **核心要点**:")
            lines.append("  - <要点 1>")
            lines.append("- **图表/表格需求**: <是 / 否,若是,描述>")
            lines.append("- **引用**: [1] <来源>")
            lines.append("- **时长**: <分钟>")
            lines.append("")
            page += 1

    lines.extend(
        [
            "---",
            "",
            "## 四、参考文献清单",
            "",
            '[1] <作者> et al., "<标题>", <会议/期刊>, <年份>.',
            "[2] ...",
            "",
        ]
    )

    out = "\n".join(lines)
    if out_path:
        out_path.write_text(out, encoding="utf-8")
        logger.info("已写入: %s", out_path)
    else:
        print(out)


if __name__ == "__main__":
    main()
