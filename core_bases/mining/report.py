# -*- coding: utf-8 -*-
"""离线相关报告。在线接口不调用本模块。"""
from __future__ import annotations

import json

import numpy as np

from core_bases.dataset.config import MINING_JSON
from core_bases.dataset.snapshot import acceptance_bounds, load_snapshot, target_column, time_column
from core_bases.mining.ops.covar import pair_corr
from core_bases.predict.catalog import CATALOG

OPERATORS = (
    {"name": "pair_corr", "title": "差分相关", "where": "离线"},
    {"name": "xcorr", "title": "互相关", "where": "离线"},
    {"name": "strata_quantiles", "title": "残差分层", "where": "离线"},
    {"name": "fit_partial_slopes", "title": "偏斜率", "where": "离线"},
    {"name": "step_path", "title": "阶跃路径", "where": "离线"},
    {"name": "summarize_gap", "title": "温度剖面", "where": "离线"},
    {"name": "summarize_time_delta", "title": "时间差", "where": "离线"},
)


def build_report() -> dict:
    """验收窗上到达近红外与流量的一阶差分相关。结果另存，页面只读。"""
    tc = time_column()
    target = target_column()
    t0, t1 = acceptance_bounds()
    frame = load_snapshot()
    table = frame[(frame[tc] >= t0) & (frame[tc] < t1)].copy()
    y = table[target].to_numpy(float)
    pairs = []
    for title, col in (
        ("回流", "2770_FT21102.VALUE_当前值"),
        ("侧线", "2770_FT21103.VALUE_当前值"),
        ("进料", "2770_FT21101.VALUE_当前值"),
    ):
        x = table[col].to_numpy(float)
        ok = np.isfinite(y) & np.isfinite(x)
        stat = pair_corr(np.diff(y[ok]), np.diff(x[ok]))
        pairs.append({"with": title, "r": stat["r"], "n": stat["n"], "weak": stat["weak"]})
    payload = {
        "offline_only": True,
        "on": "验收窗到达近红外与流量的一阶差分",
        "pairs": pairs,
        "catalog_ids": [item["id"] for item in CATALOG],
        "note": "这是离线挖掘结果。打开页面不会重算。不进入预报，也不进入验收计分。",
    }
    MINING_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def last():
    """读取上次落盘的报告。"""
    if not MINING_JSON.exists():
        return None
    return json.loads(MINING_JSON.read_text(encoding="utf-8"))


def public() -> dict:
    """算子名单和上次结果。不在这里重算。"""
    return {"offline_only": True, "operators": [dict(item) for item in OPERATORS], "last": last()}
