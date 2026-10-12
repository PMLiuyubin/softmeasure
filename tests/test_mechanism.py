# -*- coding: utf-8 -*-
from core_bases.mechanism.formula import coefficients, lock_mn


def test_lock_at_reference_is_base():
    assert lock_mn(6.53, 3.85) == 67.55


def test_coefficients_stay_locked():
    c = coefficients()
    assert c["lock_base"] == 67.55
    assert c["lock_R"] == 0.59
    assert c["lock_S"] == -2.4
    assert c["R0"] == 6.53
    assert c["S0"] == 3.85
