"""Exact discrete projection of a lattice power spectrum onto the shell moments.

The estimator in ``moments.py`` is linear in the field, so for a power cube P(k)
given per full-FFT mode (zero mode removed, same normalisation as
``mesh.mode_power``) the *ensemble* moments are, without any continuum
approximation,

    mu1(s)   = V^-1 sum_k P(k) W_s(k)
    mu2_G(s) = sigma0^2 sigma_s^2 + xi_s^2,
        sigma0^2 = V^-1 sum_k P,  sigma_s^2 = V^-1 sum_k P W_s^2,  xi_s = mu1(s),

where W_s = FFT[K_s] of the *same* discrete shell kernel. Mesh effects (CIC,
aliasing) live entirely in P, never in W.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from .moments import shell_kernel


@lru_cache(maxsize=64)
def shell_window(nmesh: int, boxsize: float, radius: float, width: float) -> np.ndarray:
    """W_s(k) on the full FFT lattice (real: the kernel is inversion symmetric)."""
    w = np.fft.fftn(shell_kernel(nmesh, boxsize, radius, width))
    if np.max(np.abs(w.imag)) > 1e-12:
        raise ValueError("shell kernel is not inversion symmetric")
    return np.ascontiguousarray(w.real)


def _check_power(power: np.ndarray) -> np.ndarray:
    p = np.array(power, dtype=float)
    n = p.shape[0]
    if p.shape != (n, n, n) or not np.isfinite(p).all():
        raise ValueError("power must be a finite (N, N, N) cube in full-FFT layout")
    p[0, 0, 0] = 0.0  # the estimator subtracts the catalog mean
    return p


def mu1(power: np.ndarray, scales, width: float, boxsize: float) -> np.ndarray:
    p = _check_power(power)
    n, v = p.shape[0], boxsize**3
    return np.array([np.sum(p * shell_window(n, float(boxsize), float(s), float(width))) / v
                     for s in np.atleast_1d(scales)])


def mu2_gaussian(power: np.ndarray, scales, width: float, boxsize: float,
                 sample_centered: bool = False) -> dict:
    """Ensemble Wick prediction; ``sample_centered`` subtracts Var(mean eta) = 2 sum (PW)^2 / V^2."""
    p = _check_power(power)
    n, v = p.shape[0], boxsize**3
    sigma0_sq = float(p.sum() / v)
    out = {"sigma0_sq": sigma0_sq, "sigma_s_sq": [], "xi_s": [], "mu2_gaussian": []}
    for s in np.atleast_1d(scales):
        w = shell_window(n, float(boxsize), float(s), float(width))
        pw = p * w
        sig_s, xi = float(np.sum(pw * w) / v), float(pw.sum() / v)
        val = sigma0_sq * sig_s + xi * xi
        if sample_centered:
            val -= float(2 * np.sum(pw * pw) / v**2)
        out["sigma_s_sq"].append(sig_s)
        out["xi_s"].append(xi)
        out["mu2_gaussian"].append(val)
    return {k: np.asarray(v_) if isinstance(v_, list) else v_ for k, v_ in out.items()}
