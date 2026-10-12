# -*- coding: utf-8 -*-
"""离线快照。实时缓存是另一个文件，不写进这张表。"""
from __future__ import annotations

import pandas as pd

from core_bases.dataset.config import DATASET_NAME, OUTPUTS, REALTIME_CACHE_NAME
from core_bases.dataset.official import load_official

SNAPSHOT = OUTPUTS / DATASET_NAME
_SNAP = None
_API = None


def _api() -> dict:
    global _API
    if _API is None:
        _API = load_official()
    return _API


def time_column() -> str:
    """官方时间列名。"""
    return _api()["tc"]


def target_column() -> str:
    """到达时刻近红外目标列名。"""
    return _api()["target"]


def split() -> dict:
    """官方训练起点和验收窗。"""
    cfg = _api()["cfg"]["split"]
    return {
        "train_start": str(cfg["train_start"]),
        "test_start": str(cfg["test_start"]),
        "test_end": str(cfg["test_end"]),
    }


def load_snapshot() -> pd.DataFrame:
    """读取冻结快照。进程内缓存，不改文件。"""
    global _SNAP
    if _SNAP is None:
        tc = time_column()
        frame = pd.read_pickle(SNAPSHOT)
        frame[tc] = pd.to_datetime(frame[tc])
        _SNAP = frame.sort_values(tc).drop_duplicates(tc).reset_index(drop=True)
    return _SNAP


def acceptance_bounds():
    """验收窗左闭右开。"""
    spec = split()
    return pd.Timestamp(spec["test_start"]), pd.Timestamp(spec["test_end"])


def describe() -> dict:
    """快照行数、时间范围和验收窗。不读取实时缓存。"""
    frame = load_snapshot()
    tc = time_column()
    spec = split()
    t0, t1 = acceptance_bounds()
    inside = frame[(frame[tc] >= t0) & (frame[tc] < t1)]
    return {
        "snapshot": DATASET_NAME,
        "frozen": True,
        "n_rows": int(len(frame)),
        "time_min": pd.Timestamp(frame[tc].min()).strftime("%Y-%m-%d %H:%M:%S"),
        "time_max": pd.Timestamp(frame[tc].max()).strftime("%Y-%m-%d %H:%M:%S"),
        "train_start": spec["train_start"],
        "acceptance": {
            "start": spec["test_start"],
            "end": spec["test_end"],
            "grain": "5 min",
            "rows_in_snapshot": int(len(inside)),
            "purpose": "验收计分。实时缓存不进入这里。",
        },
        "chart": {"grain": "15 min", "purpose": "只用于画图，不替代验收计分。"},
        "realtime_cache": REALTIME_CACHE_NAME,
        "online_marks": ["steady", "nir_jump", "nir_slow", "step"],
        "online_rule": "在线只跑这四个已有标记，不重估阈值，不把实时点写进离线快照。",
    }
