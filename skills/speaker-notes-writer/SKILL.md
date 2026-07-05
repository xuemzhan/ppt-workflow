---
name: speaker-notes-writer
description: "讲稿撰写器——为每页幻灯片撰写讲稿、页间转场句、总时长控制。输入 deck_final.pptx(或 outline),输出 speaker_notes.md,并自动写入 PPTX 的演讲者备注。触发词:演讲稿、speaker notes、讲稿生成、备注生成、转场句、PPT 备注。"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ppt, speaker notes, transcript, presentation, deck, presenter]
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



# 讲稿撰写器 (speaker-notes-writer)

> "光有 PPT 不够,演讲时还得知道每页该说什么、转场怎么过渡、大概用时多久。"

## 一、目标

为已成型的 deck 生成三类讲稿内容:

1. **每页讲稿** —— 演讲者在该页要说的完整内容
2. **页间转场句** —— 从第 N 页跳到第 N+1 页的过渡话术
3. **总时长控制** —— 每页建议时长、总时长

输出 `speaker_notes.md`,同时自动写入 PPTX 的演讲者备注栏。

## 二、何时使用

- 演示前 1-2 小时,需要熟悉讲稿
- 演讲给陌生受众,需要精确措辞
- 受众时间有限(15 分钟报告),需要控制时长

## 三、讲稿撰写规范

### 1. 讲稿不是念 PPT

❌ 念 PPT:"这一页我们看到三个要点,第一,第二,第三"
✅ 讲稿:"在分析了 12 个场景后,我们聚焦到三个核心痛点。第一,检索效率——平均每天浪费 30 分钟..."

讲稿是**补充信息 + 故事 + 衔接**,而不是念标题。

### 2. 三段式讲稿结构(每页)

| 段 | 作用 | 时长占比 |
|----|------|----------|
| **承接**(2-3 句) | 回应上一页/制造连接 | 20% |
| **展开**(主体) | 阐述本页核心信息、举例、数据 | 60% |
| **落地**(1-2 句) | 给出本节小结,引出下一页 | 20% |

### 3. 时长估算

中文演讲参考速度:**150-180 字/分钟**。

```
页面讲稿字数 / 165 ≈ 页面时长(分钟)
```

总时长 = 所有页面时长之和 + Q&A 时长。

### 4. 转场句模板

| 类型 | 模板 |
|------|------|
| 因果 | "既然 [本页结论],那么 [下一页要解决的问题]" |
| 转折 | "然而,故事还有另一个侧面。" |
| 放大 | "把视角拉远一点,这件事的影响其实是..." |
| 收束 | "以上三点归结到一个判断..." |
| 钩子 | "不过,有一个关键变量我们还没讨论。" |
| 时间 | "我们先放下 X,聊一下 Y 在 2024 年的变化..." |
| 对比 | "我们刚才看的是 [页 A],换个角度看 [页 B]..." |
| 案例 | "这个判断在我们最近的一个项目里得到了验证。" |

## 四、操作规程

### Step 1: 读取 deck

```bash
python scripts/extract_text.py deck_final.pptx > slides_text.txt
```

或读取 outline.md / slides.md。

### Step 2: 撰写讲稿

按页面顺序,逐页撰写三段式讲稿 + 转场句。

### Step 3: 估算时长

按字数 / 165 计算。

### Step 4: 输出

保存为 `speaker_notes.md`,并写入 PPTX 的演讲者备注。

## 五、配套脚本

### `scripts/notes_to_pptx.py`

把讲稿 md 文件嵌入 PPTX 的演讲者备注栏。

```python
#!/usr/bin/env python3
"""
把 speaker_notes.md 写入 PPTX 的演讲者备注栏。

speaker_notes.md 格式:
    ## 页 1: <标题>
    **承接**: ...
    **展开**: ...
    **落地**: ...
    **转场到下一页**: ...
    **时长**: 1.5 分钟

    ## 页 2: ...
"""
import re
import sys
from pathlib import Path

from pptx import Presentation


SECTION_PATTERN = re.compile(r"^##\s+页\s+(\d+):\s*(.+)$", re.MULTILINE)


def parse_notes(md_text):
    """解析 speaker_notes.md → dict[page_num, content]"""
    sections = SECTION_PATTERN.split(md_text)
    notes = {}
    for i in range(1, len(sections), 3):
        page_num = int(sections[i])
        title = sections[i + 1].strip()
        body = sections[i + 2].strip() if i + 2 < len(sections) else ""
        notes[page_num] = {"title": title, "body": body}
    return notes


def main():
    if len(sys.argv) < 3:
        print("用法: notes_to_pptx.py <deck.pptx> <notes.md> <output.pptx>")
        sys.exit(1)
    deck_path = Path(sys.argv[1])
    notes_path = Path(sys.argv[2])
    out_path = Path(sys.argv[3]) if len(sys.argv) >= 4 else deck_path

    notes = parse_notes(notes_path.read_text(encoding="utf-8"))
    prs = Presentation(str(deck_path))

    for idx, slide in enumerate(prs.slides, 1):
        if idx in notes:
            slide.notes_slide.notes_text_frame.text = notes[idx]["body"]
            print(f"  页 {idx}:已写入备注")

    prs.save(str(out_path))
    print(f"已写入备注到:{out_path}")


if __name__ == "__main__":
    main()
```

### `scripts/estimate_duration.py`

```python
#!/usr/bin/env python3
"""
估算演讲时长(基于 speaker_notes.md 或 deck.pptx 的备注)

用法:
    estimate_duration.py notes.md
    estimate_duration.py deck.pptx
"""
import re
import sys
from pathlib import Path


def estimate_from_md(md_path):
    text = Path(md_path).read_text(encoding="utf-8")
    sections = re.split(r"^##\s+页\s+\d+:", text, flags=re.MULTILINE)
    sections = [s for s in sections if s.strip()]
    total = 0.0
    print(f"{'页':<4} {'字数':<8} {'时长(分钟)':<10}")
    print("-" * 30)
    for i, sec in enumerate(sections, 1):
        # 去掉 markdown 标记后算字符
        clean = re.sub(r"[*#>_-]+", "", sec)
        cn_chars = len(re.findall(r"[\u4e00-\u9fff]", clean))
        en_words = len(re.findall(r"\b[a-zA-Z]+\b", clean))
        equiv = cn_chars + en_words * 0.6
        minutes = equiv / 165
        total += minutes
        print(f"{i:<4} {int(equiv):<8} {minutes:.2f}")
    print("-" * 30)
    print(f"总时长:{total:.2f} 分钟(不含 Q&A)")
    return total


def estimate_from_pptx(pptx_path):
    from pptx import Presentation
    prs = Presentation(str(pptx_path))
    total = 0.0
    print(f"{'页':<4} {'字数':<8} {'时长(分钟)':<10}")
    print("-" * 30)
    for i, slide in enumerate(prs.slides, 1):
        notes = ""
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text
        clean = re.sub(r"[*#>_-]+", "", notes)
        cn = len(re.findall(r"[\u4e00-\u9fff]", clean))
        en = len(re.findall(r"\b[a-zA-Z]+\b", clean))
        equiv = cn + en * 0.6
        minutes = equiv / 165
        total += minutes
        print(f"{i:<4} {int(equiv):<8} {minutes:.2f}")
    print("-" * 30)
    print(f"总时长:{total:.2f} 分钟(不含 Q&A)")
    return total


def main():
    if len(sys.argv) < 2:
        print("用法: estimate_duration.py <notes.md|deck.pptx>")
        sys.exit(1)
    path = Path(sys.argv[1])
    if path.suffix == ".md":
        estimate_from_md(path)
    elif path.suffix == ".pptx":
        estimate_from_pptx(path)
    else:
        print("不支持的文件类型")


if __name__ == "__main__":
    main()
```

## 六、模板:speaker_notes_template.md

```markdown
# <主题> — 演讲稿

> 受众:<受众>
> 预计时长:<N> 分钟
> 演讲者:<姓名>

---

## 页 1: 封面
**承接**: 大家好,今天汇报的主题是 <主题>。
**展开**: 这份汇报的结论可以一句话概括:**<核心论点>**。我将从 <N 个方面> 展开,大约用 <N 分钟>。
**落地**: 首先,我想从背景说起。
**时长**: 0.5 分钟

---

## 页 2: 背景
**承接**: 在开始之前,先交代一下背景。
**展开**: <2-3 句话展开本页背景,可以补充 PPT 上没有的数据、个人经历、行业观察>
**落地**: 这就是为什么今天要讲这个主题。
**时长**: 1.5 分钟

---

## 页 3: <页面主题>
**承接**: <承接上一页>
**展开**: <本页核心>
**落地**: <本节小结 + 引导下一页>
**转场到下一页**: "<具体转场话术>"
**时长**: X 分钟

(更多页...)
```

## 七、风险评估

🟢 **低风险** —— 只读 deck,生成/写入文本备注。

## 八、与上下 Skill 的衔接

- **上游**: 任何已生成的 deck / outline
- **下游**: `deck-review-publisher` 在最终质检时,会一并检查讲稿完整性