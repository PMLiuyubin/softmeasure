# -*- coding: utf-8 -*-
"""波动小标记。阈值来自配置，函数内部不重新取中位。"""
from __future__ import annotations

import pandas as pd

from core_bases.dataset.config import load_config


def _grid(frame: pd.DataFrame, cols: list, minutes: int) -> pd.DataFrame:
    return frame.set_index("time").sort_index()[cols].resample(f"{int(minutes)}min").median()


def fit_steady_thresholds(frame: pd.DataFrame, cols: list) -> dict:
    """只在离线、故意重估时调用。结果要写回配置后，在线才能用。"""
    cfg = load_config()["steady"]
    g = _grid(frame, cols, load_config()["grid_minutes"])
    sd = g.rolling(int(cfg["window_points"]), min_periods=int(cfg["min_points"])).std()
    use = [c for c in cols if c in sd.columns and int(sd[c].notna().sum()) >= 30]
    med = sd[use].median()
    return {c: float(med[c]) for c in use}


def mark_steady(frame: pd.DataFrame, cols: list, thresholds: dict | None = None):
    """返回 15 分钟网格、波动小布尔序列、所用阈值。滚动窗口只看当前点及以前。"""
    cfg = load_config()
    st = cfg["steady"]
    level = dict(st["thresholds"] if thresholds is None else thresholds)
    use = [c for c in cols if c in frame.columns and c in level]
    if not use:
        return frame, None, None
    g = _grid(frame, use, cfg["grid_minutes"])
    sd = g.rolling(int(st["window_points"]), min_periods=int(st["min_points"])).std()
    thr = pd.Series({c: float(level[c]) for c in use})
    ok = sd[use].notna().all(axis=1) & sd[use].le(thr).all(axis=1)
    return g, ok.fillna(False), thr
