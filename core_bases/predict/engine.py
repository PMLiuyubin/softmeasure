# -*- coding: utf-8 -*-
"""七条线签发。逐点推理默认关闭。"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from core_bases.dataset.config import OUTPUTS, load_config
from core_bases.mechanism.formula import blue, lock_mn, yellow
from core_bases.predict.catalog import CATALOG
from core_bases.predict.issued import line1_at, line5_at, line6_at, line7_at

FEATURE_META = OUTPUTS / "official_fru2h_meta.json"
R_COL = "2770_FT21102.VALUE_当前值"
S_COL = "2770_FT21103.VALUE_当前值"
NIR = "JJN_当时"
_FRAME = None


def realtime_infer_enabled() -> bool:
    """逐点推理开关。配置缺省为关闭。"""
    return bool(load_config().get("realtime_infer_enabled", False))


def live_status() -> dict:
    """说明当前没有加载权重文件。"""
    n_feat = None
    if FEATURE_META.exists():
        n_feat = len(json.loads(FEATURE_META.read_text(encoding="utf-8"))["feature_columns"])
    return {
        "enabled": realtime_infer_enabled(),
        "armed": False,
        "feature_columns": n_feat,
        "reason": "逐点推理开关关闭。绿线和实验权重只读已签发的预报文件，打开页面不训练。",
    }


def forecast(when, reflux, side, nir, green=None) -> dict:
    """组装一个时刻的七条线。推理开关打开时拒绝计算。"""
    if realtime_infer_enabled():
        raise RuntimeError("逐点推理未接入。开关保持关闭，预报只读已签发文件。")
    if green is None and when is not None:
        green = line1_at(when)
    pink = lock_mn(reflux, side) if None not in (reflux, side) else None
    return {
        "line1": None if green is None else float(green),
        "line2": yellow(nir, green, reflux, side),
        "line3": pink,
        "line4": blue(green, pink),
        "line5": line5_at(when) if when is not None else None,
        "line6": line6_at(when) if when is not None else None,
        "line7": line7_at(when) if when is not None else None,
    }


def acceptance_frame() -> pd.DataFrame:
    """验收窗上的到达近红外和七条预报。不读实时缓存。"""
    global _FRAME
    if _FRAME is not None:
        return _FRAME
    from core_bases.dataset.config import REALTIME_CACHE_NAME
    from core_bases.dataset.snapshot import acceptance_bounds, load_snapshot, target_column, time_column

    reads = (
        "official_fru2h_dataset.pkl",
        "regime_daily_pred.pkl",
        "xgb_lock_feature_pred.pkl",
        "xgb_resid_on_lock_pred.pkl",
        "xgb_resid_sim_pid_pred.pkl",
    )
    if REALTIME_CACHE_NAME in reads:
        raise RuntimeError("验收计分不得读取实时缓存")
    tc = time_column()
    target = target_column()

    def _pred(name, key):
        frame = pd.read_pickle(OUTPUTS / name)
        if tc not in frame.columns and "时间" in frame.columns:
            frame = frame.rename(columns={"时间": tc})
        frame[tc] = pd.to_datetime(frame[tc])
        return frame.rename(columns={"pred": key})[[tc, key]]

    merged = _pred("xgb_lock_feature_pred.pkl", "line5")
    for key, name in (
        ("line1", "regime_daily_pred.pkl"),
        ("line6", "xgb_resid_on_lock_pred.pkl"),
        ("line7", "xgb_resid_sim_pid_pred.pkl"),
    ):
        merged = merged.merge(_pred(name, key), on=tc, how="inner")
    feat = load_snapshot()[[tc, NIR, R_COL, S_COL, target]].rename(columns={target: "y"})
    merged = merged.merge(feat, on=tc, how="inner")
    t0, t1 = acceptance_bounds()
    table = merged[(merged[tc] >= t0) & (merged[tc] < t1)].dropna().reset_index(drop=True)
    y = table["y"].to_numpy(float)
    green = table["line1"].to_numpy(float)
    pink = np.array([lock_mn(r, s) for r, s in zip(table[R_COL], table[S_COL])], float)
    nir = table[NIR].to_numpy(float)
    table = table.copy()
    table["line2"] = pink + (green - nir)
    table["line3"] = pink
    table["line4"] = np.array([blue(g, p) for g, p in zip(green, pink)], float)
    _FRAME = table
    return table


def public() -> dict:
    """目录和推理状态。"""
    return {"catalog": [dict(item) for item in CATALOG], "live_infer": live_status()}
