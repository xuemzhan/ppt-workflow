"""Pytest conftest:共享 fixtures 和路径常量"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SAMPLE_INPUT = REPO / "examples" / "sample_deck" / "input"
SAMPLE_OUTPUT = REPO / "examples" / "sample_deck" / "output"


@pytest.fixture
def ensure_clean_output():
    """在端到端测试前清空 SAMPLE_OUTPUT,避免陈旧产物干扰。"""
    if SAMPLE_OUTPUT.exists():
        shutil.rmtree(SAMPLE_OUTPUT)
    SAMPLE_OUTPUT.mkdir(parents=True, exist_ok=True)
    return SAMPLE_OUTPUT
