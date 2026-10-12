# -*- coding: utf-8 -*-
"""路径与产品配置。系数只从 config/product.json 读取。"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2]
SLOT_ROOT = Path("/Users/liuyubin/Documents/中化/single_tower_slot")
OUTPUTS = SLOT_ROOT / "phase3_delta_2h" / "outputs"
XINBAO_FRU2H = SLOT_ROOT / "xinbao-ai-product-purity-main" / "XGBoost_1h_mean_var_fru_2h"
FACTORY_DATA = Path("/Users/liuyubin/Documents/中化/AI揭榜/资料")
CONFIG_PATH = APP_ROOT / "config" / "product.json"
DATA_DIR = APP_ROOT / "data"
DB_PATH = DATA_DIR / "factory.db"
REALTIME_CACHE = DATA_DIR / "realtime_cache.pkl"
SCORE_JSON = OUTPUTS / "line_scores.json"
MINING_JSON = OUTPUTS / "mining_last.json"

ACCEPTANCE_NAME = "regime_daily_pred.pkl"
DATASET_NAME = "official_fru2h_dataset.pkl"
REALTIME_CACHE_NAME = "realtime_cache.pkl"
FROZEN_NAMES = {ACCEPTANCE_NAME, DATASET_NAME}


@lru_cache(maxsize=1)
def load_config() -> dict:
    """读取唯一配置。缺少文件时直接失败，不在代码里补系数。"""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("缺少产品配置: %s" % CONFIG_PATH)
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def config_version() -> str:
    """配置版本号。"""
    return str(load_config().get("version") or "")
