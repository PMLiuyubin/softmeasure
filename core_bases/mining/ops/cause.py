# -*- coding: utf-8 -*-
"""根因只列候选。不认定，不进模型。"""
from __future__ import annotations


def list_candidates(residual_big: bool, unsteady: bool, nir_jump: bool, valve_sat: bool) -> list:
    out = []
    if valve_sat:
        out.append("阀饱和（只有连续阀位时才能列入）")
    if nir_jump:
        out.append("含量列跳变（待核对，不直接写成仪表故障）")
    if unsteady:
        out.append("该时刻流量或塔温波动偏大")
    if residual_big and not out:
        out.append("残差偏大，但没有足够的标记可列候选")
    if not out:
        out.append("无候选")
    return out
