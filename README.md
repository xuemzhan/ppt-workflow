# PPT 工作流能力手册

> 基于《从"手搓 PPT"到"演示生产线":10 个 PPT Skills 构成的工作流》
> 一文实现的端到端 PPT 制作流水线。

---

## 一、能力速览

本套件把 PPT 创作拆成 10 个独立但可串接的 Skill,每个 Skill 完成流水线中的一个明确环节。

| # | Skill | 职责 | 输入 | 输出 |
|---|-------|------|------|------|
| 1 | `ppt-outline-builder` | 把主题拆成结构骨架 | 资料/主题 | `outline.md` |
| 2 | `deck-storyline-designer` | 设计叙事弧 + Hook + 转场 + CTA | `outline.md` | `storyline.md` |
| 3 | `markdown-to-slides` | Markdown → 幻灯片源 | `slides.md` | `slides.md` (简化) |
| 4 | `pptx-generator` | 从 JSON spec 精确生成 .pptx | `spec.json` | `deck_draft.pptx` |
| 5 | `template-layout-deck` | 套用公司/客户模板 | `template.pptx` + 内容 | `deck_themed.pptx` |
| 6 | `visual-slide-designer` | 强化视觉(封面/金句/流程) | 内容 | `visual_*.png` |
| 7 | `chart-slide-maker` | 数据 → 图表 | CSV/JSON | `chart_*.png` |
| 8 | `academic-pptx` | 学术汇报专用大纲 | 论文/课题 | 学术 outline |
| 9 | `speaker-notes-writer` | 写讲稿、估时长 | deck | `speaker_notes.md` |
| 10 | `deck-review-publisher` | QA + 缩略图 + 导出 PDF | deck | `qa_report.md` + `.pdf` |

**额外**:
- `ppt-workflow-orchestrator` —— 总编排,一键走完整流水线

---

## 二、目录结构

```
ppt-workflow/
├── README.md                       # 本文件
├── docs/                           # 进阶文档
│   ├── 01_快速开始.md
│   ├── 02_各 Skill 详解.md
│   ├── 03_常见场景案例.md
│   └── 04_安全原则与风险评估.md
├── skills/                         # 10 个 Skill
│   ├── ppt-workflow-orchestrator/
│   ├── ppt-outline-builder/
│   ├── deck-storyline-designer/
│   ├── markdown-to-slides/
│   ├── pptx-generator/
│   ├── template-layout-deck/
│   ├── visual-slide-designer/
│   ├── chart-slide-maker/
│   ├── academic-pptx/
│   ├── speaker-notes-writer/
│   └── deck-review-publisher/
├── scripts/
│   └── orchestrate.py              # 总编排脚本
├── templates/                      # 通用模板
│   └── theme/                      # 主题色板
└── examples/                       # 示例
    └── sample_deck/
        ├── input/
        └── output/
```

---

## 三、三种使用方式

### 方式 1:零配置一键运行(适合"先出个东西看看")

```bash
mkdir my-deck && cd my-deck
mkdir input output
echo "2026 年中评审" > input/scenario.txt
echo "公司管理层" > input/audience.txt
echo "智能办公套件 V1.0 阶段性成果" > input/theme.txt

python scripts/orchestrate.py --input input --output output
```

产出:
- `output/outline.md` —— 演示骨架
- `output/storyline.md` —— 故事线
- `output/deck_final.pptx` —— 终版 PPT
- `output/qa_report.md` —— 质检报告

### 方式 2:用 slides.json 自定义骨架(推荐)

在 `input/` 中准备 `slides.json`:

```json
{
  "theme": "智能办公套件 V1.0",
  "audience": "公司管理层",
  "scenario": "2026 年中评审",
  "slides": [
    {"section": "context", "title": "我们正站在办公方式变革的拐点", "points": ["远程协作成为常态", "AI 工具普及", "效率瓶颈显现"], "evidence": "数据", "chart_needed": true, "chart_type": "柱状图", "viz_type": "对比栏", "source": "行业报告 2026", "minutes": 2},
    {"section": "challenge", "title": "员工每天浪费 30 分钟在文件检索上", "points": ["检索耗时", "工具分散", "知识难沉淀"], "evidence": "调研", "chart_needed": false, "viz_type": "无", "source": "内部调研 2026Q2", "minutes": 2},
    {"section": "insight", "title": "三件事决定了这次升级", "points": ["WPS 集成需求", "本地搜索痛点", "知识库分散"], "evidence": "案例", "chart_needed": false, "viz_type": "流程图", "source": "用户访谈", "minutes": 2},
    {"section": "solution", "title": "套件以 Agent + 工具融合为核心", "points": ["AionUI 作为入口", "Everything + Tesseract 提供本地能力", "Obsidian 提供知识沉淀"], "evidence": "案例", "chart_needed": false, "viz_type": "流程图", "source": "架构设计", "minutes": 2},
    {"section": "evidence", "title": "试点数据显示检索时间从 30min 降到 5s", "points": ["检索效率提升 360 倍", "用户满意度 4.7/5"], "evidence": "数据", "chart_needed": true, "chart_type": "柱状图", "viz_type": "对比栏", "source": "试点报告", "minutes": 2},
    {"section": "action", "title": "Q4 前完成全员部署,需批 50 万预算", "points": ["8 月完成 50 人试点", "10 月全员上线", "12 月收反馈迭代"], "evidence": "行动", "chart_needed": false, "viz_type": "无", "source": "项目计划", "minutes": 1.5}
  ]
}
```

```bash
python scripts/orchestrate.py --input input --output output
```

### 方式 3:用 spec.json 精确控制(高级)

直接写 `spec.json`,每页指定 type(title/bullet/two_column/stat/quote/process/table/timeline/thank_you):

```json
{
  "theme": {"primary_color": "1E2761", "accent_color": "F96167"},
  "slides": [
    {"type": "title", "title": "...", "subtitle": "...", "author": "...", "date": "..."},
    {"type": "section", "section_number": "01", "title": "..."},
    {"type": "bullet", "title": "...", "bullets": [{"text": "...", "level": 0}], "note": "..."},
    {"type": "two_column", "title": "...", "left": {"heading": "...", "items": ["..."]}, "right": {"heading": "...", "items": ["..."]}},
    {"type": "stat", "title": "...", "stats": [{"value": "30min", "label": "→ 5s", "description": "..."}]},
    {"type": "quote", "text": "...", "attribution": "..."},
    {"type": "process", "title": "...", "steps": [{"title": "步骤 1", "description": "..."}]},
    {"type": "table", "title": "...", "headers": ["...", "..."], "rows": [["...", "..."]]},
    {"type": "timeline", "title": "...", "events": [{"date": "Q1", "title": "...", "description": "..."}]},
    {"type": "thank_you", "title": "谢谢", "subtitle": "欢迎讨论"}
  ]
}
```

```bash
# 跳过 outline/storyline,直接用 spec 出 PPT
python scripts/orchestrate.py --input input --output output --skip-outline --skip-storyline
```

---

## 四、单 Skill 调用

每个 Skill 都可独立使用。例:

```bash
# 仅生成大纲
python skills/ppt-outline-builder/scripts/build_outline.py slides.json outline.md

# 仅生成图表
python skills/chart-slide-maker/scripts/render_chart.py chart_spec.json chart.png

# 仅做 QA
python skills/deck-review-publisher/scripts/qa_check.py deck_final.pptx qa_report.md
```

完整脚本列表见各 Skill 目录下的 `SKILL.md`。

---

## 五、典型场景

### 场景 1:季度汇报(15 分钟)

```bash
# 1. 写 slides.json(场景/主题/受众/6-8 页骨架)
# 2. 一键编排
python scripts/orchestrate.py --input q3_input --output q3_output
# 3. 收到 deck_final.pptx,人工微调
# 4. 用 deck-review-publisher 复检
python skills/deck-review-publisher/scripts/qa_check.py q3_output/deck_final.pptx q3_output/qa.md
```

### 场景 2:客户提案(30 分钟,套客户模板)

```bash
python scripts/orchestrate.py --input proposal_input --output proposal_output \
    --template client_template.pptx
# deck_themed.pptx 已自动套用客户模板
```

### 场景 3:学术答辩(15 分钟)

```bash
# 用 academic-pptx 生成大纲
python skills/academic-pptx/scripts/build_academic_outline.py thesis \
    "基于深度学习的 xxx 方法研究" thesis_outline.md

# 把 thesis_outline.md 转成 slides.json,然后跑编排
python scripts/orchestrate.py --input thesis_input --output thesis_output
```

### 场景 4:数据汇报(图表密集)

```bash
# 准备 chart_data/*.json(每个文件一个图表 spec)
# 准备 slides.json(只写结构,不动数据)
python scripts/orchestrate.py --input data_input --output data_output
# chart_data/ 下的所有 .json 都会自动渲染成 PNG 到 charts/
```

---

## 六、配色与主题

默认配色:Midnight Executive(午夜高管)
- 主色:`#1E2761`(深蓝)
- 辅色:`#CADCFC`(冰蓝)
- 强调:`#F96167`(珊瑚红)

可在 `skills/markdown-to-slides/templates/template_profile.json` 中修改。
预设主题备选:

| 主题 | 主色 | 强调 | 适用场景 |
|------|------|------|----------|
| Midnight Executive | `1E2761` | `F96167` | 默认/正式商务 |
| Forest & Moss | `2C5F2D` | `97BC62` | 绿色环保/可持续发展 |
| Coral Energy | `F96167` | `F9E795` | 营销/品牌活力 |
| Ocean Gradient | `065A82` | `21295C` | 科技/创新 |
| Charcoal Minimal | `36454F` | `212121` | 极简/学术 |
| Cherry Bold | `990011` | `2F3C7E` | 红色/警示/医疗 |

---

## 七、依赖清单

### 必备(已通过 pip 安装)
- `python-pptx >= 1.0.0`
- `Pillow >= 10.0`

### 可选(按需安装)
- `markitdown` —— PPTX 文本提取(更智能)
- `playwright` —— visual-slide-designer 高质量截图
- `LibreOffice (soffice)` —— PPTX ↔ PDF 转换
- `Poppler (pdftoppm)` —— PDF → JPG

### 字体
- Windows:自带 Microsoft YaHei
- macOS:自带 PingFang SC
- Linux:需安装 `fonts-noto-cjk` 或类似字体

---

## 八、安全原则(来自原文)

1. **只装可信来源** —— 官方 Skill 优先;社区 Skill 要看源码、依赖和最近维护情况。
2. **最小权限** —— 能不用脚本就不用脚本;能只读就不要给写入。
3. **敏感数据脱敏** —— 患者信息、合同金额、工资绩效、银行账号,不要直接丢给 Skill。
4. **固定依赖版本** —— 锁定版本,不自动升级。
5. **强制质检** —— PPT 生成完不是结束,是开始。

---

## 九、常见问题

**Q:生成的 PPT 没有 LibreOffice,能转 PDF 吗?**
A:不能。PPT → PDF 必须经 LibreOffice。如无 LibreOffice,QA 报告会跳过 PDF 部分,但 PPTX 仍然可用。

**Q:中文标题在 PowerPoint 里显示为方框怎么办?**
A:通常是字体问题。把 PPT 模板的字体改为"思源黑体"或"微软雅黑"。Linux 上需安装 CJK 字体。

**Q:visual-slide-designer 的截图是空白的?**
A:Playwright/Chrome 未安装或 HTML 路径含特殊字符。运行 `python -c "from playwright.sync_api import sync_playwright"` 测试。

**Q:图表数据更新后如何重新生成?**
A:`python skills/chart-slide-maker/scripts/render_chart.py spec.json out.png`

**Q:能不能加页/删页?**
A:删页:直接编辑 `deck_final.pptx`(PowerPoint)或修改 `spec.json` 重跑。加页:修改 `spec.json` 增加 slide,然后只跑 Step 4-7。

---

## 十、命令行参数

| 参数 | 作用 |
|------|------|
| `--input <dir>` | 输入目录(含 theme.txt/audience.txt/scenario.txt/slides.json/chart_data/) |
| `--output <dir>` | 输出目录(产物落盘位置) |
| `--theme "..."` | 覆盖 theme.txt |
| `--audience "..."` | 覆盖 audience.txt |
| `--scenario "..."` | 覆盖 scenario.txt |
| `--template <file.pptx>` | 套用公司/客户模板 |
| `--force` | 强制全量重跑,忽略已有产物 |
| `--list` | 列出所有可用 Skill 后退出(不需 --input/--output) |
| `--skip-outline` | 跳过大纲生成 |
| `--skip-storyline` | 跳过故事线生成 |
| `--skip-template` | 跳过模板套用 |
| `--skip-notes` | 跳过讲稿生成 |
| `--skip-qa` | 跳过 QA 质检 |

## 十一、产物清单

每次跑完会在 `output_dir` 产生:

| 文件 | 来自 Skill | 说明 |
|------|------------|------|
| `outline.md` | ppt-outline-builder | 演示骨架(CCISEA 六段式) |
| `storyline.md` | deck-storyline-designer | 故事线 + Hook + 转场 + CTA |
| `slides.md` | markdown-to-slides | 简化版 Markdown 源文件 |
| `spec.json` | pptx-generator | 严格 JSON spec,可二次编辑 |
| `deck_draft.pptx` | pptx-generator | 初版 PPT |
| `deck_themed.pptx` | template-layout-deck | 套用模板后(若提供 --template) |
| `deck_final.pptx` | - | 终版(含备注) |
| `deck_final.pdf` | deck-review-publisher | PDF 导出(需 LibreOffice,本机未装时跳过) |
| `speaker_notes.md` | speaker-notes-writer | 草稿讲稿(从 outline 派生) |
| `qa_report.md` | deck-review-publisher | 质检报告 |
| `thumbnails.jpg` | deck-review-publisher | 缩略图网格(零 LibreOffice 依赖) |
| `charts/*.png` | chart-slide-maker | 数据图表 |
| `workflow_log.md` | - | 运行日志 |

## 十二、幂等性 & 错误传递

```bash
# 第一次:跑全部
python scripts/orchestrate.py --input input --output output

# 改了 slides.json 后:只跑受影响步骤
#   (因为 outline.md 已存在 → Step 1 跳过)
#   (因为 spec.json 已存在 → Step 4 跳过)
#   (但 deck_draft.pptx 已存在 → Step 5 跳过)

# 强制全量重跑
python scripts/orchestrate.py --input input --output output --force
```

任一关键步失败立即终止,不连环崩溃。可在中间任意时刻 `--skip-xxx` 跳过。

## 十三、数量级自适应(chart-slide-maker v1.1)

当数据最大值/最小值 > 50 倍,自动切换到**对数刻度** + 标题加 [对数刻度] 提示,避免小柱完全不可见。已实测:30min vs 0.083min 的 360 倍差异,两柱都清晰可见。

## 十四、QA 扩展(v1.1)

`qa_check.py` 现在检测 5 类问题:

1. **占位符残留**(lorem/xxxx/click here 等)
2. **硬编码占位词**(对照 1/选项 A/示例文本/此处输入 等)
3. **重复文本**(同 shape 内 text 出现 ≥2 次)
4. **字号过小**(< 12pt 投影看不见)
5. **页数合理性** / **备注缺失**

## 十五、套模板示例(v1.1)

```bash
# 1. 准备模板(用本项目自带的 examples/make_company_template.py)
python examples/make_company_template.py examples/company_template.pptx

# 2. 准备内容 spec(版式索引对应模板版式)
#    examples/sample_deck/template_content.json 已经准备好

# 3. 套模板生成
python skills/template-layout-deck/scripts/apply_template.py \
    examples/company_template.pptx \
    examples/sample_deck/template_content.json \
    examples/sample_deck/output/deck_templated.pptx
```

## 十六、Roadmap

- [x] ~~接 LLM 自动生成 speaker_notes.md~~ → 已实现从 outline 自动派生草稿
- [x] ~~QA 报告扩展~~ → 已支持 5 类问题检测
- [x] ~~幂等性/错误传递~~ → 已实现
- [x] ~~数量级自适应图表~~ → 已实现
- [x] ~~缩略图零 LibreOffice 方案~~ → 已实现 render_thumbnails.py
- [ ] 接 LLM 真正生成 slides.json(从主题+受众)
- [ ] 支持 Marp / Pandoc 路径
- [ ] 可视化工作流编辑器
- [ ] Web UI(Hermes Agent 集成)

## 十七、项目结构

```
ppt-workflow/
├── README.md                       # 本文件
├── .gitignore                      # Git 忽略规则
├── pyproject.toml                  # Python 项目配置 + pytest
├── scripts/
│   └── orchestrate.py              # 总编排(10 步流水线)
├── skills/                         # 11 个 Skill + shared
│   ├── shared/                     # 共享模块(★v1.3 核心)
│   │   ├── __init__.py
│   │   ├── utils.py                # load_json / write_json / hex_to_rgb
│   │   ├── fonts.py                # 跨平台字体路径
│   │   ├── logging_config.py       # 统一日志配置
│   │   ├── types.py                # 数据契约(TypedDict/dataclass)
│   │   └── cli.py                  # argparse 基类
│   ├── ppt-workflow-orchestrator/
│   ├── ppt-outline-builder/
│   ├── deck-storyline-designer/
│   ├── markdown-to-slides/
│   ├── pptx-generator/
│   ├── template-layout-deck/
│   ├── visual-slide-designer/
│   ├── chart-slide-maker/
│   ├── academic-pptx/
│   ├── speaker-notes-writer/
│   └── deck-review-publisher/
├── tests/                          # 单元测试 + 集成测试
│   ├── conftest.py                 # 共享 fixture
│   ├── test_utils.py               # shared/utils.py 单测
│   ├── test_fonts.py               # shared/fonts.py 单测
│   ├── test_types.py               # shared/types.py 单测
│   └── test_e2e.py                 # 5 个端到端集成测试
└── examples/
    ├── quickstart.py               # 一键体验
    ├── slides_template.json         # AI 集成模板
    ├── make_company_template.py     # 构造公司模板
    ├── company_template.pptx
    ├── demo_input/                  # 一键 demo 输入
    ├── demo_output/                 # 一键 demo 输出
    └── sample_deck/                 # 完整示例
        ├── input/
        └── output/
```

### shared/ 模块说明

所有 Skill 脚本统一通过 `skills/shared/` 复用基础设施:

| 模块 | 暴露的 API | 用途 |
|------|-----------|------|
| `utils.py` | `load_json`, `write_json`, `hex_to_rgb`, `read_text`, `write_text`, `ensure_dir`, `project_root` | I/O 与通用工具 |
| `fonts.py` | `get_font_path`, `get_font_path_optional`, `check_font_availability` | 跨平台字体路径 |
| `logging_config.py` | `setup_logging`, `get_logger` | 统一日志 |
| `types.py` | `SlideItem`, `SlidesJson`, `SlideSpec`, `Spec`, `ThemeSpec`, `ChartSpec` 等 11 个 | 数据契约 |
| `cli.py` | `create_base_parser`, `parse_args` | argparse 标准化 |

接入方式:在每个脚本顶部加:

```python
# IMPORTANT: path setup must come BEFORE any skills.* imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from skills.shared.utils import load_json, write_json, hex_to_rgb
from skills.shared.logging_config import setup_logging
setup_logging()
```

## 十八、测试

### 跑测试

```bash
# 全部
python -m pytest tests/ -v

# 只单元测试(shared 模块)
python -m pytest tests/test_utils.py tests/test_fonts.py tests/test_types.py -v

# 只集成测试(端到端)
python -m pytest tests/test_e2e.py -v
```

### 测试覆盖

| 类型 | 数量 | 覆盖范围 |
|------|------|----------|
| 单元测试 | 32 | `shared/utils`、`shared/fonts`、`shared/types` |
| 集成测试 | 5 | orchestrate 端到端、图表数量级、模板套用、QA 检出、spec 验证 |
| **合计** | **37** | — |

### 集成测试场景

1. `test_orchestrator_runs_full_pipeline` — 从 input 跑 10 步流水线,验证所有产物存在
2. `test_chart_renders_with_log_scale` — 数据差异 > 50x 时自动对数刻度
3. `test_template_layout_preserves_placeholders` — 模板套用内容正确
4. `test_qa_detects_issues` — 硬编码占位词检出
5. `test_validate_spec_catches_unknown_types` — 未知 type 拒绝

## 十九、Roadmap

- [x] ~~接 LLM 自动生成 speaker_notes.md~~ → 已实现从 outline 自动派生草稿
- [x] ~~QA 报告扩展~~ → 已支持 5 类问题检测
- [x] ~~幂等性/错误传递~~ → 已实现
- [x] ~~数量级自适应图表~~ → 已实现
- [x] ~~缩略图零 LibreOffice 方案~~ → 已实现 render_thumbnails.py
- [x] ~~shared 模块接入生产脚本~~ → 5 个高频脚本已接入(v1.3)
- [x] ~~集成测试~~ → 5 个端到端测试(37 总测试)
- [x] ~~统一 logger 配置~~ → 所有脚本用 setup_logging
- [ ] 接 LLM 真正生成 slides.json(从主题+受众)
- [ ] 支持 Marp / Pandoc 路径
- [ ] 可视化工作流编辑器
- [ ] Web UI(Hermes Agent 集成)
