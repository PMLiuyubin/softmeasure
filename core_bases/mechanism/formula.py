# -*- coding: utf-8 -*-
"""回流侧线线性关系式。系数来自配置，函数不重估。"""
from __future__ import annotations

from core_bases.dataset.config import load_config


def coefficients() -> dict:
    """锁定系数。"""
    ref = load_config()["slope_reference"]
    return {
        "lock_base": float(ref["lock_base"]),
        "lock_R": float(ref["lock_R"]),
        "lock_S": float(ref["lock_S"]),
        "R0": float(ref["R0"]),
        "S0": float(ref["S0"]),
    }


def fusion_weights() -> tuple[float, float]:
    """模型外融合权重。"""
    cfg = load_config()["fusion"]
    return float(cfg["green"]), float(cfg["pink"])


def lock_mn(reflux: float, side: float) -> float:
    """由回流、侧线计算含量。"""
    c = coefficients()
    return c["lock_base"] + c["lock_R"] * (float(reflux) - c["R0"]) + c["lock_S"] * (float(side) - c["S0"])


def yellow(nir, green, reflux, side):
    """绿线增量加到锁温式上。缺任一输入则空。"""
    if None in (nir, green, reflux, side):
        return None
    return lock_mn(reflux, side) + (float(green) - float(nir))


def blue(green, pink):
    """绿线与锁温式在模型外加权。"""
    if None in (green, pink):
        return None
    wg, wp = fusion_weights()
    return wg * float(green) + wp * float(pink)


def public() -> dict:
    """给页面的公式说明。"""
    c = coefficients()
    wg, wp = fusion_weights()
    return {
        "name": "回流侧线线性关系式",
        "coefficients": c,
        "formula": "含量 = {lock_base} + {lock_R}×(回流 - {R0}) + ({lock_S})×(侧线 - {S0})".format(**c),
        "weights": "黄线、蓝线引用绿线的已签发预报。蓝线权重 %s / %s。" % (wg, wp),
    }
