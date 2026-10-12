# -*- coding: utf-8 -*-
"""离散测点温差的汇总。异常上限不在正式配置里。"""
from __future__ import annotations

import pandas as pd


def summarize_gap(diff: pd.Series) -> dict:
    s = pd.Series(diff).dropna()
    if s.empty:
        return {"n": 0, "median": None, "p10": None, "p90": None}
    return {
        "n": int(len(s)),
        "median": float(s.median()),
        "p10": float(s.quantile(0.1)),
        "p90": float(s.quantile(0.9)),
    }
