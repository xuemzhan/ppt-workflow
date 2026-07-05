#!/usr/bin/env python3
"""把 CSV 转成 chart_spec.json
用法: csv_to_chart_spec.py <input.csv> <chart_type> <title> <output.json>

CSV 格式:
    category,series1,series2
    华东,40,60
    华南,25,18
"""

# IMPORTANT: path setup must come BEFORE any skills.* imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

from skills.shared.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="把 CSV 转成 chart_spec.json")
    parser.add_argument("input", help="输入 CSV 文件路径")
    parser.add_argument(
        "chart_type", help="图表类型 (bar/line/pie/stacked_bar/grouped_bar/table)"
    )
    parser.add_argument("title", help="图表标题")
    parser.add_argument("output", help="输出 JSON 文件路径")
    args = parser.parse_args()
    csv_path = Path(args.input)
    ctype = args.chart_type
    title = args.title
    out_path = Path(args.output)

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    headers = rows[0]
    cats = [r[0] for r in rows[1:]]
    series = []
    for ci in range(1, len(headers)):
        vals = []
        for r in rows[1:]:
            try:
                vals.append(float(r[ci]))
            except ValueError:
                vals.append(0)
        series.append({"name": headers[ci], "values": vals})

    spec = {
        "type": ctype,
        "title": title,
        "data": {"categories": cats, "series": series},
    }
    out_path.write_text(
        json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info("已生成: %s", out_path)


if __name__ == "__main__":
    main()
