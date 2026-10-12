# -*- coding: utf-8 -*-
"""差分互相关。需要整段序列，不进实时链路。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from core_bases.dataset.config import load_config


def pearson(a: np.ndarray, b: np.ndarray, min_pairs: int | None = None):
    cfg = load_config()["xcorr"]
    need = int(cfg["min_pairs"] if min_pairs is None else min_pairs)
    m = np.isfinite(a) & np.isfinite(b)
    n = int(m.sum())
    if n < need:
        return None, n
    x = a[m] - a[m].mean()
    y = b[m] - b[m].mean()
    den = float(np.sqrt(np.dot(x, x) * np.dot(y, y)))
    if den == 0:
        return None, n
    return float(np.dot(x, y) / den), n


def xcorr(x: pd.Series, y: pd.Series) -> dict | None:
    cfg = load_config()["xcorr"]
    step = int(cfg["step_min"])
    xmax = int(cfg["max_lag_min"])
    xv = x.to_numpy(float)
    rows = []
    for k, lag in enumerate(range(0, xmax + 1, step)):
        r, n = pearson(xv, y.shift(-k).to_numpy(float))
        rows.append({"lag": lag, "r": r, "n": n})
    usable = [row for row in rows if row["r"] is not None]
    if not usable:
        return None
    best = max(usable, key=lambda row: abs(row["r"]))
    zero = next(row for row in rows if row["lag"] == 0)
    gain = None if zero["r"] is None else abs(best["r"]) - abs(zero["r"])
    clear = (
        abs(best["r"]) >= float(cfg["clear_abs_r"])
        and best["lag"] >= int(cfg["clear_min_lag_min"])
        and gain is not None
        and gain >= float(cfg["clear_gain"])
    )
    return {"best": best, "zero": zero, "clear": clear}
