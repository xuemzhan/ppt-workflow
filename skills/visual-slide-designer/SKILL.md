---
name: visual-slide-designer
description: "视觉页设计器——把普通文字页升级为视觉强页(封面、金句、方法论、流程图)。单文件 HTML + 内联 CSS/JS,固定 1920x1080 舞台,导出 PNG 后插入 PPTX。触发词:可视化页面、金句页、封面设计、PPT 视觉强化、visual slide、screenshot slide。"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ppt, visual, html, css, screenshot, cover, hero, deck]
    related_skills: [ppt-workflow-orchestrator, pptx-generator, deck-review-publisher]
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



# 视觉页设计器 (visual-slide-designer)

> "把普通文字页变成视觉页——封面、金句、方法论、流程图。"

## 一、目标

为 PPT 中的**关键页**(封面、章节封面、金句页、流程图页)生成高视觉冲击的单页 HTML,固定 1920×1080 舞台,然后用 Playwright/Chromium 截图,作为图片插入 PPTX。

## 二、何时使用

- 封面页需要"看上去不像 AI 生成的"
- 章节过渡页需要一张"视觉锚"
- 一句话金句需要大字号、深背景
- 复杂流程/架构图用 PPT 形状很难画

## 三、支持的可视化模板

### 模板 1: hero_cover(强冲击封面)

```html
<div class="hero">
  <div class="hero-bg-grid"></div>
  <div class="hero-content">
    <div class="hero-eyebrow">2026 年中评审</div>
    <h1 class="hero-title">智能办公<br>从工具到生产力</h1>
    <div class="hero-sub">开悟个体增智办公套件 V1.0</div>
    <div class="hero-author">汇报人 · 张三</div>
  </div>
</div>
```

### 模板 2: chapter_divider(章节封面)

```html
<div class="chapter">
  <div class="chapter-number">02</div>
  <div class="chapter-title">洞察</div>
  <div class="chapter-sub">我们发现了什么</div>
</div>
```

### 模板 3: big_quote(大金句)

```html
<div class="quote">
  <div class="quote-mark">"</div>
  <p class="quote-text">AI 不是替代你<br>而是放大你</p>
  <div class="quote-author">—— 项目愿景</div>
</div>
```

### 模板 4: methodology(三段式方法论)

```html
<div class="method">
  <h2>方法论:三步走</h2>
  <div class="method-steps">
    <div class="method-step">
      <div class="step-num">01</div>
      <h3>发现</h3>
      <p>梳理 12 个核心场景</p>
    </div>
    <div class="method-step">
      <div class="step-num">02</div>
      <h3>设计</h3>
      <p>搭结构 / 选模板 / 做视觉</p>
    </div>
    <div class="method-step">
      <div class="step-num">03</div>
      <h3>验证</h3>
      <p>小范围试点 / 收反馈</p>
    </div>
  </div>
</div>
```

### 模板 5: flow_diagram(流程图)

```html
<div class="flow">
  <h2>用户旅程</h2>
  <div class="flow-row">
    <div class="flow-node">需求输入</div>
    <div class="flow-arrow">→</div>
    <div class="flow-node highlight">AI 加工</div>
    <div class="flow-arrow">→</div>
    <div class="flow-node">结构化输出</div>
  </div>
</div>
```

## 四、操作规程

### Step 1: 选择模板

从上述 5 种中选一种,或基于 JSON 配置自定义。

### Step 2: 生成 HTML

调用 `scripts/build_visual.py`,传入模板名 + 内容 → 输出 `visual.html`。

### Step 3: 截图为 PNG

使用 Playwright 截图 1920×1080:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    page.goto(f"file://{html_path}")
    page.screenshot(path=png_path, full_page=False)
    browser.close()
```

如无 Playwright,可用 Chrome/Edge headless:

```bash
chrome --headless --disable-gpu --no-sandbox --window-size=1920,1080 --screenshot=output.png file://input.html
msedge --headless --disable-gpu --no-sandbox --window-size=1920,1080 --screenshot=output.png file://input.html
```

### Step 4: 插入 PPTX

```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation("deck.pptx")
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.shapes.add_picture("visual.png", Inches(0), Inches(0), width=prs.slide_width, height=prs.slide_height)
prs.save("deck.pptx")
```

## 五、配套脚本

### `scripts/build_visual.py`

```python
#!/usr/bin/env python3
"""
视觉页 HTML 生成器:5 种模板 → 单文件 HTML(1920x1080)
用法:
    python build_visual.py <template> <content.json> <output.html>

template: hero_cover | chapter_divider | big_quote | methodology | flow_diagram
"""
import json
import sys
from pathlib import Path


BASE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  width: 1920px; height: 1080px;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  overflow: hidden;
}
"""


HERO_COVER_HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{css}
.hero {
  width: 1920px; height: 1080px;
  background: linear-gradient(135deg, #1E2761 0%, #065A82 100%);
  position: relative;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
}
.hero-bg-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px);
  background-size: 60px 60px;
}
.hero-content { position: relative; text-align: center; padding: 0 100px; }
.hero-eyebrow {
  display: inline-block; padding: 8px 24px;
  border: 1px solid #F96167; color: #F96167;
  font-size: 28px; letter-spacing: 6px;
  margin-bottom: 40px;
}
.hero-title {
  font-size: 140px; font-weight: 900; line-height: 1.1;
  margin-bottom: 40px;
  text-shadow: 0 4px 30px rgba(0,0,0,.3);
}
.hero-sub {
  font-size: 44px; color: #CADCFC; margin-bottom: 80px;
}
.hero-author { font-size: 28px; color: #CADCFC; opacity: .8; }
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


CHAPTER_HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{css}
.chapter {
  width: 1920px; height: 1080px;
  background: linear-gradient(135deg, #1E2761 0%, #0a0f2c 100%);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: #fff; position: relative;
}
.chapter-number {
  font-size: 320px; font-weight: 900; color: #F96167;
  text-shadow: 0 0 80px rgba(249,97,103,.4);
  line-height: 1;
}
.chapter-title {
  font-size: 100px; font-weight: 700; margin-top: 40px;
  letter-spacing: 20px;
}
.chapter-sub {
  font-size: 36px; color: #CADCFC; margin-top: 40px;
  letter-spacing: 8px;
}
</style></head><body>
<div class="chapter">
  <div class="chapter-number">{number}</div>
  <div class="chapter-title">{title}</div>
  <div class="chapter-sub">{sub}</div>
</div>
</body></html>
"""


QUOTE_HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{css}
.quote {
  width: 1920px; height: 1080px;
  background: linear-gradient(135deg, #1E2761 0%, #2C5F2D 100%);
  display: flex; align-items: center; justify-content: center;
  color: #fff; position: relative; padding: 0 200px;
}
.quote-mark {
  position: absolute; top: 120px; left: 200px;
  font-size: 400px; color: #F96167; opacity: .3;
  font-family: Georgia, serif; line-height: 1;
}
.quote-text {
  font-size: 96px; font-weight: 700; line-height: 1.4;
  text-align: center; position: relative;
}
.quote-author {
  position: absolute; bottom: 200px;
  font-size: 32px; color: #CADCFC; letter-spacing: 4px;
}
</style></head><body>
<div class="quote">
  <div class="quote-mark">"</div>
  <p class="quote-text">{text}</p>
  <div class="quote-author">{author}</div>
</div>
</body></html>
"""


METHODOLOGY_HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{css}
.method {
  width: 1920px; height: 1080px;
  background: #F5F5F5;
  padding: 120px 160px;
}
.method h2 {
  font-size: 80px; color: #1E2761; margin-bottom: 100px;
  text-align: center; font-weight: 800;
}
.method-steps { display: flex; gap: 80px; }
.method-step {
  flex: 1; background: #fff;
  padding: 60px 50px; border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0,0,0,.08);
  border-top: 6px solid #F96167;
}
.step-num {
  font-size: 80px; font-weight: 900; color: #F96167;
  line-height: 1; margin-bottom: 30px;
}
.method-step h3 {
  font-size: 48px; color: #1E2761; margin-bottom: 20px;
}
.method-step p {
  font-size: 28px; color: #36454F; line-height: 1.6;
}
</style></head><body>
<div class="method">
  <h2>{title}</h2>
  <div class="method-steps">
    {steps_html}
  </div>
</div>
</body></html>
"""


FLOW_HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{css}
.flow {
  width: 1920px; height: 1080px;
  background: #F5F5F5;
  padding: 100px 120px;
}
.flow h2 {
  font-size: 72px; color: #1E2761; text-align: center; margin-bottom: 100px;
  font-weight: 800;
}
.flow-row {
  display: flex; align-items: center; justify-content: center; gap: 30px;
  flex-wrap: wrap;
}
.flow-node {
  padding: 40px 60px; background: #1E2761; color: #fff;
  font-size: 36px; border-radius: 12px; font-weight: 600;
  box-shadow: 0 4px 16px rgba(0,0,0,.1);
}
.flow-node.highlight {
  background: #F96167; transform: scale(1.1);
}
.flow-arrow {
  font-size: 60px; color: #1E2761; font-weight: 900;
}
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
                <div class="step-num">{i+1:02d}</div>
                <h3>{s.get('title','')}</h3>
                <p>{s.get('desc','')}</p>
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
                f'<div class="flow-node{" highlight" if n.get("highlight") else ""}">{n.get("label","")}</div>'
            )
            if i < len(nodes) - 1:
                parts.append('<div class="flow-arrow">→</div>')
        return FLOW_HTML.format(
            css=BASE_CSS,
            title=content.get("title", ""),
            nodes_html="\n".join(parts),
        )
    raise ValueError(f"未知模板:{template}")


def main():
    if len(sys.argv) < 4:
        print("用法: build_visual.py <template> <content.json> <output.html>")
        print("template 取值:hero_cover / chapter_divider / big_quote / methodology / flow_diagram")
        sys.exit(1)
    template = sys.argv[1]
    content = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    out_path = Path(sys.argv[3])
    out_path.write_text(build(template, content), encoding="utf-8")
    print(f"已生成 HTML:{out_path}")


if __name__ == "__main__":
    main()
```

### `scripts/html_to_png.py`

```python
#!/usr/bin/env python3
"""把 1920x1080 HTML 截图为 PNG

用法:
    python html_to_png.py <input.html> <output.png>

依赖二选一:
    1. playwright: pip install playwright && playwright install chromium
    2. 系统 Chrome/Edge + headless 模式
"""
import shutil
import subprocess
import sys
from pathlib import Path


def screenshot_with_playwright(html_path, png_path):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(f"file://{html_path.resolve()}")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(png_path), full_page=False)
        browser.close()
    return True


def screenshot_with_chrome(html_path, png_path):
    candidates = [
        "chrome", "google-chrome", "chromium",
        "msedge", "Microsoft\\Edge\\Application\\msedge.exe",
    ]
    for c in candidates:
        path = shutil.which(c)
        if path:
            cmd = [
                path, "--headless=new", "--disable-gpu", "--no-sandbox",
                f"--window-size=1920,1080", f"--screenshot={png_path}",
                f"file://{html_path.resolve()}",
            ]
            subprocess.run(cmd, check=False)
            return png_path.exists()
    return False


def main():
    if len(sys.argv) < 3:
        print("用法: html_to_png.py <input.html> <output.png>")
        sys.exit(1)
    html_path = Path(sys.argv[1])
    png_path = Path(sys.argv[2])

    if screenshot_with_playwright(html_path, png_path):
        print(f"已截图(playwright):{png_path}")
        return
    if screenshot_with_chrome(html_path, png_path):
        print(f"已截图(chrome):{png_path}")
        return

    print("错误:既未安装 playwright,也找不到 Chrome/Edge。请 pip install playwright 后再试。")
    sys.exit(1)


if __name__ == "__main__":
    main()
```

## 六、风险评估

🟡 **中风险** —— Playwright/Chromium 会下载并执行 Chromium 二进制,首次使用需要联网。如果 Vercel 等平台署的内容会被外部用户访问,需要小心内部信息泄露。

## 七、与上下 Skill 的衔接

- **上游**: `ppt-outline-builder` 决定哪些页是"视觉锚"页
- **下游**:截图 PNG 插入到 `pptx-generator` 生成的 deck 中,作为某一页的背景图