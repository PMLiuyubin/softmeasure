# -*- coding: utf-8 -*-
"""决定系数和均方根。不读实时缓存，不改验收预报。"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score

from core_bases.dataset.config import SCORE_JSON
from core_bases.dataset.guard import assert_not_acceptance
from core_bases.dataset.snapshot import acceptance_bounds
from core_bases.predict.catalog import CATALOG
from core_bases.predict.engine import acceptance_frame

_CACHE = None


def _metric(y, p) -> dict:
    return {"R2": float(r2_score(y, p)), "RMSE": float(np.sqrt(mean_squared_error(y, p)))}


def score(write: bool = False) -> dict:
    """计算七条线在验收窗上的指标。默认不写文件。"""
    global _CACHE
    table = acceptance_frame()
    y = table["y"].to_numpy(float)
    lines = []
    for item in CATALOG:
        row = dict(item)
        row.update(_metric(y, table[item["id"]].to_numpy(float)))
        row["n"] = int(len(y))
        lines.append(row)
    t0, t1 = acceptance_bounds()
    payload = {
        "window": "%s 至 %s" % (t0.strftime("%Y-%m-%d"), (t1 - pd.Timedelta(days=1)).strftime("%Y-%m-%d")),
        "grain": "5 min",
        "n": int(len(y)),
        "ruler": "预报对照到达时刻近红外",
        "line6_line7_max_abs_diff": float(np.max(np.abs(table["line6"] - table["line7"]))),
        "lines": lines,
    }
    if write:
        assert_not_acceptance(SCORE_JSON)
        SCORE_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _CACHE = payload
    return payload


def load_or_score() -> dict:
    """优先用已落盘的计分，避免页面打开时重算。"""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if SCORE_JSON.exists():
        _CACHE = json.loads(SCORE_JSON.read_text(encoding="utf-8"))
        return _CACHE
    return score(write=False)
