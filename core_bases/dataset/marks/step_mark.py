# -*- coding: utf-8 -*-
"""流量阶跃判定。路径汇总不在这里。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from core_bases.dataset.config import load_config


def fit_step_threshold(series: pd.Series) -> float | None:
    q = float(load_config()["step"]["quantile"])
    valid = series.diff().dropna()
    if len(valid) < 50:
        return None
    return float(valid.abs().quantile(q))


def mark_steps(series: pd.Series, threshold: float, min_gap_hours: float | None = None) -> list:
    """返回 (时刻, 差分) 。同一序列在最小间隔内只留一次。"""
    gap = float(load_config()["step"]["min_gap_hours"] if min_gap_hours is None else min_gap_hours)
    dx = series.diff()
    hits = []
    last = None
    span = pd.Timedelta(hours=gap)
    for ts, val in dx.items():
        if not np.isfinite(val) or abs(float(val)) < float(threshold):
            continue
        if last is not None and (ts - last) < span:
            continue
        last = ts
        hits.append((ts, float(val)))
    return hits
