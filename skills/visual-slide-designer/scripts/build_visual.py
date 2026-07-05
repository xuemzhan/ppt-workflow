#!/usr/bin/env python3
"""视觉页 HTML 生成器:5 种模板 → 单文件 HTML(1920x1080)

用法:
    python build_visual.py <template> <content.json> <output.html>

template 取值:hero_cover / chapter_divider / big_quote / methodology / flow_diagram
"""

# IMPORTANT: path setup must come BEFORE any skills.* imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import argparse
import json
import logging
import sys
from pathlib import Path

from skills.shared.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


BASE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  width: 1920px; height: 1080px;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  overflow: hidden;
}
"""


HERO_COVER_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{css}
.hero {{
  width: 1920px; height: 1080px;
  background: linear-gradient(135deg, #1E2761 0%, #065A82 100%);
  position: relative;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
}}
.hero-bg-grid {{
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px);
  background-size: 60px 60px;
}}
.hero-content {{ position: relative; text-align: center; padding: 0 100px; }}
.hero-eyebrow {{
  display: inline-block; padding: 8px 24px;
  border: 1px solid #F96167; color: #F96167;
  font-size: 28px; letter-spacing: 6px;
  margin-bottom: 40px;
}}
.hero-title {{
  font-size: 140px; font-weight: 900; line-height: 1.1;
  margin-bottom: 40px;
  text-shadow: 0 4px 30px rgba(0,0,0,.3);
}}
.hero-sub {{
  font-size: 44px; color: #CADCFC; margin-bottom: 80px;
}}
.hero-author {{ font-size: 28px; color: #CADCFC; opacity: .8; }}
</style></head><body>
<div class="hero">
  <div class="hero-bg-grid"></div>
  <div class="hero-content">
    <div class="hero-eyebrow">{eyebrow}</div>
    <h1 class="hero-title">{title}</h1>
    <div class="hero-sub">{sub}</div>
    <div class="hero-author">{author}</div>
  </div>
</div>
</body></html>
"""


CHAPTER_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{css}
.chapter {{
  width: 1920px; height: 1080px;
  background: linear-gradient(135deg, #1E2761 0%, #0a0f2c 100%);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: #fff; position: relative;
}}
.chapter-number {{
  font-size: 320px; font-weight: 900; color: #F96167;
  text-shadow: 0 0 80px rgba(249,97,103,.4);
  line-height: 1;
}}
.chapter-title {{
  font-size: 100px; font-weight: 700; margin-top: 40px;
  letter-spacing: 20px;
}}
.chapter-sub {{
  font-size: 36px; color: #CADCFC; margin-top: 40px;
  letter-spacing: 8px;
}}
</style></head><body>
<div class="chapter">
  <div class="chapter-number">{number}</div>
  <div class="chapter-title">{title}</div>
  <div class="chapter-sub">{sub}</div>
</div>
</body></html>
"""


QUOTE_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{css}
.quote {{
  width: 1920px; height: 1080px;
  background: linear-gradient(135deg, #1E2761 0%, #2C5F2D 100%);
  display: flex; align-items: center; justify-content: center;
  color: #fff; position: relative; padding: 0 200px;
}}
.quote-mark {{
  position: absolute; top: 120px; left: 200px;
  font-size: 400px; color: #F96167; opacity: .3;
  font-family: Georgia, serif; line-height: 1;
}}
.quote-text {{
  font-size: 96px; font-weight: 700; line-height: 1.4;
  text-align: center; position: relative;
}}
.quote-author {{
  position: absolute; bottom: 200px;
  font-size: 32px; color: #CADCFC; letter-spacing: 4px;
}}
</style></head><body>
<div class="quote">
  <div class="quote-mark">"</div>
  <p class="quote-text">{text}</p>
  <div class="quote-author">{author}</div>
</div>
</body></html>
"""


METHODOLOGY_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{css}
.method {{
  width: 1920px; height: 1080px;
  background: #F5F5F5;
  padding: 120px 160px;
}}
.method h2 {{
  font-size: 80px; color: #1E2761; margin-bottom: 100px;
  text-align: center; font-weight: 800;
}}
.method-steps {{ display: flex; gap: 80px; }}
.method-step {{
  flex: 1; background: #fff;
  padding: 60px 50px; border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0,0,0,.08);
  border-top: 6px solid #F96167;
}}
.step-num {{
  font-size: 80px; font-weight: 900; color: #F96167;
  line-height: 1; margin-bottom: 30px;
}}
.method-step h3 {{
  font-size: 48px; color: #1E2761; margin-bottom: 20px;
}}
.method-step p {{
  font-size: 28px; color: #36454F; line-height: 1.6;
}}
</style></head><body>
<div class="method">
  <h2>{title}</h2>
  <div class="method-steps">
    {steps_html}
  </div>
</div>
</body></html>
"""


FLOW_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{css}
.flow {{
  width: 1920px; height: 1080px;
  background: #F5F5F5;
  padding: 100px 120px;
}}
.flow h2 {{
  font-size: 72px; color: #1E2761; text-align: center; margin-bottom: 100px;
  font-weight: 800;
}}
.flow-row {{
  display: flex; align-items: center; justify-content: center; gap: 30px;
  flex-wrap: wrap;
}}
.flow-node {{
  padding: 40px 60px; background: #1E2761; color: #fff;
  font-size: 36px; border-radius: 12px; font-weight: 600;
  box-shadow: 0 4px 16px rgba(0,0,0,.1);
}}
.flow-node.highlight {{
  background: #F96167; transform: scale(1.1);
}}
.flow-arrow {{
  font-size: 60px; color: #1E2761; font-weight: 900;
}}
</style></head><body>
<div class="flow">
  <h2>{title}</h2>
  <div class="flow-row">
    {nodes_html}
  </div>
</div>
</body></html>
"""


def build(template, content):
    if template == "hero_cover":
        return HERO_COVER_HTML.format(
            css=BASE_CSS,
            eyebrow=content.get("eyebrow", ""),
            title=content.get("title", "").replace("\n", "<br>"),
            sub=content.get("sub", ""),
            author=content.get("author", ""),
        )
    if template == "chapter_divider":
        return CHAPTER_HTML.format(
            css=BASE_CSS,
            number=content.get("number", "00"),
            title=content.get("title", ""),
            sub=content.get("sub", ""),
        )
    if template == "big_quote":
        return QUOTE_HTML.format(
            css=BASE_CSS,
            text=content.get("text", "").replace("\n", "<br>"),
            author=content.get("author", ""),
        )
    if template == "methodology":
        steps_html = "\n".join(
            f"""<div class="method-step">
                <div class="step-num">{i + 1:02d}</div>
                <h3>{s.get("title", "")}</h3>
                <p>{s.get("desc", "")}</p>
            </div>"""
            for i, s in enumerate(content.get("steps", []))
        )
        return METHODOLOGY_HTML.format(
            css=BASE_CSS,
            title=content.get("title", ""),
            steps_html=steps_html,
        )
    if template == "flow_diagram":
        nodes = content.get("nodes", [])
        parts = []
        for i, n in enumerate(nodes):
            parts.append(
                f'<div class="flow-node{" highlight" if n.get("highlight") else ""}">{n.get("label", "")}</div>'
            )
            if i < len(nodes) - 1:
                parts.append('<div class="flow-arrow">→</div>')
        return FLOW_HTML.format(
            css=BASE_CSS,
            title=content.get("title", ""),
            nodes_html="\n".join(parts),
        )
    raise ValueError(f"未知模板:{template}")


def main() -> None:
    parser = argparse.ArgumentParser(description="生成视觉页 HTML")
    parser.add_argument(
        "template",
        choices=[
            "hero_cover",
            "chapter_divider",
            "big_quote",
            "methodology",
            "flow_diagram",
        ],
        help="模板类型",
    )
    parser.add_argument("content", help="内容 JSON 文件路径")
    parser.add_argument("output", help="输出 HTML 文件路径")
    args = parser.parse_args()
    content = json.loads(Path(args.content).read_text(encoding="utf-8-sig"))
    out_path = Path(args.output)
    out_path.write_text(build(args.template, content), encoding="utf-8")
    logger.info("已生成 HTML: %s", out_path)


if __name__ == "__main__":
    main()
