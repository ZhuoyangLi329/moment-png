"""Fixed-cutoff one-loop halo power (EdS kernels), and its one-PNG-leg response.

Status: diagnostic. There are no counterterms, so results depend strongly on the
radial cutoffs [qmin, qmax] (see docs/findings.md, loop section). All integrals
use a log-spaced radial grid and a uniform mu grid with the trapezoid rule.

Bias expansion: delta_h = b1 delta + b2/2 delta^2 + bK2 K^2 (+ PNG terms), with
    K2(q, r) = b1 F2(q, r) + b2/2 + bK2 S2(q, r),   S2 = mu^2 - 1/3.
"""
from __future__ import annotations

import numpy as np

trapz = getattr(np, "trapezoid", None) or np.trapz


def _grid(k, qmin, qmax, nq, nmu):
    x = np.linspace(np.log(qmin), np.log(qmax), nq)
    mu = np.linspace(-1, 1, nmu)
    qq, mm = np.meshgrid(np.exp(x), mu, indexing="ij")
    r = np.sqrt(k * k + qq * qq - 2 * k * qq * mm)  # |k - q|
    return x, mu, qq, mm, r


def _f2(qq, r, mm):
    return 5 / 7 + 0.5 * mm * (qq / np.maximum(r, 1e-30) + r / np.maximum(qq, 1e-30)) + 2 / 7 * mm * mm


def _p22(k, kernel_sq_times_pp, x, mu):
    # 2 int d^3q/(2pi)^3 K^2 P(q) P(|k-q|), azimuth integrated (2 pi), q^3 from dq = q dlnq.
    return float(trapz(trapz(kernel_sq_times_pp, mu, axis=1), x) / (2 * np.pi) ** 3 * 2 * 2 * np.pi)


def halo_P22(k, P, b1, b2, bK2, qmin, qmax, nq=160, nmu=96):
    """P22 with the halo kernel K2; b1=1, b2=bK2=0 gives the matter P22."""
    x, mu, qq, mm, r = _grid(float(k), qmin, qmax, nq, nmu)
    kh = b1 * _f2(qq, r, mm) + 0.5 * b2 + bK2 * (mm * mm - 1 / 3)
    return _p22(k, qq**3 * kh * kh * np.asarray(P(qq)) * np.asarray(P(r)), x, mu)


def halo_P22_directional(k, P, Pdir, b1, b2, bK2, qmin, qmax, nq=160, nmu=96):
    """d P22 / d lambda under P -> P + lambda Pdir (one perturbed leg, product rule)."""
    x, mu, qq, mm, r = _grid(float(k), qmin, qmax, nq, nmu)
    kh = b1 * _f2(qq, r, mm) + 0.5 * b2 + bK2 * (mm * mm - 1 / 3)
    pp = np.asarray(Pdir(qq)) * np.asarray(P(r)) + np.asarray(P(qq)) * np.asarray(Pdir(r))
    return _p22(k, qq**3 * kh * kh * pp, x, mu)


def _p13_kernel(r):
    eps = np.abs(r - 1.0) < 1e-6  # analytic finite limit at r = 1
    log = np.where(eps, 0.0, np.log(np.abs((1 + r) / np.maximum(np.abs(1 - r), 1e-30))))
    return 12 / r**2 - 158 + 100 * r**2 - 42 * r**4 + 3 * (r * r - 1) ** 3 * (7 * r * r + 2) * log / r**3


def matter_P13(k, P, qmin, qmax, nq=160):
    """EdS angle-averaged P13 = P(k) k^3/(252 (2pi)^2) int dr P(kr) kernel(r)."""
    k = float(k)
    x = np.linspace(np.log(qmin), np.log(qmax), nq)
    q = np.exp(x)
    r = q / max(k, 1e-30)
    return float(P(k) * k**3 / (252 * 2 * np.pi**2) * trapz(np.asarray(P(q)) * _p13_kernel(r) * r, x))


def matter_P13_directional(k, P, Pdir, qmin, qmax, nq=160):
    k = float(k)
    x = np.linspace(np.log(qmin), np.log(qmax), nq)
    q = np.exp(x)
    r = q / max(k, 1e-30)
    kern = _p13_kernel(r) * r
    pre = k**3 / (252 * 2 * np.pi**2)
    return float(Pdir(k) * pre * trapz(np.asarray(P(q)) * kern, x)
                 + P(k) * pre * trapz(np.asarray(Pdir(q)) * kern, x))


def halo_P13(k, P, b1, b2, bK2, qmin, qmax, nq=160, nmu=96) -> dict:
    """b1^2 F3 (matter P13) + b1 b2 D3 + b1 bK2 T3, collapsed at (k, q, -q)."""
    k = float(k)
    if k <= 0 or qmin <= 0 or qmax <= qmin:
        raise ValueError("invalid k or cutoff")
    x, mu, qq, mm, _ = _grid(k, qmin, qmax, nq, nmu)
    fp = 5 / 7 + 0.5 * mm * (k / qq + qq / k) + 2 / 7 * mm * mm    # F2(k, q)
    fm = 5 / 7 - 0.5 * mm * (k / qq + qq / k) + 2 / 7 * mm * mm    # F2(k, -q)
    d3 = (fp + fm) / 3.0
    kmq = np.sqrt(k * k + qq * qq - 2 * k * qq * mm)
    kpq = np.sqrt(k * k + qq * qq + 2 * k * qq * mm)
    s_a = np.where(kmq > 0, ((k * mm - qq) / np.where(kmq > 0, kmq, 1)) ** 2 - 1 / 3, 0.0)  # S2(q, k-q)
    s_b = np.where(kpq > 0, ((k * mm + qq) / np.where(kpq > 0, kpq, 1)) ** 2 - 1 / 3, 0.0)  # S2(-q, k+q)
    t3 = 2.0 / 3.0 * (s_a * fm + s_b * fp)
    integrand = (b2 * d3 + bK2 * t3) * np.asarray(P(qq)) * qq**3
    bias = 6.0 * b1 * float(P(k)) * float(trapz(trapz(integrand, mu, axis=1), x)) / (4 * np.pi**2)
    matter = b1 * b1 * matter_P13(k, P, qmin, qmax, nq)
    return {"total": matter + bias, "matter": matter, "bias": bias}


def halo_png_loop_response(k, P, Pdir, b1, b2, bK2, qmin, qmax, nq=160, nmu=96) -> float:
    """One-PNG-leg derivative of [halo P22 + b1^2 P13]; PNG kernel bias insertions are NOT included."""
    return (halo_P22_directional(k, P, Pdir, b1, b2, bK2, qmin, qmax, nq, nmu)
            + b1 * b1 * matter_P13_directional(k, P, Pdir, qmin, qmax, nq))


def loop_components(kbins, P, M, b1, b2, bK2, bphi, qmin, qmax, nq, nmu) -> dict:
    """Halo P22, P13 and the per-fNL PNG loop response evaluated at each k in ``kbins``."""
    pdir = lambda q: bphi / np.maximum(np.abs(M(q)), 1e-30) * P(q)
    p22, p13, dl = [], [], []
    for k in kbins:
        p22.append(halo_P22(k, P, b1, b2, bK2, qmin, qmax, nq, nmu))
        p13.append(halo_P13(k, P, b1, b2, bK2, qmin, qmax, nq, nmu)["total"])
        dl.append(halo_png_loop_response(k, P, pdir, b1, b2, bK2, qmin, qmax, nq, nmu))
    return {"P22": np.asarray(p22), "P13": np.asarray(p13), "dloop_dfNL": np.asarray(dl)}
