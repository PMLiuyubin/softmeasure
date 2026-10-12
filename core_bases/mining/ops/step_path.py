# -*- coding: utf-8 -*-
"""阶跃之后的路径。判定用轻量算子，汇总只在离线做。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from core_bases.dataset.config import load_config
from core_bases.dataset.marks.step_mark import mark_steps


def step_path(series: pd.Series, target: pd.Series, threshold: float) -> dict | None:
    hits = mark_steps(series, threshold)
    if not hits and threshold is None:
        return None
    horizons = tuple(load_config()["step"]["path_horizons_min"])

    def one(sign: int) -> dict:
        chosen = [(ts, val) for ts, val in hits if np.sign(val) == sign]
        points = []
        for minutes in horizons:
            deltas = []
            for ts, _val in chosen:
                a = target.get(ts, np.nan)
                b = target.get(ts + pd.Timedelta(minutes=int(minutes)), np.nan)
                if np.isfinite(a) and np.isfinite(b):
                    deltas.append(float(b - a))
            med = float(np.median(deltas)) if len(deltas) >= 8 else None
            points.append({"minutes": int(minutes), "n": len(deltas), "median": med})
        return {"n": len(chosen), "path": points}

    return {"threshold": float(threshold), "n": len(hits), "up": one(1), "down": one(-1), "times": hits}
