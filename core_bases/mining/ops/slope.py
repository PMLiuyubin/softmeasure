# -*- coding: utf-8 -*-
"""回流、侧线对含量的联合斜率。不改锁定式。"""
from __future__ import annotations

import numpy as np

from core_bases.dataset.config import load_config


def fit_partial_slopes(y, reflux, side) -> dict | None:
    y = np.asarray(y, float)
    if len(y) < 20:
        return None
    ref = load_config()["slope_reference"]
    x = np.column_stack([
        np.ones(len(y)),
        np.asarray(reflux, float) - float(ref["R0"]),
        np.asarray(side, float) - float(ref["S0"]),
    ])
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    resid = y - x @ beta
    dof = len(y) - 3
    se = None
    if dof >= 5:
        try:
            cov = (float(np.dot(resid, resid)) / dof) * np.linalg.inv(x.T @ x)
            se = np.sqrt(np.diag(cov))
        except np.linalg.LinAlgError:
            se = None
    return {
        "n": int(len(y)),
        "intercept": float(beta[0]),
        "reflux": float(beta[1]),
        "side": float(beta[2]),
        "se_reflux": None if se is None else float(se[1]),
        "se_side": None if se is None else float(se[2]),
        "lock_reflux": float(ref["lock_R"]),
        "lock_side": float(ref["lock_S"]),
        "lock_base": float(ref["lock_base"]),
    }
