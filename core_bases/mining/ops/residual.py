# -*- coding: utf-8 -*-
"""已有预报残差的分位。不训练，不回灌。"""
from __future__ import annotations

import numpy as np
import pandas as pd


def strata_quantiles(values: pd.Series) -> dict:
    v = pd.Series(values).dropna().to_numpy(float)
    if len(v) == 0:
        return {"n": 0, "p10": None, "p50": None, "p90": None}
    q = np.quantile(v, [0.1, 0.5, 0.9])
    return {"n": int(len(v)), "p10": float(q[0]), "p50": float(q[1]), "p90": float(q[2])}
