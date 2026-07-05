#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPT 工作流 - 一键体验 demo

不需要任何配置,运行本脚本即可走完完整流水线,
所有产物落在 examples/demo_output/ 目录。

用法:
    python examples/quickstart.py
"""
import shutil
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
INPUT = REPO / "examples" / "demo_input"
OUTPUT = REPO / "examples" / "demo_output"


def main():
    print("=" * 60)
    print("  PPT 工作流 - 一键体验")
    print("=" * 60)
    print(f"仓库:{REPO}")

    # 1. 准备输入(基于已有 sample_deck)
    src = REPO / "examples" / "sample_deck" / "input"
    if INPUT.exists():
        shutil.rmtree(INPUT)
    shutil.copytree(src, INPUT)
    # 删除中间调试文件
    for f in INPUT.glob("*.json"):
        if f.name != "slides.json":
            f.unlink()
    print(f"输入已就绪:{INPUT}")

    # 2. 清空旧产物
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)

    # 3. 跑流水线
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "orchestrate.py"),
        "--input", str(INPUT),
        "--output", str(OUTPUT),
    ]
    print(f"\n运行:{' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n❌ 流水线退出码 {result.returncode}")
        sys.exit(1)

    # 4. 展示产物
    print("\n" + "=" * 60)
    print("  产物清单")
    print("=" * 60)
    for f in sorted(OUTPUT.iterdir()):
        if f.is_file():
            size = f.stat().st_size
            print(f"  📄 {f.name:<30} {size:>10,} bytes")
        elif f.is_dir():
            for sub in sorted(f.iterdir()):
                if sub.is_file():
                    size = sub.stat().st_size
                    print(f"  📄 {f.name}/{sub.name:<25} {size:>10,} bytes")

    # 5. 显示 QA 报告摘要
    qa = OUTPUT / "qa_report.md"
    if qa.exists():
        print("\n" + "=" * 60)
        print("  QA 报告摘要")
        print("=" * 60)
        text = qa.read_text(encoding="utf-8-sig")
        # 只显示前 30 行
        for line in text.splitlines()[:30]:
            print(f"  {line}")
        if len(text.splitlines()) > 30:
            print(f"  ...(共 {len(text.splitlines())} 行)")

    print("\n" + "=" * 60)
    print("  体验完成!")
    print("  关键产物:")
    print(f"    - {OUTPUT / 'deck_final.pptx'}")
    print(f"    - {OUTPUT / 'speaker_notes.md'}")
    print(f"    - {OUTPUT / 'qa_report.md'}")
    print(f"    - {OUTPUT / 'thumbnails.jpg'}")
    print(f"    - {OUTPUT / 'charts'}/")
    print("\n  试用其他场景:把 examples/slides_template.json 复制到")
    print("  examples/demo_input/slides.json 改字段再跑。")
    print("=" * 60)


if __name__ == "__main__":
    main()