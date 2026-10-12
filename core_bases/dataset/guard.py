# -*- coding: utf-8 -*-
"""冻结文件保护。实时缓存和实验输出不得覆盖快照或验收预报。"""
from __future__ import annotations

from pathlib import Path

from core_bases.dataset.config import ACCEPTANCE_NAME, FROZEN_NAMES


def assert_not_acceptance(path) -> None:
    """拒绝写入验收预报文件。"""
    if Path(path).name == ACCEPTANCE_NAME:
        raise RuntimeError("不得写入验收预报 regime_daily_pred.pkl")


def assert_not_frozen(path) -> None:
    """拒绝写入离线快照或验收预报。"""
    if Path(path).name in FROZEN_NAMES:
        raise RuntimeError("不得写入离线快照或验收预报")
