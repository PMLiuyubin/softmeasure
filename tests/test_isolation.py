# -*- coding: utf-8 -*-
import sys
from pathlib import Path

from core_bases.dataset.guard import assert_not_frozen
from fastapi.testclient import TestClient


def test_web_does_not_import_mining():
    sys.modules.pop("core_bases.mining", None)
    sys.modules.pop("core_bases.mining.report", None)
    import application.main as main
    assert "core_bases.mining" not in sys.modules
    assert "core_bases.mining.report" not in sys.modules
    client = TestClient(main.app)
    res = client.get("/api/health")
    assert res.status_code == 200
    assert "core_bases.mining" not in sys.modules


def test_frozen_names_rejected(tmp_path: Path):
    try:
        assert_not_frozen(tmp_path / "official_fru2h_dataset.pkl")
    except RuntimeError:
        return
    raise AssertionError("快照文件名必须被拒绝")
