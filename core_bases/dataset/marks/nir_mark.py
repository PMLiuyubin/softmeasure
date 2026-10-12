# -*- coding: utf-8 -*-
"""侧线近红外含量列的跳变和慢变。中心和跳变阈值读配置。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from core_bases.dataset.config import load_config


def _nir_cfg() -> dict:
    return load_config()["nir_content"]


def fit_nir_levels(nir: pd.Series) -> dict:
    cfg = _nir_cfg()
    g = nir.resample(f"{int(load_config()['grid_minutes'])}min").median().dropna()
    d = g.diff().dropna()
    return {
        "center_pct": float(g.median()),
        "jump_abs_pct": float(d.abs().quantile(float(cfg["jump_quantile"]))),
    }


def mark_nir_slow(rolling_median: pd.Series, center: float | None = None, band: float | None = None) -> pd.Series:
    cfg = _nir_cfg()
    c = float(cfg["center_pct"] if center is None else center)
    b = float(cfg["slow_band_pct"] if band is None else band)
    return (rolling_median - c).abs().gt(b)


def mark_nir_jump(values: pd.Series, jump_abs: float | None = None) -> pd.Series:
    cfg = _nir_cfg()
    thr = float(cfg["jump_abs_pct"] if jump_abs is None else jump_abs)
    return values.diff().abs().ge(thr)


def slow_rolling(values: pd.Series) -> pd.Series:
    n = int(_nir_cfg()["slow_window_points"])
    return values.rolling(n, min_periods=max(2, n // 2)).median()
