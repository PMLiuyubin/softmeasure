# -*- coding: utf-8 -*-
from __future__ import annotations

import numpy as np

from core_bases.mining.ops.xcorr import pearson
from core_bases.dataset.config import load_config


def pair_corr(a: np.ndarray, b: np.ndarray) -> dict:
    r, n = pearson(a, b)
    weak = r is None or abs(r) < float(load_config()["xcorr"]["clear_abs_r"])
    return {"r": r, "n": n, "weak": weak}
