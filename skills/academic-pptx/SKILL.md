---
name: academic-pptx
description: "学术 PPT 制作器——按学术汇报的逻辑出 PPT:一个核心论点、一页一个洞察、每张图都服务标题、引用与参考文献清晰。适合论文答辩、课题汇报、学术报告、文献综述。触发词:学术 PPT、论文答辩、课题汇报、学术报告、文献综述演示、thesis defense。"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ppt, academic, thesis, defense, research, presentation, deck]
    related_skills: [ppt-workflow-orchestrator, markdown-to-slides, pptx-generator]
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



# 学术 PPT 制作器 (academic-pptx)

> "学术 PPT 有自己的逻辑:一个核心论点、一页一个洞察、每张图都服务标题、引用与参考文献清晰。"

## 一、目标

按学术汇报的特殊要求生成 PPT:
1. 围绕**单一核心论点**(central thesis)组织全篇
2. **每页一个洞察**(one insight per slide)
3. **每张图/表都服务标题**(figure serves the headline)
4. **引用规范清晰**(citations)
5. **结尾给出明确 takeaway**

## 二、何时使用

- 论文答辩、课题评审、文献综述
- 学术会议口头报告、海报演讲
- 研究进展汇报、博士开题/中期/答辩
- 实验结果汇报、方法学介绍

## 三、操作规程

### Step 1: 确定核心论点(Central Thesis)

用一句话回答:"如果观众只能记住一件事,那是什么?"

```
差: "本文研究了一种新方法"
好: "本文提出的 X 方法,在 Y 任务上比 SOTA 平均提升 12.4%,
    且推理速度提高 3 倍,适合边缘部署场景"
```

核心论点 = 标题 = 摘要 = 第 1 页 = 第 N 页

### Step 2: 学术 PPT 标准结构

| 段落 | 页数 | 内容 |
|------|------|------|
| 标题 + 核心论点 | 1 | 标题/作者/会议/一句话论点 |
| 动机 | 1-2 | 为什么这个问题重要 |
| 已有方法局限 | 1-2 | 前人工作的 gap |
| 本文方法 | 2-3 | 方法核心思想、模型图、关键公式 |
| 实验结果 | 3-5 | 主表、主图、消融实验、案例分析 |
| 讨论 | 1 | 局限性、未来工作 |
| 结论 | 1 | 重申论点 + takeaway |
| 谢谢/Q&A | 1 | 联系方式 |
| 参考文献 | 0-1 | 选关键 3-5 篇 |

总页数: **12-20 页**(短报告 10-12,长报告 18-20)

### Step 3: 每页一个洞察

学术页的标题必须是一个**判断**,而不是"实验结果"这种中性描述:

```
❌ 差标题:
- 实验结果
- 消融实验
- 方法介绍
- 数据集

✅ 好标题(每页一个洞察):
- X 在 Y 任务上超过 SOTA 12.4%,且保持 3x 推理速度
- 去掉 Z 模块导致性能下降 8.7%,说明 Z 是关键设计
- 方法 A 与 B 在大模型上差距扩大,但在小模型上相当
- 图 3 揭示了 X 方法在长序列上的失败模式
```

### Step 4: 图/表规范

学术 PPT 的图/表必须:

1. **服务于标题** —— 标题给出"判断",图/表给出"证据"。观众看标题 + 图/表 = 完整论点
2. **清晰的标注** —— 坐标轴标签、单位、图例、误差棒、显著性
3. **数字大、字号大** —— 投影时观众在最后一排也要看清
4. **避免一图多观点** —— 一张图只表达一个发现,需要多个发现就拆多张
5. **配色友好色盲** —— 避免纯红+纯绿对比
6. **引用规范** —— 图/表下方注明 "[来源:本文图 X]" 或 "[改编自:Smith et al., 2023]"

### Step 5: 引用格式

学术 PPT 常用引用样式(任选一种并全文统一):

```
[1] Smith et al., "Title", Conference, Year.
[1] (Smith et al., 2023)
[1] Smith2023
```

页内引用:角落或图下方。末尾参考文献页:列出关键 3-10 篇。

### Step 6: 输出

按以下格式输出:

```
academic_deck/
├── outline.md           # 学术大纲
├── slides.md            # Markdown 源文件
├── spec.json            # 严格 spec(pptx-generator 入口)
├── figures/             # 图表 PNG
├── deck_draft.pptx
└── deck_final.pptx      # 终版
```

## 四、学术场景模板

### 模板 A: 论文答辩(15 分钟)

```markdown
1. 标题页(标题/作者/答辩日期)
2. 一句话核心论点
3. 背景:这个领域的关键问题
4. 已有方法的局限
5. 本文方法:核心思路
6. 方法:模型架构图
7. 实验设置:数据集/评价指标/基线
8. 主结果:与 SOTA 对比(表)
9. 主结果可视化(主图)
10. 消融实验:每个模块的贡献
11. 案例分析
12. 局限性
13. 未来工作
14. 结论:重申论点
15. Q&A
```

### 模板 B: 课题中期汇报(20 分钟)

```markdown
1. 课题名 / 起止时间 / 汇报阶段
2. 课题目标(原始任务书)
3. 当前进展(完成项)
4. 当前进展(进行中)
5. 关键技术路线
6. 已取得的关键结果
7. 阶段性结论
8. 遇到的问题与对策
9. 下阶段计划
10. 时间节点
11. 需要的支持
12. Q&A
```

### 模板 C: 文献综述(30 分钟)

```markdown
1. 主题/范围
2. 文献检索策略
3. 主题分类(领域地图)
4. 方法 A 综述(2-3 页)
5. 方法 B 综述(2-3 页)
6. 方法 C 综述(2-3 页)
7. 横向对比(表)
8. 研究 gap
9. 未来方向
10. 参考文献清单
```

## 五、配套脚本

### `scripts/build_academic_outline.py`

```python
#!/usr/bin/env python3
"""
学术大纲生成器:按学术 PPT 标准结构生成 outline.md
"""
import sys
from pathlib import Path
from datetime import datetime


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


def main():
    if len(sys.argv) < 3:
        print("用法: build_academic_outline.py <thesis|midterm|review> <title> [output.md]")
        sys.exit(1)
    template = sys.argv[1]
    title = sys.argv[2]
    out_path = Path(sys.argv[3]) if len(sys.argv) >= 4 else None

    if template not in TEMPLATES:
        print(f"未知模板:{template},可选:{','.join(TEMPLATES.keys())}")
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
            lines.append(f"### 页 {page}: {sec_name}{' - ' + str(i+1) if sec_pages > 1 else ''}")
            lines.append(f"- **段落**:{sec_name}")
            lines.append(f"- **标题(自带结论)**: <此页的核心发现/判断>")
            lines.append(f"- **核心要点**:")
            lines.append(f"  - <要点 1>")
            lines.append(f"- **图表/表格需求**: <是 / 否,若是,描述>")
            lines.append(f"- **引用**: [1] <来源>")
            lines.append(f"- **时长**: <分钟>")
            lines.append("")
            page += 1

    lines.extend([
        "---",
        "",
        "## 四、参考文献清单",
        "",
        "[1] <作者> et al., \"<标题>\", <会议/期刊>, <年份>.",
        "[2] ...",
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

## 六、风险评估

⚠️ **未审查** —— 学术 PPT 涉及引用、数据真实性,务必用户自查引用、数据、图片版权。

## 七、与上下 Skill 的衔接

- **上游**: 用户的研究笔记、论文、图表
- **下游**: 用 `markdown-to-slides` 转成 .pptx,或 `pptx-generator` 从 spec.json 出精确版