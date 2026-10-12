# -*- coding: utf-8 -*-
"""把资料目录里能读成表的文件写入 SQLite。不改离线快照。"""
from __future__ import annotations

import sqlite3
import traceback
from datetime import datetime

import pandas as pd

from core_bases.dataset.config import DATA_DIR, DB_PATH, FACTORY_DATA, load_config
from core_bases.evaluate.score import load_or_score

TABULAR = {".csv", ".xlsx"}
TEXT = {".txt", ".log"}
SKIP_BODY = {".pdf", ".rar", ".docx", ".smg", ""}


def _read_table(path):
    suffix = path.suffix.lower()
    if suffix == ".csv":
        last = None
        for enc in ("utf-8", "gbk", "gb18030"):
            try:
                return {"csv": pd.read_csv(path, encoding=enc)}
            except Exception as exc:
                last = exc
        raise RuntimeError(str(last))
    if suffix == ".xlsx":
        book = pd.read_excel(path, sheet_name=None, engine="openpyxl")
        return book
    raise RuntimeError("不是表")


def _safe(name: str) -> str:
    out = []
    for ch in name:
        if ch.isalnum():
            out.append(ch.lower())
        else:
            out.append("_")
    text = "".join(out).strip("_")
    return text[:40] or "sheet"


def ingest() -> None:
    """扫描资料目录并入库。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE source_file (
            id INTEGER PRIMARY KEY,
            relpath TEXT NOT NULL,
            suffix TEXT NOT NULL,
            bytes INTEGER NOT NULL,
            n_rows INTEGER,
            status TEXT NOT NULL,
            message TEXT
        )"""
    )
    conn.execute(
        """CREATE TABLE source_text (
            file_id INTEGER PRIMARY KEY,
            body TEXT NOT NULL
        )"""
    )
    conn.execute(
        """CREATE TABLE coefficient (
            name TEXT PRIMARY KEY,
            value REAL NOT NULL
        )"""
    )
    conn.execute(
        """CREATE TABLE line_score (
            line_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            pool TEXT NOT NULL,
            n INTEGER NOT NULL,
            r2 REAL NOT NULL,
            rmse REAL NOT NULL
        )"""
    )
    conn.execute(
        """CREATE TABLE column_map (
            file_id INTEGER NOT NULL,
            sheet TEXT NOT NULL,
            ordinal INTEGER NOT NULL,
            original TEXT NOT NULL
        )"""
    )
    cfg = load_config()["slope_reference"]
    for key in ("lock_base", "lock_R", "lock_S", "R0", "S0"):
        conn.execute("INSERT INTO coefficient(name, value) VALUES (?, ?)", (key, float(cfg[key])))
    scored = load_or_score()
    for row in scored["lines"]:
        conn.execute(
            "INSERT INTO line_score(line_id, name, pool, n, r2, rmse) VALUES (?, ?, ?, ?, ?, ?)",
            (row["id"], row["name"], row["pool"], row["n"], row["R2"], row["RMSE"]),
        )
    files = [p for p in FACTORY_DATA.rglob("*") if p.is_file()]
    for path in files:
        rel = str(path.relative_to(FACTORY_DATA))
        suffix = path.suffix.lower()
        size = path.stat().st_size
        if path.name.startswith(".") or path.name.startswith("~$"):
            conn.execute(
                "INSERT INTO source_file(relpath, suffix, bytes, n_rows, status, message) VALUES (?, ?, ?, NULL, 'catalog', '临时文件，不入库')",
                (rel, suffix, size),
            )
            continue
        cur = conn.execute(
            "INSERT INTO source_file(relpath, suffix, bytes, n_rows, status, message) VALUES (?, ?, ?, NULL, 'pending', '')",
            (rel, suffix, size),
        )
        file_id = cur.lastrowid
        try:
            if suffix in TABULAR:
                sheets = _read_table(path)
                total = 0
                for sheet, frame in sheets.items():
                    if not isinstance(frame, pd.DataFrame) or frame.shape[1] == 0:
                        continue
                    frame = frame.copy()
                    originals = [str(c) for c in frame.columns]
                    frame.columns = ["c%d" % i for i in range(len(originals))]
                    for ordinal, original in enumerate(originals):
                        conn.execute(
                            "INSERT INTO column_map(file_id, sheet, ordinal, original) VALUES (?, ?, ?, ?)",
                            (file_id, str(sheet), ordinal, original),
                        )
                    table = "f%d_%s" % (file_id, _safe(str(sheet)))
                    frame.to_sql(table, conn, if_exists="replace", index=False)
                    total += int(len(frame))
                conn.execute(
                    "UPDATE source_file SET n_rows=?, status='loaded', message='' WHERE id=?",
                    (total, file_id),
                )
            elif suffix in TEXT and size <= 5_000_000:
                body = None
                for enc in ("utf-8", "gbk", "gb18030"):
                    try:
                        body = path.read_text(encoding=enc)
                        break
                    except UnicodeDecodeError:
                        continue
                if body is None:
                    raise RuntimeError("文本编码无法识别")
                conn.execute("INSERT INTO source_text(file_id, body) VALUES (?, ?)", (file_id, body))
                conn.execute(
                    "UPDATE source_file SET n_rows=?, status='loaded', message='text' WHERE id=?",
                    (body.count("\n") + 1, file_id),
                )
            else:
                conn.execute(
                    "UPDATE source_file SET status='catalog', message='只登记文件，不把二进制拆进表' WHERE id=?",
                    (file_id,),
                )
        except Exception as exc:
            conn.execute(
                "UPDATE source_file SET status='error', message=? WHERE id=?",
                (traceback.format_exc().splitlines()[-1][:500], file_id),
            )
        conn.commit()
        print(datetime.now().isoformat(timespec="seconds"), file_id, rel)
    conn.close()
    print("database", DB_PATH)


if __name__ == "__main__":
    ingest()
