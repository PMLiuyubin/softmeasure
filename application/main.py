# -*- coding: utf-8 -*-
"""侧线软测量应用层。FastAPI。不导入 core_bases.mining。"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from application.bundle import bundle
from application.realtime import accept_point, recent
from core_bases.dataset.config import DB_PATH
from core_bases.dataset.snapshot import time_column
from core_bases.predict.engine import acceptance_frame, forecast

app = FastAPI(title="侧线软测量", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PointIn(BaseModel):
    """实时测点。未知列由实时入口拒绝。"""
    t: str | None = None
    time: str | None = None
    nir: float | None = None
    F: float | None = None
    R: float | None = None
    S: float | None = None
    D: float | None = None
    Ttop: float | None = None
    Tside: float | None = None
    Tbot: float | None = None

    model_config = {"extra": "allow"}


@app.get("/api/health")
def health():
    """服务健康。"""
    return {"ok": True, "database": DB_PATH.exists()}


@app.get("/api/foundation")
def foundation():
    """五块底座只读总览。"""
    return bundle()


@app.get("/api/compute/lines")
def lines(
    reflux: float = Query(...),
    side: float = Query(...),
    nir: float | None = Query(None),
    when: str | None = Query(None),
    green: float | None = Query(None),
):
    """按回流、侧线和时刻组装七条线。"""
    try:
        return forecast(when, reflux, side, nir, green=green)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/series")
def series(grain: int = Query(15)):
    """验收窗曲线。15 分钟只用于画图。数值全部由后端算出。"""
    frame = acceptance_frame()
    tc = time_column()
    view = frame
    if grain == 15:
        view = frame[frame[tc].dt.minute % 15 == 0]
    cols = ["line1", "line2", "line3", "line4", "line5", "line6", "line7", "y"]
    rows = []
    for rec in view[[tc, *cols]].to_dict(orient="records"):
        rows.append({
            "t": rec[tc].strftime("%Y-%m-%d %H:%M:%S"),
            "nir_arrival": float(rec["y"]),
            **{key: float(rec[key]) for key in cols if key != "y"},
        })
    return {"grain_min": grain, "n": len(rows), "rows": rows}


@app.get("/api/realtime/recent")
def realtime_recent(limit: int = 20):
    """最近写入的实时点。"""
    return recent(limit)


@app.post("/api/realtime/point")
def realtime_point(body: PointIn):
    """追加一个实时点到单独缓存。不写离线快照。"""
    try:
        return accept_point(body.model_dump(exclude_none=False))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/kb/health")
def kb_health():
    """知识库与工厂库是否已生成。"""
    return {"ok": True, "database": str(DB_PATH), "ready": DB_PATH.exists()}


@app.get("/api/kb/sources")
def kb_sources(limit: int = 50):
    """资料目录入库清单。"""
    if not DB_PATH.exists():
        return {"ready": False, "items": [], "note": "先运行 python -m application.ingest"}
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    items = [dict(row) for row in conn.execute(
        "SELECT id, relpath, suffix, bytes, n_rows, status, message FROM source_file ORDER BY id LIMIT ?",
        (int(limit),),
    )]
    total = conn.execute("SELECT COUNT(*) FROM source_file").fetchone()[0]
    loaded = conn.execute("SELECT COUNT(*) FROM source_file WHERE status = 'loaded'").fetchone()[0]
    conn.close()
    return {"ready": True, "total": total, "loaded": loaded, "items": items}
