# -*- coding: utf-8 -*-
"""阀位、静差、震荡。配置里 realtime_enabled 为 false 时，不进入在线目录。"""
from __future__ import annotations

import numpy as np

from core_bases.dataset.config import load_config


def realtime_enabled() -> bool:
    return bool(load_config()["pid"].get("realtime_enabled"))


def detect_pid(pv, sp, mv) -> dict:
    cfg = load_config()["pid"]
    err = np.abs(np.asarray(pv, float) - np.asarray(sp, float))
    mv = np.asarray(mv, float)
    sat = (mv >= float(cfg["sat_high"])) | (mv <= float(cfg["sat_low"]))
    run = 0
    sat_points = 0
    need = int(cfg["min_sat_points"])
    for flag in sat:
        if flag:
            run += 1
            if run == need:
                sat_points += need
            elif run > need:
                sat_points += 1
        else:
            run = 0
    d = np.diff(mv, prepend=mv[0])
    sign = np.sign(d)
    sign[np.abs(d) < float(cfg["osc_deadband"])] = 0
    win = int(cfg["osc_window_points"])
    flips = 0
    windows = 0
    for i in range(0, max(len(mv) - win, 0), win):
        windows += 1
        seg = sign[i:i + win]
        seg = seg[seg != 0]
        if len(seg) >= 2 and int(np.sum(seg[1:] * seg[:-1] < 0) >= int(cfg["osc_min_flips"])):
            flips += 1
    hours = float(cfg["point_hours"])
    return {
        "mean_abs": float(np.mean(err)) if len(err) else 0.0,
        "sat_h": float(sat_points) * hours,
        "osc_windows": int(flips),
        "n_windows": int(windows),
        "realtime_enabled": realtime_enabled(),
    }
