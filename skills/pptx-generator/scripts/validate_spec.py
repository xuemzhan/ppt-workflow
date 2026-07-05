#!/usr/bin/env python3
"""spec.json schema 验证器

检查 spec.json 是否符合 pptx-generator 期望的格式。
在 orchestrate 出错时(尤其是 spec_to_pptx.py 抛 KeyError)第一时间定位。

用法:
    python validate_spec.py <spec.json>

支持的 slide.type:
    title / section / bullet / two_column / three_column
    stat / quote / process / table / timeline / thank_you

退出码:
    0 = 通过
    1 = 有错误
"""

# IMPORTANT: path setup must come BEFORE any skills.* imports
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_PROJECT_ROOT = (
    _HERE.parent.parent.parent.parent
)  # scripts/<skill>/<name>.py → project root
sys.path.insert(0, str(_PROJECT_ROOT))

import argparse
import json
import logging

from skills.shared.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


VALID_TYPES = {
    "title",
    "section",
    "bullet",
    "two_column",
    "three_column",
    "stat",
    "quote",
    "process",
    "table",
    "timeline",
    "thank_you",
}


def validate(spec):
    errors = []
    warnings = []

    # 顶层
    if not isinstance(spec, dict):
        errors.append("spec 必须是 JSON 对象")
        return errors, warnings

    theme = spec.get("theme", {})
    if not isinstance(theme, dict):
        errors.append("theme 必须是对象")
    else:
        for color_key in ("primary_color", "secondary_color", "accent_color"):
            v = theme.get(color_key, "")
            if v and not (isinstance(v, str) and len(v) in (6, 7)):
                warnings.append(
                    f"theme.{color_key}={v!r} 不是 6 位 hex 颜色(可能不被识别)"
                )

    slides = spec.get("slides", [])
    if not isinstance(slides, list):
        errors.append("slides 必须是数组")
        return errors, warnings

    if len(slides) < 1:
        errors.append("slides 不能为空")

    for i, slide in enumerate(slides):
        prefix = f"slides[{i}]"
        if not isinstance(slide, dict):
            errors.append(f"{prefix} 必须是对象")
            continue

        stype = slide.get("type")
        if not stype:
            errors.append(f"{prefix} 缺少 type 字段")
            continue
        if stype not in VALID_TYPES:
            errors.append(
                f"{prefix}.type={stype!r} 不支持,有效类型:{', '.join(sorted(VALID_TYPES))}"
            )

        if "title" in slide and not isinstance(slide["title"], str):
            errors.append(f"{prefix}.title 必须是字符串")

        # 类型特定检查
        if stype == "bullet":
            if "bullets" not in slide:
                warnings.append(f"{prefix} 缺少 bullets(将显示空白)")
            elif not isinstance(slide["bullets"], list):
                errors.append(f"{prefix}.bullets 必须是数组")
        elif stype in ("two_column", "three_column"):
            for key in ("left", "right"):
                if key not in slide:
                    errors.append(f"{prefix} 缺少 {key} 字段")
                elif not isinstance(slide[key], dict):
                    errors.append(f"{prefix}.{key} 必须是对象")
        elif stype == "process":
            if "steps" not in slide:
                errors.append(f"{prefix} 缺少 steps 字段")
            elif not isinstance(slide["steps"], list) or len(slide["steps"]) == 0:
                errors.append(f"{prefix}.steps 必须是至少 1 项的数组")
        elif stype == "stat":
            if "stats" not in slide:
                errors.append(f"{prefix} 缺少 stats 字段")
            elif not isinstance(slide["stats"], list) or len(slide["stats"]) == 0:
                errors.append(f"{prefix}.stats 必须是至少 1 项的数组")
        elif stype == "table":
            headers = slide.get("headers", [])
            rows = slide.get("rows", [])
            if not rows and not headers:
                errors.append(f"{prefix} 缺少 headers/rows")
            elif headers and rows:
                n_cols = len(headers)
                bad = [i for i, r in enumerate(rows) if len(r) != n_cols]
                if bad:
                    errors.append(
                        f"{prefix}.rows 第 {bad} 行长度不等于 headers 长度({n_cols})"
                    )
        elif stype == "timeline":
            events = slide.get("events", [])
            if not events:
                errors.append(f"{prefix} 缺少 events")

    return errors, warnings


def main() -> None:
    parser = argparse.ArgumentParser(description="验证 spec.json 格式")
    parser.add_argument("spec", help="spec.json 文件路径")
    args = parser.parse_args()
    spec_path = Path(args.spec)
    if not spec_path.exists():
        logger.error("%s 不存在", spec_path)
        sys.exit(1)

    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        logger.exception("JSON 解析失败")
        sys.exit(1)

    errors, warnings = validate(spec)

    if errors:
        logger.error("%d 个错误:", len(errors))
        for e in errors:
            logger.error("  - %s", e)
    if warnings:
        logger.warning("%d 个警告:", len(warnings))
        for w in warnings:
            logger.warning("  - %s", w)
    if not errors and not warnings:
        logger.info("spec.json 验证通过 (%d 页)", len(spec.get("slides", [])))
        sys.exit(0)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
