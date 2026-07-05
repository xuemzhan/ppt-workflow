---
name: ppt-outline-builder
description: "PPT 结构搭建器——把主题/资料拆解为'背景-问题-洞察-方案-证据-行动'的演示骨架,而不是急着做页。生成 outline.md。触发词:PPT 大纲、演示结构、deck outline、汇报骨架、ppt 框架、幻灯片大纲。"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ppt, outline, structure, deck, productivity]
    related_skills: [ppt-workflow-orchestrator, deck-storyline-designer, markdown-to-slides]
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



# PPT 结构搭建器 (ppt-outline-builder)

> "先搭结构,不急着做页。"

## 一、目标

把一个模糊的演示主题,拆成可执行的演示骨架。重点不是生成 PPT,而是明确:

- 演示分几页?
- 每页讲什么?
- 每页承担什么论证功能?
- 每页放什么证据?

输出 `outline.md`,作为后续 Skill 的统一起点。

## 二、何时使用

- 用户给了主题但还没想好结构
- 用户提供一堆原始资料,需要先归类、再分页
- 用户要做对外汇报、内部决策汇报、项目评审、季度复盘等正式场景
- 用户的需求是"先出个框架给我看看"

## 三、操作规程

### Step 1: 资料归集与阅读

读取 `input/` 目录下的全部文件(支持 .md / .txt / .docx / .pdf / .xlsx / .csv),逐文件提要点。

### Step 2: 确定演示骨架

按 **"背景-问题-洞察-方案-证据-行动"** (Context-Challenge-Insight-Solution-Evidence-Action,简称 CCISEA) 六段式搭建:

| 段落 | 功能 | 典型页数 |
|------|------|----------|
| 背景 (Context) | 建立共识,交代为何讲 | 1-2 页 |
| 问题 (Challenge) | 暴露矛盾,定义核心问题 | 1-2 页 |
| 洞察 (Insight) | 提供新的认识、判断 | 2-3 页 |
| 方案 (Solution) | 给出建议、对策 | 2-4 页 |
| 证据 (Evidence) | 数据、案例、对比 | 2-3 页 |
| 行动 (Action) | 谁、什么时候、做什么 | 1-2 页 |

加上封面/封底,总页数控制在 **8-16 页**。超过 20 页通常需要重新拆分为多个 deck。

### Step 3: 逐页填写大纲

每页包含以下字段:

```markdown
### 页 N: <页面主题>
- **段落**: 背景/问题/洞察/方案/证据/行动
- **标题结论**: <观众读完标题就能 get 的论点>
- **核心要点**: 1. ... 2. ... 3. ...
- **证据类型**: 数据 / 案例 / 对比 / 引文 / 图表
- **图表需求**: 是/否,若 是,类型(柱/线/饼/表)
- **可视化需求**: 流程图 / 金句页 / 时间线 / 对比栏 / 大数字
- **来源**: <资料文件名>
- **预计时长**: <分钟>
```

### Step 4: 自检

跑一遍检查清单:

- [ ] 每页标题都是结论,不是中性描述
- [ ] 没有连续 3 页以上都是纯文字列表
- [ ] 每段(背景/问题/...)至少有一页
- [ ] 行动页至少有"谁+何时+做什么"
- [ ] 总页数 8-16 之间
- [ ] 每页都有"证据类型"且不为空
- [ ] 至少 2 页有图表需求

### Step 5: 输出

保存到 `outline.md`。

## 四、配套脚本

### `scripts/build_outline.py`

```python
#!/usr/bin/env python3
"""
PPT 大纲生成器 - 辅助生成符合 CCISEA 框架的 outline.md
"""
import json
import sys
from pathlib import Path
from datetime import datetime


CCISEA_TEMPLATE = {
    "context": {"label": "背景", "min_pages": 1, "max_pages": 2},
    "challenge": {"label": "问题", "min_pages": 1, "max_pages": 2},
    "insight": {"label": "洞察", "min_pages": 2, "max_pages": 3},
    "solution": {"label": "方案", "min_pages": 2, "max_pages": 4},
    "evidence": {"label": "证据", "min_pages": 2, "max_pages": 3},
    "action": {"label": "行动", "min_pages": 1, "max_pages": 2},
}


def make_outline(theme, audience, scenario, slides):
    """
    slides: list of dict, 每项含 section, title, points, evidence, chart_needed, viz_type, source, minutes
    """
    total = len(slides) + 2  # +封面 +封底
    lines = [
        f"# {theme} — 演示大纲",
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

    # 按段落聚合
    by_section = {}
    for i, s in enumerate(slides, start=2):  # 从页 2 开始,留页 1 给封面
        by_section.setdefault(s["section"], []).append((i, s))

    for sec_key, sec_info in CCISEA_TEMPLATE.items():
        if sec_key in by_section:
            page_nums = [str(p[0]) for p in by_section[sec_key]]
            titles = "; ".join(p[1]["title"][:30] for p in by_section[sec_key])
            lines.append(f"| {sec_info['label']} | {', '.join(page_nums)} | {titles} |")

    lines.extend(["", "---", "", "## 二、逐页大纲", ""])
    lines.append("### 页 1: 封面")
    lines.append(f"- **段落**: 封面")
    lines.append(f"- **标题**: {theme}")
    lines.append(f"- **副标题**: {audience} · {scenario}")
    lines.append(f"- **时长**: 0.5")
    lines.append("")

    for i, s in slides:
        sec_label = CCISEA_TEMPLATE[s["section"]]["label"]
        lines.append(f"### 页 {i}: {s['title']}")
        lines.append(f"- **段落**: {sec_label}")
        lines.append(f"- **标题结论**: {s['title']}")
        lines.append(f"- **核心要点**:")
        for p in s.get("points", []):
            lines.append(f"  - {p}")
        lines.append(f"- **证据类型**: {s.get('evidence', '文字')}")
        lines.append(f"- **图表需求**: {'是, ' + s.get('chart_type', '') if s.get('chart_needed') else '否'}")
        lines.append(f"- **可视化需求**: {s.get('viz_type', '无')}")
        lines.append(f"- **来源**: {s.get('source', '-')}")
        lines.append(f"- **预计时长**: {s.get('minutes', 1)} 分钟")
        lines.append("")

    cover_end = len(slides) + 2
    lines.append(f"### 页 {cover_end}: 封底/讨论")
    lines.append(f"- **段落**: 行动")
    lines.append(f"- **标题结论**: 谢谢讨论 — 下一步行动待确认")
    lines.append(f"- **核心要点**:")
    lines.append(f"  - 收集反馈")
    lines.append(f"  - 列出待办责任人")
    lines.append(f"  - 约定下次同步时间")
    lines.append(f"- **时长**: 2")
    lines.append("")

    # 自检
    lines.extend(["---", "", "## 三、自检清单", ""])
    checks = [
        ("每页标题都是结论", all(s["title"].strip() and len(s["title"]) > 4 for s in slides)),
        ("总页数在 8-16 之间", 6 <= len(slides) <= 14),
        ("每段(背景/问题/...)至少有一页", all(k in by_section for k in CCISEA_TEMPLATE)),
        ("至少 2 页有图表需求", sum(1 for s in slides if s.get("chart_needed")) >= 2),
        ("行动页存在", "action" in by_section),
    ]
    for label, ok in checks:
        lines.append(f"- [{'x' if ok else ' '}] {label}")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: build_outline.py <slides.json>")
        print("slides.json 格式: [{\"section\": \"context\", \"title\": \"...\", ...}]")
        sys.exit(1)
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    theme = data.get("theme", "未命名演示")
    audience = data.get("audience", "通用受众")
    scenario = data.get("scenario", "通用场景")
    slides = data["slides"]
    print(make_outline(theme, audience, scenario, slides))


if __name__ == "__main__":
    main()
```

## 五、模板

### `templates/outline_template.md`

```markdown
# <主题> — 演示大纲

> 受众:<受众>
> 场景:<汇报场景>
> 生成时间:<YYYY-MM-DD HH:MM>
> 总页数:<N> (含封面/封底)

---

## 一、整体结构(CCISEA)

| 段落 | 页码范围 | 主要论证 |
|------|---------|----------|
| 背景 | | |
| 问题 | | |
| 洞察 | | |
| 方案 | | |
| 证据 | | |
| 行动 | | |

---

## 二、逐页大纲

### 页 1: 封面
- **段落**: 封面
- **标题**: <主题>
- **副标题**: <受众> · <场景>
- **时长**: 0.5

### 页 2: <页面主题>
- **段落**: 背景/问题/洞察/方案/证据/行动
- **标题结论**: <自带结论的标题>
- **核心要点**:
  1. ...
  2. ...
- **证据类型**: 数据 / 案例 / 对比 / 引文 / 图表
- **图表需求**: 是/否
- **可视化需求**: 流程图 / 金句页 / 时间线 / 对比栏 / 大数字
- **来源**: <资料文件名>
- **预计时长**: <分钟>

(更多页...)

---

## 三、自检清单

- [ ] 每页标题都是结论
- [ ] 总页数在 8-16 之间
- [ ] 每段(背景/问题/...)至少有一页
- [ ] 至少 2 页有图表需求
- [ ] 行动页存在
```

## 六、风险评估

🟢 **低风险** —— 本 Skill 主要输出结构化文本,不执行写文件以外的命令,不访问网络。

## 七、与上下 Skill 的衔接

- **上游**:无 / 用户原始资料
- **下游**: `deck-storyline-designer` 接收 `outline.md`,转化为带叙事张力的 `storyline.md`