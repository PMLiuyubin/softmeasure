# -*- coding: utf-8 -*-
"""实时入口。只追加单独缓存，不改离线快照，不改验收预报，不训练。

列名与离线表一致。只调用 operators.light 里已开放的四个标记，不调用 fit_*。
标记保持算子原值，不收成有效、可疑或无效，也不用来隐藏黄线或蓝线。
粉线在回流和侧线都有数时计算。黄线、蓝线只在该时刻已有绿线预报时计算，否则留空。
绿、紫、青、橙只读已有预报文件。逐点推理开关默认关闭。
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from core_bases.dataset.config import REALTIME_CACHE
from core_bases.dataset.guard import assert_not_frozen
from core_bases.dataset.config import load_config
from core_bases.dataset.marks.nir_mark import mark_nir_jump, mark_nir_slow, slow_rolling
from core_bases.dataset.marks.steady import mark_steady
from core_bases.dataset.marks.step_mark import mark_steps
from core_bases.predict.engine import forecast

CACHE = REALTIME_CACHE
RETAIN_DAYS = 7
TIME = "时间"
NIR = "JJN_当时"
TAGS = {
    "F": "2770_FT21101.VALUE_当前值",
    "R": "2770_FT21102.VALUE_当前值",
    "S": "2770_FT21103.VALUE_当前值",
    "D": "2770_FT21105.VALUE_当前值",
    "Ttop": "2770_TE21104.VALUE_当前值",
    "Tside": "2770_TE21105.VALUE_当前值",
    "Tbot": "2770_TE21108.VALUE_当前值",
}
SHORT = {
    "t": TIME,
    "time": TIME,
    "时间": TIME,
    "nir": NIR,
    "JJN_当时": NIR,
    "F": TAGS["F"],
    "R": TAGS["R"],
    "S": TAGS["S"],
    "D": TAGS["D"],
    "Ttop": TAGS["Ttop"],
    "Tside": TAGS["Tside"],
    "Tbot": TAGS["Tbot"],
}
ALLOWED = {TIME, NIR, *TAGS.values()}
MARK_COLS = ["steady", "nir_jump", "nir_slow", "step_F", "step_R", "step_S", "step_D"]
LINE_COLS = ["line1", "line2", "line3", "line4", "line5", "line6", "line7"]


def realtime_infer_enabled() -> bool:
    return bool(load_config().get("realtime_infer_enabled", False))


def _num(value):
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(out):
        return None
    return out


def _parse(row: dict) -> dict:
    mapped = {}
    for key, value in dict(row or {}).items():
        name = SHORT.get(key, key)
        if name in mapped and mapped[name] not in (None, ""):
            continue
        mapped[name] = value
    unknown = [k for k in mapped if k not in ALLOWED]
    if unknown:
        raise ValueError("列名不在离线表这套位号里: " + "、".join(unknown))
    if TIME not in mapped or mapped[TIME] in (None, ""):
        raise ValueError("需要时间")
    when = pd.Timestamp(mapped[TIME])
    if pd.isna(when):
        raise ValueError("时间无法识别")
    parsed = {"received_at": datetime.now().replace(microsecond=0), TIME: when, NIR: _num(mapped.get(NIR))}
    for col in TAGS.values():
        parsed[col] = _num(mapped.get(col))
    return parsed


def _load(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_pickle(path)
    frame[TIME] = pd.to_datetime(frame[TIME])
    return frame


def _trim(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    received = pd.to_datetime(frame["received_at"])
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=RETAIN_DAYS)
    keep = frame[received >= cutoff].copy()
    return keep.sort_values([TIME, "received_at"]).reset_index(drop=True)


def _last_bool(series: pd.Series, ready: bool):
    if not ready or series.empty:
        return None
    value = series.iloc[-1]
    if value is None or (isinstance(value, float) and not np.isfinite(value)) or pd.isna(value):
        return None
    return bool(value)


def _marks(frame: pd.DataFrame, when) -> dict:
    cfg = load_config()
    work = frame[frame[TIME] <= pd.Timestamp(when)].sort_values(TIME).copy()
    view = work.rename(columns={TIME: "time"})
    short = {name: col for name, col in TAGS.items() if view[col].notna().any()}
    renamed = view[["time", *short.values()]].rename(columns={v: k for k, v in short.items()})
    steady = None
    bins = int(view["time"].dt.floor("15min").nunique())
    if short and bins >= int(cfg["steady"]["min_points"]):
        _grid, mask, _thr = mark_steady(renamed, list(short), cfg["steady"]["thresholds"])
        if mask is not None and not mask.empty:
            prior = mask.loc[: view["time"].iloc[-1]]
            steady = None if prior.empty else bool(prior.iloc[-1])
    nir = view.set_index("time")[NIR].astype(float)
    diff = nir.diff()
    jump_ready = bool(np.isfinite(diff.iloc[-1])) if len(diff) else False
    nir_jump = _last_bool(mark_nir_jump(nir), jump_ready)
    roll = slow_rolling(nir)
    slow_ready = bool(np.isfinite(roll.iloc[-1])) if len(roll) else False
    nir_slow = _last_bool(mark_nir_slow(roll), slow_ready)
    steps = {}
    gap = float(cfg["step"]["min_gap_hours"])
    when = view["time"].iloc[-1]
    for name, col in TAGS.items():
        if name not in cfg["step"]["thresholds_tph"]:
            continue
        series = renamed.set_index("time")[name].astype(float) if name in renamed.columns else pd.Series(dtype=float)
        hit = None
        if series.notna().sum() >= 2:
            for ts, val in mark_steps(series.dropna(), float(cfg["step"]["thresholds_tph"][name]), gap):
                if pd.Timestamp(ts) == when:
                    hit = float(val)
        steps[name] = hit
    return {"steady": steady, "nir_jump": nir_jump, "nir_slow": nir_slow, "step": steps}


def _lines(parsed: dict) -> dict:
    return forecast(parsed[TIME], parsed[TAGS["R"]], parsed[TAGS["S"]], parsed[NIR])


def _jsonable(value):
    if value is None or value is pd.NaT:
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return pd.Timestamp(value).strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, (np.floating, float)):
        if not np.isfinite(value):
            return None
        return float(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def _public(row: dict, marks: dict, lines: dict) -> dict:
    return {
        "received_at": _jsonable(row["received_at"]),
        "时间": _jsonable(row[TIME]),
        NIR: _jsonable(row[NIR]),
        "tags": {name: _jsonable(row[TAGS[name]]) for name in TAGS},
        "marks": {
            "steady": marks["steady"],
            "nir_jump": marks["nir_jump"],
            "nir_slow": marks["nir_slow"],
            "step": marks["step"],
        },
        "lines": {key: _jsonable(lines[key]) for key in LINE_COLS},
        "retain_days": RETAIN_DAYS,
        "realtime_infer_enabled": False,
        "note": "标记保持算子原值。黄线和蓝线在没有已发出的绿线时留空。本点不进入验收计分。",
    }


def _store_row(parsed: dict, marks: dict, lines: dict) -> dict:
    row = dict(parsed)
    row["steady"] = marks["steady"]
    row["nir_jump"] = marks["nir_jump"]
    row["nir_slow"] = marks["nir_slow"]
    for name, val in marks["step"].items():
        row["step_" + name] = val
    row.update(lines)
    return row


def accept_point(row: dict, cache_path: Path | None = None) -> dict:
    if realtime_infer_enabled():
        raise RuntimeError("逐点推理未接入。realtime_infer_enabled 保持关闭，预报只读已有文件。")
    path = Path(cache_path) if cache_path else CACHE
    meta = path.with_name(path.stem + "_meta.json")
    assert_not_frozen(path)
    assert_not_frozen(meta)
    parsed = _parse(row)
    frame = _trim(_load(path))
    if not frame.empty:
        frame = frame[frame[TIME] != parsed[TIME]]
    marks = _marks(pd.concat([frame, pd.DataFrame([parsed])], ignore_index=True), parsed[TIME])
    lines = _lines(parsed)
    stored = _store_row(parsed, marks, lines)
    frame = _trim(pd.concat([frame, pd.DataFrame([stored])], ignore_index=True))
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_pickle(path)
    meta.write_text(json.dumps({
        "retain_days": RETAIN_DAYS,
        "realtime_infer_enabled": False,
        "marks": ["steady", "nir_jump", "nir_slow", "step"],
        "mark_note": "标记保持算子原值，不收成有效、可疑或无效，也不用来藏线。",
        "score_note": "本缓存按写入时间保留 7 天，不进入验收计分，不写入离线快照和验收预报。",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return _public(stored, marks, lines)


def recent(limit: int = 20, cache_path: Path | None = None) -> dict:
    path = Path(cache_path) if cache_path else CACHE
    frame = _load(path)
    items = []
    if not frame.empty:
        view = frame.sort_values([TIME, "received_at"]).tail(int(limit))
        for rec in view.to_dict(orient="records"):
            items.append({
                "received_at": _jsonable(rec.get("received_at")),
                "时间": _jsonable(rec.get(TIME)),
                "steady": None if pd.isna(rec.get("steady")) else bool(rec.get("steady")),
                "nir_jump": None if pd.isna(rec.get("nir_jump")) else bool(rec.get("nir_jump")),
                "nir_slow": None if pd.isna(rec.get("nir_slow")) else bool(rec.get("nir_slow")),
                "step": {name: _jsonable(rec.get("step_" + name)) for name in ("F", "R", "S", "D")},
                "lines": {key: _jsonable(rec.get(key)) for key in LINE_COLS},
            })
    return {
        "items": items,
        "retain_days": RETAIN_DAYS,
        "realtime_infer_enabled": realtime_infer_enabled(),
    }
