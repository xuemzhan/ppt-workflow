#!/usr/bin/env python3
"""用 LibreOffice 把 PPTX 转 PDF
用法: soffice_convert.py <input.pptx> <output.pdf>
"""

# IMPORTANT: path setup must come BEFORE any skills.* imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path

from skills.shared.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def find_soffice():
    candidates = ["soffice", "libreoffice"]
    for c in candidates:
        p = shutil.which(c)
        if p:
            return p
    win_paths = [
        "C:/Program Files/LibreOffice/program/soffice.exe",
        "C:/Program Files (x86)/LibreOffice/program/soffice.exe",
    ]
    for p in win_paths:
        if Path(p).exists():
            return p
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="用 LibreOffice 把 PPTX 转 PDF")
    parser.add_argument("input", help="输入 PPTX 文件路径")
    parser.add_argument("output", help="输出 PDF 文件路径")
    args = parser.parse_args()
    in_path = Path(args.input).resolve()
    out_path = Path(args.output).resolve()
    soffice = find_soffice()
    if not soffice:
        logger.error("找不到 LibreOffice。请安装 LibreOffice 或把 soffice 加入 PATH。")
        sys.exit(1)

    out_dir = out_path.parent
    cmd = [
        soffice,
        "--headless",
        "--norestore",
        "--nologo",
        "--convert-to",
        "pdf",
        "--outdir",
        str(out_dir),
        str(in_path),
    ]
    subprocess.run(cmd, check=True)
    pdf_name = in_path.stem + ".pdf"
    produced = out_dir / pdf_name
    if produced != out_path:
        shutil.move(str(produced), str(out_path))
    logger.info("已生成: %s", out_path)


if __name__ == "__main__":
    main()
