---
name: template-layout-deck
description: "模板套用器——先分析 PowerPoint 母版和占位符,再把内容'塞'进合适的布局。适合公司汇报、咨询方案、董事会材料等需要统一模板的正式材料。触发词:套模板、用母版、套版式、应用公司模板、PPT 套用 .potx、占位符替换。"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ppt, template, master, layout, placeholder, deck]
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



# 模板套用器 (template-layout-deck)

> "先分析 PowerPoint 的母版和占位符,再把内容'塞'进合适的布局里。"

## 一、目标

读取客户/公司提供的 `.pptx` 或 `.potx` 母版,识别其版式(Layout)、母版(Master)、占位符(Placeholder)。然后把初版 PPT 的内容"映射"到对应版式上,而不是粗暴替换文本。

## 二、何时使用

- 公司/客户/单位有统一的 PPT 模板(常见于咨询、银行、政府汇报)
- 需要保留模板中的 logo、页眉、页脚、配色、字体
- 模板版式比较复杂(标题页、章节页、对比页、数据页各有专用版式)
- 同一份 PPT 需要按多个不同模板出多个版本

## 三、操作规程

### Step 1: 分析模板

```python
from pptx import Presentation
tmpl = Presentation("template.pptx")
print(f"幻灯片尺寸: {tmpl.slide_width} x {tmpl.slide_height}")
print(f"版式数: {len(tmpl.slide_layouts)}")
for i, layout in enumerate(tmpl.slide_layouts):
    placeholders = [(ph.placeholder_format.idx, ph.placeholder_format.type, ph.name) for ph in layout.placeholders]
    print(f"  版式 {i}: {layout.name}, 占位符={placeholders}")
```

把输出保存到 `template_profile.json`:

```json
{
  "template_path": "company_template.pptx",
  "slide_size": {"width": 12192000, "height": 6858000},
  "layouts": [
    {
      "index": 0,
      "name": "封面",
      "placeholders": [
        {"idx": 0, "type": "TITLE", "name": "标题 1"},
        {"idx": 1, "type": "SUBTITLE", "name": "副标题 2"}
      ]
    },
    {
      "index": 1,
      "name": "标题+内容",
      "placeholders": [
        {"idx": 0, "type": "TITLE", "name": "标题 1"},
        {"idx": 1, "type": "BODY", "name": "内容占位符 2"}
      ]
    }
  ],
  "fonts": {"header": "思源黑体", "body": "思源宋体"},
  "colors": {"primary": "0E2A4E", "accent": "C8102E"}
}
```

### Step 2: 内容分类

把初版 PPT 每页内容映射到版式:

| 初版类型 | 目标版式 |
|----------|----------|
| 封面 | "封面" |
| 章节页 | "标题页" / "分隔页" |
| 项目符号 | "标题+内容" |
| 对比栏 | "两栏内容" / "比较" |
| 大数字 | "标题+内容"(自定义) |
| 引用 | "仅标题" / "标题页" |
| 时间线 | "标题+内容"(自定义) |
| 封底 | "标题页"(改成"谢谢") |

### Step 3: 套用版式

读取模板的对应版式,克隆其占位符形状,把内容写入占位符。

```python
from pptx import Presentation
from copy import deepcopy

# 加载模板
tmpl = Presentation("template.pptx")

# 用模板创建空 deck
deck = Presentation("template.pptx")  # 这样保留母版
# 删除模板里已有的示例页(假设前 N 页是示例)
# ...

# 用指定版式添加新页
def add_with_layout(deck, layout_index, content):
    layout = deck.slide_layouts[layout_index]
    slide = deck.slides.add_slide(layout)
    for ph in slide.placeholders:
        idx = ph.placeholder_format.idx
        if idx in content:
            ph.text = content[idx]
    return slide
```

### Step 4: 保留视觉元素

模板的 logo、页脚、配色、字体由**版式继承**——只要不主动删除 `slide_master`,新加的页面会自动带这些元素。

如果模板有特殊的"每页 logo"或"每页页脚":通常在 `slide_master` 中,通过版式继承即可。

### Step 5: 输出

保存为 `deck_themed.pptx`。

## 四、配套脚本

### `scripts/apply_template.py`

```python
#!/usr/bin/env python3
"""
模板套用:把内容 spec 应用到指定 .pptx 模板的版式上

用法:
    python apply_template.py <template.pptx> <content.json> <output.pptx>

content.json 格式:
{
  "slides": [
    {
      "layout_index": 0,           // 对应模板的 slide_layouts 索引
      "layout_name": "封面",        // 注释用,便于人工核对
      "placeholders": {
        "0": "智能办公套件 V1.0 汇报",   // idx 0 的占位符
        "1": "2026 年中评审"
      }
    },
    ...
  ]
}
"""
import json
import sys
from pathlib import Path
from copy import deepcopy
from pptx import Presentation


def analyze_template(tmpl_path):
    """分析模板结构,输出模板配置"""
    tmpl = Presentation(str(tmpl_path))
    info = {
        "slide_size": {"width": tmpl.slide_width, "height": tmpl.slide_height},
        "layouts": []
    }
    for i, layout in enumerate(tmpl.slide_layouts):
        phs = []
        for ph in layout.placeholders:
            phs.append({
                "idx": ph.placeholder_format.idx,
                "type": str(ph.placeholder_format.type),
                "name": ph.name,
            })
        info["layouts"].append({"index": i, "name": layout.name, "placeholders": phs})
    return info


def add_with_layout(deck, layout_index, content):
    layout = deck.slide_layouts[layout_index]
    slide = deck.slides.add_slide(layout)
    for ph in slide.placeholders:
        idx = str(ph.placeholder_format.idx)
        if idx in content:
            ph.text = content[idx]
    return slide


def main():
    if len(sys.argv) < 3:
        print("用法: apply_template.py <template.pptx> <content.json> <output.pptx>")
        print("      apply_template.py <template.pptx> --analyze")
        sys.exit(1)

    tmpl_path = Path(sys.argv[1])

    if "--analyze" in sys.argv:
        info = analyze_template(tmpl_path)
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return

    if len(sys.argv) < 4:
        print("错误:缺少 content.json 或 output.pptx")
        sys.exit(1)

    content_path = Path(sys.argv[2])
    out_path = Path(sys.argv[3])
    content = json.loads(content_path.read_text(encoding="utf-8"))

    deck = Presentation(str(tmpl_path))

    n = 0
    for slide_spec in content.get("slides", []):
        layout_idx = slide_spec.get("layout_index", 1)
        if layout_idx >= len(deck.slide_layouts):
            print(f"警告:版式索引 {layout_idx} 超出范围,跳过")
            continue
        add_with_layout(deck, layout_idx, slide_spec.get("placeholders", {}))
        n += 1

    deck.save(str(out_path))
    print(f"已套用模板并生成:{out_path} ({n} 页)")


if __name__ == "__main__":
    main()
```

### `scripts/analyze_template.py`

```python
#!/usr/bin/env python3
"""分析 PPTX 模板结构,输出 JSON 配置
用法: analyze_template.py <template.pptx> [output.json]
"""
import json
import sys
from pathlib import Path
from pptx import Presentation

if len(sys.argv) < 2:
    print("用法: analyze_template.py <template.pptx> [output.json]")
    sys.exit(1)

tmpl = Presentation(sys.argv[1])
info = {
    "template_path": str(sys.argv[1]),
    "slide_size": {"width": tmpl.slide_width, "height": tmpl.slide_height},
    "layouts": []
}
for i, layout in enumerate(tmpl.slide_layouts):
    phs = []
    for ph in layout.placeholders:
        phs.append({
            "idx": ph.placeholder_format.idx,
            "type": str(ph.placeholder_format.type),
            "name": ph.name,
        })
    info["layouts"].append({"index": i, "name": layout.name, "placeholders": phs})

out = json.dumps(info, ensure_ascii=False, indent=2)
if len(sys.argv) >= 3:
    Path(sys.argv[2]).write_text(out, encoding="utf-8")
    print(f"已写入:{sys.argv[2]}")
else:
    print(out)
```

## 五、常见陷阱

1. **占位符 idx 错位** —— 模板的"封面"版式 idx 可能不是 0,务必通过 `--analyze` 确认。
2. **占位符继承字体** —— 在占位符上写文本时,直接 `ph.text = "..."` 会保留版式定义的字体;但如果用 `text_frame` 重设,可能覆盖。
3. **母版 vs 版式** —— 修改母版会改动所有页面;只改版式只影响该版式对应的页面。
4. **嵌入字体** —— 如果 PPT 要在没装对应字体的机器上播放,需要嵌入字体(PowerPoint 选项 → 保存 → 嵌入字体)。
5. **不要直接复制 shape 元素** —— 不同模板的 shape element XML 结构可能不同,复制会出错。应通过版式继承。

## 六、风险评估

🟢 **低风险** —— 主要读模板的 XML 结构,不执行网络命令。⚠️ 注意:模板文件的版权合规需用户自行负责。

## 七、与上下 Skill 的衔接

- **上游**: `pptx-generator` 出 `deck_draft.pptx`,或 `markdown-to-slides` 出初版
- **下游**: `visual-slide-designer` 给关键页做视觉强化,或 `deck-review-publisher` 做最终质检