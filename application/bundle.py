# -*- coding: utf-8 -*-
"""底座只读总览。本模块不导入 mining。"""
from __future__ import annotations

import json

from core_bases.dataset.config import MINING_JSON
from core_bases.dataset.snapshot import describe
from core_bases.evaluate.score import load_or_score
from core_bases.mechanism.formula import public as mechanism_public
from core_bases.predict.engine import public as predict_public


def mining_view() -> dict:
    """读取上次落盘的挖掘结果，不导入挖掘包。"""
    last = None
    if MINING_JSON.exists():
        last = json.loads(MINING_JSON.read_text(encoding="utf-8"))
    return {
        "offline_only": True,
        "imported_by_web": False,
        "last": last,
        "note": "在线服务不导入挖掘包。这里只读已落盘的报告。",
    }


def bundle() -> dict:
    """五块底座的只读包。挖掘段来自文件。"""
    return {
        "dataset": describe(),
        "mechanism": mechanism_public(),
        "predict": predict_public(),
        "evaluate": load_or_score(),
        "mining": mining_view(),
    }
