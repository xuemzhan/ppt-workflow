---
name: ppt-workflow-orchestrator
description: "PPT 工作流总编排器——基于'10 个 PPT Skills 生产线'思路,把资料整理、结构搭建、故事线设计、内容页生成、图表生成、模板套用、视觉优化、讲稿撰写、质量复盘串成一条端到端流水线。触发关键词:PPT 工作流、deck pipeline、演示生产线、PPT Skills、PPT 工作线、deck 流水线、PPT 全流程、幻灯片生产线。"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ppt, workflow, pipeline, presentation, deck, productivity]
    related_skills: [powerpoint, ppt-outline-builder, deck-storyline-designer, markdown-to-slides, pptx-generator, template-layout-deck, visual-slide-designer, chart-slide-maker, academic-pptx, speaker-notes-writer, deck-review-publisher]
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



# PPT 工作流总编排器 (PPT Workflow Orchestrator)

> "把 PPT 创作从'手搓几页'升级为'演示生产线'。"

## 一、为什么需要这个 Skill

很多人以为 AI 做 PPT 就是"一键生成几页幻灯片"。这个理解不能说错,但有点可惜——就好比买了台高级相机,只用来拍证件照。

本文不讨论让 AI 替你画几页,而是把 PPT 创作拆成一条**生产线**:资料整理、结构搭建、故事线设计、内容页生成、图表生成、模板套用、视觉优化、讲稿撰写、质量复盘。每个环节交给专门的 Skill 处理。

**Skill 是什么?** 把某一类任务的经验、规则、脚本和检查流程封装成一个"拿出来就能用"的工作单元。

## 二、Skill 的三层结构

一个完整的 Skill 通常包含三层:

1. **触发条件** —— 告诉 AI 什么时候该上场。如用户提到 "deck"、"slides"、"presentation"、"汇报"、"幻灯片",相关 Skill 自动亮起来。
2. **操作规程** —— 把模糊任务变成可执行步骤清单。如"先读模板 → 提取文本 → 生成缩略图 → 替换占位符 → 视觉检查"。
3. **配套工具** —— Python、python-pptx、PptxGenJS、Pillow、markdown 解析器等,真正干活的部分。

⚠️ **风险提示**:Skill 能力越强,权限越大,风险越高。能跑脚本的 Skill 比只写提示词的强,但出问题动静也更大。

## 三、10 个 PPT Skill 流水线全景

| 步骤 | Skill | 主要职责 | 输入 | 输出 | 风险 |
|------|-------|---------|------|------|------|
| 1 | `ppt-outline-builder` | 把主题拆成"背景-问题-洞察-方案-证据-行动"骨架 | 资料包 / 主题 | `outline.md` | 🟢 低 |
| 2 | `deck-storyline-designer` | 起承转合,每页标题自带结论 | `outline.md` | `storyline.md` | 🟢 低 |
| 3 | `markdown-to-slides` | Markdown → PPTX/PDF/HTML | `slides.md` | 中间 `slides.pptx` | 🟡 中 |
| 4 | `pptx-generator` | 从零创建或读写改 .pptx | JSON/草稿 | `deck_draft.pptx` | 🟡 中 |
| 5 | `template-layout-deck` | 套模板、保留母版和占位符 | `deck_draft.pptx` + `.potx` | `deck_themed.pptx` | 🟢 低 |
| 6 | `visual-slide-designer` | 文字页 → 视觉页(封面/金句/流程) | 单页内容 | `visual_slide.html` 截图 | 🟡 中 |
| 7 | `chart-slide-maker` | 数据 → 图表页 | Excel/CSV/指标 | `chart_slide.pptx` | 🟡 中 |
| 8 | `academic-pptx` | 学术汇报专用:一论点一洞察 | 论文/课题 | `academic_deck.pptx` | ⚠️ 需审查 |
| 9 | `speaker-notes-writer` | 讲稿、转场句、时长 | `deck_final.pptx` | `speaker_notes.md` | 🟢 低 |
| 10 | `deck-review-publisher` | 复盘、质检、最终导出 | `deck_*.pptx` | `qa_report.md` + `deck_final.pptx/pdf` | 🟡 中 |

## 四、标准文件流转格式

```
资料包 input/
  │
  ▼
结构稿 outline.md
  │
  ▼
故事线 storyline.md
  │
  ▼
幻灯片源文件 slides.md
  │
  ▼
图表规格 chart_spec.json
  │
  ▼
模板配置 template_profile.json
  │
  ▼
初版 deck_draft.pptx
  │
  ▼
讲稿 speaker_notes.md
  │
  ▼
质检报告 qa_report.md
  │
  ▼
终版 deck_final.pptx / deck_final.pdf
```

每个阶段都有中间成果;出了问题不需要推倒重来,只要回到对应环节修改即可。

## 五、五条安全原则

1. **只装可信来源** —— 官方 Skill 优先;社区 Skill 要看源码、依赖和最近维护情况。
2. **最小权限** —— 能不用脚本就不用脚本;能关闭网络就关闭网络;能只读就不要给写入。
3. **敏感数据脱敏** —— 患者信息、合同金额、工资绩效、银行账号,不要直接丢给不可信 Skill。
4. **固定依赖版本** —— 不要让 Skill 每次自动安装最新版依赖。生产环境用锁定版本和隔离虚拟环境。
5. **强制质检** —— PPT 生成完不是结束,是开始。必须经过文本提取、缩略图检查、视觉验证。

## 六、何时加载此 Skill

- 用户说:"帮我做 PPT"、"做一个汇报"、"演讲材料"、"演示文稿"、"deck"
- 用户说:"按生产线出 PPT"、"走 PPT 工作流"、"端到端做幻灯片"
- 用户提供资料 + 目标场景 + 受众,要求生成完整演示

## 七、快速调用

执行单步 Skill:

```
load_skill: ppt-outline-builder
load_skill: deck-storyline-designer
load_skill: markdown-to-slides
load_skill: pptx-generator
load_skill: template-layout-deck
load_skill: visual-slide-designer
load_skill: chart-slide-maker
load_skill: academic-pptx
load_skill: speaker-notes-writer
load_skill: deck-review-publisher
```

执行全链路:

```bash
python scripts/orchestrate.py --input ./examples/sample_deck/input --output ./examples/sample_deck/output
```

## 八、相关 Skill

- `ppt-outline-builder` — 结构搭建
- `deck-storyline-designer` — 故事线设计
- `markdown-to-slides` — Markdown → 幻灯片
- `pptx-generator` — 从零生成 pptx
- `template-layout-deck` — 模板套用
- `visual-slide-designer` — 视觉强化
- `chart-slide-maker` — 图表生成
- `academic-pptx` — 学术汇报
- `speaker-notes-writer` — 讲稿撰写
- `deck-review-publisher` — 质量复盘
- `powerpoint` — 单点 .pptx 读写改