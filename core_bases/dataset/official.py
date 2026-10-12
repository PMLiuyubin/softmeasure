# -*- coding: utf-8 -*-
"""只读挂载官方切分。不修改 xinbao 源码。"""
from __future__ import annotations

import sys

from core_bases.dataset.config import XINBAO_FRU2H


def load_official() -> dict:
    """返回官方时间列、目标列和切分配置。"""
    root = str(XINBAO_FRU2H.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    from src.config import PROJECT_ROOT, load_config
    from src.data_loader import CURRENT_JJN_COLUMN, MATCHED_NIR_TIME_COLUMN
    from src.dataset_builder import prepare_model_dataset
    from src.process_features import sample_weights_from_cfg
    from src.splits import iter_test_days, slice_test_day, slice_train

    cfg = load_config(PROJECT_ROOT)
    return {
        "project_root": PROJECT_ROOT,
        "cfg": cfg,
        "prepare_model_dataset": prepare_model_dataset,
        "slice_train": slice_train,
        "slice_test_day": slice_test_day,
        "iter_test_days": iter_test_days,
        "sample_weights_from_cfg": sample_weights_from_cfg,
        "CURRENT_JJN_COLUMN": CURRENT_JJN_COLUMN,
        "MATCHED_NIR_TIME_COLUMN": MATCHED_NIR_TIME_COLUMN,
        "tc": cfg["data"]["dcs_time_column"],
        "target": cfg["data"]["target_column"],
    }
