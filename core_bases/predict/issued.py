# -*- coding: utf-8 -*-
"""按时刻读取已签发的预报文件。没有该时刻就返回空，不现训。"""
from __future__ import annotations

import pandas as pd

from core_bases.dataset.config import OUTPUTS

_CACHE: dict[str, pd.DataFrame] = {}


def _frame(name: str) -> pd.DataFrame | None:
    if name in _CACHE:
        return _CACHE[name]
    path = OUTPUTS / name
    if not path.exists():
        return None
    pred = pd.read_pickle(path)
    if "时间" not in pred.columns:
        return None
    pred = pred.copy()
    pred["时间"] = pd.to_datetime(pred["时间"])
    _CACHE[name] = pred
    return pred


def value_at(name: str, when) -> float | None:
    """读取一个预报文件在指定时刻的 pred。"""
    if when is None:
        return None
    pred = _frame(name)
    if pred is None:
        return None
    hit = pred.loc[pred["时间"] == pd.Timestamp(when), "pred"]
    if hit.empty:
        return None
    return float(hit.iloc[0])


def line1_at(when):
    return value_at("regime_daily_pred.pkl", when)


def line5_at(when):
    return value_at("xgb_lock_feature_pred.pkl", when)


def line6_at(when):
    return value_at("xgb_resid_on_lock_pred.pkl", when)


def line7_at(when):
    return value_at("xgb_resid_sim_pid_pred.pkl", when)
