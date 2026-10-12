# -*- coding: utf-8 -*-
"""时间差 = 近红外时间减化验时间，单位分钟。"""
from __future__ import annotations

import pandas as pd


def summarize_time_delta(delta_minutes: pd.Series, within_min: float = 20) -> dict:
    ok = pd.Series(delta_minutes).dropna()
    if ok.empty:
        return {"n": 0, "median": None, "p10": None, "p90": None, "within": 0}
    return {
        "n": int(len(ok)),
        "median": float(ok.median()),
        "p10": float(ok.quantile(0.1)),
        "p90": float(ok.quantile(0.9)),
        "within": int((ok.abs() <= within_min).sum()),
    }
