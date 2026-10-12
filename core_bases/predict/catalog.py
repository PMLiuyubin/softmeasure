# -*- coding: utf-8 -*-
"""七条线目录。"""
from __future__ import annotations

CATALOG = (
    {"id": "line1", "name": "近红外模型预测", "pool": "生产", "kind": "独立权重", "file": "regime_daily_pred.pkl", "default_on": True},
    {"id": "line2", "name": "线性关系式叠加预测增量", "pool": "实验", "kind": "引用绿线", "file": None, "default_on": False},
    {"id": "line3", "name": "回流侧线线性关系式", "pool": "实验", "kind": "代数，无权重", "file": None, "default_on": True},
    {"id": "line4", "name": "机理与预测后融合", "pool": "实验", "kind": "引用绿线", "file": None, "default_on": False},
    {"id": "line5", "name": "锁温特征模型", "pool": "实验", "kind": "独立权重", "file": "xgb_lock_feature_pred.pkl", "default_on": False},
    {"id": "line6", "name": "线性关系式加残差", "pool": "实验", "kind": "独立权重", "file": "xgb_resid_on_lock_pred.pkl", "default_on": False},
    {"id": "line7", "name": "残差加模拟PID", "pool": "实验", "kind": "独立权重", "file": "xgb_resid_sim_pid_pred.pkl", "default_on": False},
)
