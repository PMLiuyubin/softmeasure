# -*- coding: utf-8 -*-
"""离线统计算子。"""
from core_bases.mining.ops.align import summarize_time_delta
from core_bases.mining.ops.covar import pair_corr
from core_bases.mining.ops.residual import strata_quantiles
from core_bases.mining.ops.slope import fit_partial_slopes
from core_bases.mining.ops.step_path import step_path
from core_bases.mining.ops.temp_profile import summarize_gap
from core_bases.mining.ops.xcorr import xcorr

__all__ = [
    "summarize_time_delta",
    "pair_corr",
    "strata_quantiles",
    "fit_partial_slopes",
    "step_path",
    "summarize_gap",
    "xcorr",
]
