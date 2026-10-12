# -*- coding: utf-8 -*-
"""在线四个标记。本包不导入 mining。"""
from __future__ import annotations

from core_bases.dataset.marks.nir_mark import mark_nir_jump, mark_nir_slow
from core_bases.dataset.marks.steady import mark_steady
from core_bases.dataset.marks.step_mark import mark_steps


def online_catalog() -> tuple:
    """实时链路允许调用的名字。阀位检测未开放。"""
    return ("mark_steady", "mark_nir_jump", "mark_nir_slow", "mark_steps")


__all__ = [
    "mark_steady",
    "mark_nir_jump",
    "mark_nir_slow",
    "mark_steps",
    "online_catalog",
]
