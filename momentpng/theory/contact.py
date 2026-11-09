"""Discrete Poisson contact terms of mu2 for an iid (unclustered) catalog.

For Poisson points with mean lambda per cell, the connected mu2 beyond the Wick
term comes from the kappa_22 contraction at zero lag.

  * ``iid``: nearest-grid-point idealisation, K_0^2 / lambda^3.
  * ``cic``: the exact CIC-assignment version,
        I / lambda^3,  I = int_[0,1]^3 d^3u  w_0(u)^2 [sum_e K_e w_e(u)]^2,
    where e runs over the 8 cells receiving a point at fractional offset u.
Clustered halos add repeated-index terms that are not modelled here.
"""
from __future__ import annotations

import numpy as np


def poisson_contact_iid(kernel: np.ndarray, lam: float) -> float:
    if lam <= 0:
        raise ValueError("lambda must be positive")
    return float(kernel[0, 0, 0] ** 2 / lam**3)


def poisson_contact_cic(kernel: np.ndarray, lam: float, order: int = 8) -> float:
    if lam <= 0:
        raise ValueError("lambda must be positive")
    x, w = np.polynomial.legendre.leggauss(order)
    u, w = (x + 1) / 2, w / 2
    ux, uy, uz = np.meshgrid(u, u, u, indexing="ij")
    wgt = w[:, None, None] * w[None, :, None] * w[None, None, :]
    val = np.zeros_like(ux)
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                ww = ((1 - ux) if dx == 0 else ux) * ((1 - uy) if dy == 0 else uy) * ((1 - uz) if dz == 0 else uz)
                val += kernel[dx, dy, dz] * ww
    w0 = (1 - ux) * (1 - uy) * (1 - uz)
    return float(np.sum(wgt * w0**2 * val**2) / lam**3)
