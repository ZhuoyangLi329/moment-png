"""Model algebra: PNG bias normalisation, response template, loop integrals, GLS fits."""
import numpy as np

from momentpng.stats import gls_amplitude, gls_linear
from momentpng.theory.loops import (halo_P13, halo_P22, matter_P13, matter_P13_directional)
from momentpng.theory.tree import halo_power, response_per_c, universal_bphi

P = lambda k: np.exp(-np.asarray(k) ** 2) + 0.2


def test_bphi_is_the_full_coefficient():
    """P_h = (b1 + fNL bphi / M)^2 P_m: no hidden (b1 - 1) or b1 factor."""
    pm, M = np.array([0.0, 2.0, 3.0]), np.array([1.0, 0.5, 4.0])
    got = halo_power(pm, M, b1=2.0, bphi=5.0, fnl=1.0)
    np.testing.assert_allclose(got[1:], (2.0 + 5.0 / M[1:]) ** 2 * pm[1:])
    assert got[0] == 0.0


def test_odd_response_is_linear_in_c():
    pm, M = np.array([0.0, 2.0, 3.0]), np.array([1.0, 0.5, 4.0])
    b1, bphi, f = 2.7, 3.7, 100.0
    odd = (halo_power(pm, M, b1, bphi, f) - halo_power(pm, M, b1, bphi, -f)) / (2 * f)
    np.testing.assert_allclose(odd, b1 * bphi * response_per_c(pm, M))


def test_universal_bphi():
    v, e = universal_bphi(2.0, 1.12, 1.686, sigma_b1=0.1)
    np.testing.assert_allclose(v, 2 * 1.686 * 0.88)
    np.testing.assert_allclose(e, 2 * 1.686 * 0.1)


def test_p13_directional_derivative():
    D = lambda k: 0.3 * np.exp(-np.asarray(k) ** 2) / (1 + np.asarray(k) ** 2)
    k, qmin, qmax, n, eps = 0.13, 0.01, 0.4, 240, 1e-5
    fd = (matter_P13(k, lambda x: P(x) + eps * D(x), qmin, qmax, n)
          - matter_P13(k, lambda x: P(x) - eps * D(x), qmin, qmax, n)) / (2 * eps)
    an = matter_P13_directional(k, P, D, qmin, qmax, n)
    assert abs(fd - an) / max(abs(fd), abs(an)) < 2e-4


def test_halo_p13_reduces_to_matter():
    r = halo_P13(0.2, P, 2.0, 0.0, 0.0, 0.01, 0.8, nq=48, nmu=40)
    np.testing.assert_allclose(r["total"], 4.0 * matter_P13(0.2, P, 0.01, 0.8, nq=48), rtol=1e-12)
    assert abs(r["bias"]) < 1e-14
    assert halo_P13(0.2, P, 2.0, -0.2, 0.1, 0.01, 0.8, nq=48, nmu=40)["bias"] != 0


def test_halo_p22_scaling():
    a = halo_P22(0.1, P, 1.0, 0.0, 0.0, 0.01, 1.0, nq=64, nmu=48)
    b = halo_P22(0.1, P, 2.0, 0.0, 0.0, 0.01, 1.0, nq=64, nmu=48)
    np.testing.assert_allclose(b, 4 * a, rtol=1e-12)
    assert a > 0


def test_gls_recovers_known_amplitude():
    rng = np.random.default_rng(0)
    t = np.linspace(1, 2, 6)
    x = 3.0 * t + rng.normal(scale=0.05, size=(400, 6))
    r = gls_amplitude(t, x)
    assert abs(r["amplitude"] - 3.0) < 4 * r["sigma"]
    assert 0.3 < r["chi2_dof"] < 3


def test_gls_linear_exact():
    X = np.column_stack([np.linspace(1, 3, 5), np.ones(5)])
    y = X @ np.array([2.0, -1.0])
    r = gls_linear(X, y, np.diag(np.full(5, 0.1)))
    np.testing.assert_allclose(r["beta"], [2.0, -1.0], atol=1e-12)
