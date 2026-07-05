---
name: deck-storyline-designer
description: "故事线设计器——把 PPT 从'页面堆砌'升级为'起承转合的演示旅程',让观众读完所有标题就能理解整套汇报逻辑。每页标题自带结论。输入 outline.md,输出 storyline.md。触发词:故事线、storyline、叙事弧、起承转合、deck 逻辑、PPT 叙事。"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ppt, storyline, narrative, deck, productivity]
    related_skills: [ppt-workflow-orchestrator, ppt-outline-builder, markdown-to-slides]
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



# 故事线设计器 (deck-storyline-designer)

> "演示不是页面的堆砌,而是一段有起承转合的旅程。"

## 一、目标

把上一环节生成的 `outline.md`(段落骨架),转化为带叙事张力的 `storyline.md`。观众读完所有标题,就能理解整套汇报的逻辑——而不是看到第 8 页还在猜第 1 页想说什么。

## 二、何时使用

- outline.md 已经生成,但各页之间缺乏过渡
- 用户希望增强演示的说服力、感染力
- 受众是被动接收方(领导、客户、外部听众),需要"被说服"
- 演示要在 5-15 分钟内完成,叙事效率就是生命

## 三、五种叙事弧模板

### 弧 1: 问题-洞察-方案(默认)

适合:决策汇报、季度复盘、项目评审

```
Hook(开场钩子)→ Why now(为何此刻)→ What we found(发现)→ What we propose(方案)→ What we need(资源/批准)
```

### 弧 2: 现状-愿景-路径

适合:战略汇报、年度规划、变革管理

```
Where we are(现状)→ Where we want to be(愿景)→ Why the gap(差距)→ How to bridge(路径)→ First 90 days(头 90 天)
```

### 弧 3: 反共识-证据-新视角

适合:技术分享、观点输出、说服型报告

```
Common belief(共识)→ Why it's wrong(为何错)→ Evidence(证据)→ New model(新模型)→ Implications(含义)
```

### 弧 4: 时间线-里程碑

适合:项目复盘、阶段汇报、年度回顾

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → What's next
```

### 弧 5: 案例-方法-复用

适合:最佳实践分享、内部分享、培训材料

```
Specific case(具体案例)→ Why it worked(为何有效)→ Distilled method(方法提炼)→ How to apply(如何复用)→ Caveats(注意事项)
```

## 四、操作规程

### Step 1: 读取 outline.md

提取每页的段落、标题、要点、证据。

### Step 2: 选择叙事弧

根据演示场景选择上述 5 种之一,或在 AI 提示下生成混合弧。

### Step 3: 改写每页标题

**核心原则:标题自带结论。**

❌ 差标题(中性描述):"项目进度"、"技术方案"、"用户反馈"
✅ 好标题(自带结论):"项目进度达 80%,但资源缺口仍达 30%"、"采用 X 方案可降低 40% 成本"、"75% 用户认为响应速度是核心痛点"

将所有页面标题按此原则重写。

### Step 4: 设计过渡

每页之间需要一个**过渡句**(transition hook),告诉观众"我们从这一页跳到下一页的理由"。

| 过渡类型 | 用途 | 示例 |
|----------|------|------|
| 因果型 | "因为 X,所以 Y" | "既然目标是降本 30%,那么下一步就是…" |
| 转折型 | 翻到新视角 | "然而,数据揭示了另一个故事…" |
| 放大型 | 从细节到整体 | "把视角拉远,我们看到…" |
| 收束型 | 从发散到聚焦 | "以上三点归结为一个判断…" |
| 钩子型 | 引发好奇 | "但有一个关键变量我们还没讨论…" |

### Step 5: 设计开场钩子

第 1 页之后、第 2 页(背景/现状)之前,需要一个 **hook**(15-30 秒抓住注意力):

- 一个反直觉的数据("95% 的 X,其实都没有 Y")
- 一个场景化问题("想象一下,你每天花 2 小时做这件事")
- 一个对比("同样是 Q3,A 团队做到 80%,B 团队只有 30%,差异在哪?")
- 一个引用("我们 CEO 上个月说了一句让我睡不着的话…")

### Step 6: 设计结尾行动召唤(CTA)

最后一页之前,需要明确**行动召唤**(Call-to-Action):

- "批准预算 120 万,在 Q4 前完成 X"
- "本周内确认两位候选人选"
- "下周再次评审时,会带上完整 ROI 测算"

### Step 7: 输出 storyline.md

```markdown
# <主题> — 故事线设计

> 叙事弧:<弧 1/2/3/4/5>
> 一句话总结:<一句话说清整套汇报要证明什么>

---

## 叙事弧概览

<Hook(15-30s)>
    ↓
<背景 1-2 页>
    ↓
<核心论证 / 转折>
    ↓
<方案 / 证据 / 洞察>
    ↓
<行动召唤>

---

## 逐页故事线

### 页 1: 封面
- **标题**: <主题>
- **演讲者开场**: "<一句话引入主题>"

### 页 2: Hook(钩子页)
- **标题**: <自带的反直觉/对比/问题>
- **演讲者**: "<完整 15-30s 钩子稿>"
- **过渡到下一页**: "<为什么下一张幻灯片从这里开始>"

### 页 3: <背景-1>
- **标题(自带结论)**: <...>
- **要点**:
  - <要点 1>
  - <要点 2>
- **视觉建议**: <图表/对比/数字>
- **过渡句**: "<...>"

(更多页...)

### 页 N: CTA 行动召唤
- **标题**: <明确的可执行行动>
- **要点**:
  - 谁: <责任人>
  - 何时: <deadline>
  - 做什么: <具体动作>
- **演讲者收束**: "<完整的收束稿>"

---

## 故事线自检清单

- [ ] 每页标题都自带结论
- [ ] Hook 能在 30 秒内抓住注意力
- [ ] 任意 5 张连续页标题连读,能听懂讲什么
- [ ] 至少 3 处过渡句设计
- [ ] CTA 明确、可执行、有截止时间
- [ ] 整体时长符合场景(决策汇报通常 10-15 分钟)
```

## 五、配套脚本

### `scripts/build_storyline.py`

读取 outline.md,辅助生成 storyline.md 骨架(含 Hook、过渡句占位、CTA 占位)。

```python
#!/usr/bin/env python3
"""
故事线骨架生成器:读 outline.md,生成 storyline.md 占位骨架,
便于 AI/作者进一步填充叙事弧、Hook、过渡句、CTA。
"""
import re
import sys
from datetime import datetime
from pathlib import Path


ARC_OPTIONS = {
    "1": "问题-洞察-方案(决策汇报/季度复盘)",
    "2": "现状-愿景-路径(战略/规划/变革)",
    "3": "反共识-证据-新视角(技术分享/说服)",
    "4": "时间线-里程碑(项目复盘/年度回顾)",
    "5": "案例-方法-复用(最佳实践/培训)",
}


def parse_outline(text):
    """简易解析 outline.md,抽取页 N: <标题>"""
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
            lines.extend([
                f"### 页 {page_num}: 封面",
                f"- **标题**: {title}",
                f"- **演讲者开场**: \"<一句话引入主题,说明为何此刻讲>\"",
                "",
            ])
        elif i == 1:
            # 第二页通常是 Hook
            lines.extend([
                f"### 页 {page_num}: Hook(钩子页)",
                f"- **标题(自带结论)**: <改写:反直觉数据/对比/问题>",
                f"- **演讲者**: \"<完整 15-30s 钩子稿>\"",
                f"- **过渡到下一页**: \"<为什么下一张幻灯片从这里开始>\"",
                "",
            ])
        elif page_num == len(pages):
            # 末页 CTA
            lines.extend([
                f"### 页 {page_num}: CTA 行动召唤",
                f"- **标题**: <明确可执行的行动>",
                f"- **要点**:",
                f"  - **谁**: <责任人>",
                f"  - **何时**: <deadline>",
                f"  - **做什么**: <具体动作>",
                f"- **演讲者收束**: \"<完整的收束稿,呼应 Hook>\"",
                "",
            ])
        else:
            lines.extend([
                f"### 页 {page_num}: {title}",
                f"- **标题(自带结论)**: <改写,把中性描述换成带数字/方向的判断>",
                f"- **要点**:",
                f"  - <要点 1>",
                f"  - <要点 2>",
                f"- **视觉建议**: <图表/对比/数字/案例>",
                f"- **过渡到下一页**: \"<因果型/转折型/放大型/收束型/钩子型>\"",
                "",
            ])

    lines.extend([
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
    ])
    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print("用法: build_storyline.py <outline.md> <arc> [output.md]")
        print("arc 取值:1=问题-洞察-方案 2=现状-愿景-路径 3=反共识-证据-新视角 4=时间线-里程碑 5=案例-方法-复用")
        sys.exit(1)
    outline_path = Path(sys.argv[1])
    arc = sys.argv[2]
    out_path = Path(sys.argv[3]) if len(sys.argv) >= 4 else None

    text = outline_path.read_text(encoding="utf-8")
    # 提取主题(从首个一级标题)
    m = re.search(r"^#\s+(.+?)\s+—", text, re.MULTILINE)
    theme = m.group(1) if m else "未命名演示"

    # 提取受众
    a = re.search(r"受众:(\S+)", text)
    audience = a.group(1) if a else "通用受众"

    pages = parse_outline(text)
    if not pages:
        print("错误:未在 outline.md 中找到 ### 页 N: ... 行")
        sys.exit(1)

    out = make_storyline(theme, arc, pages, audience)
    if out_path:
        out_path.write_text(out, encoding="utf-8")
        print(f"已写入:{out_path}")
    else:
        print(out)


if __name__ == "__main__":
    main()
```

## 六、风险评估

🟢 **低风险** —— 主要输出结构化文本,无外部依赖,不执行脚本/网络。

## 七、与上下 Skill 的衔接

- **上游**: `ppt-outline-builder` 输出 `outline.md`
- **下游**: `markdown-to-slides` 接收 `storyline.md`,转化为可直接生成幻灯片的源文件