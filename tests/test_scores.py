# -*- coding: utf-8 -*-
from core_bases.evaluate.score import score


def test_acceptance_numbers_unchanged():
    payload = score(write=False)
    assert payload["n"] == 2878
    line1 = next(row for row in payload["lines"] if row["id"] == "line1")
    assert abs(line1["R2"] - 0.2939220730565444) < 1e-9
    assert abs(line1["RMSE"] - 0.69180665612781) < 1e-9
    assert payload["line6_line7_max_abs_diff"] == 0.0
