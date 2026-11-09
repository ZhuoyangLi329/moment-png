"""Tree-level halo power with local-PNG scale-dependent bias, on the mesh lattice.

    P_h(k) = [b1 + fNL bphi / M(k)]^2 P_m(k) T_m(k) + P_shot T_s(k)

bphi is the *full* PNG bias coefficient (Delta b = fNL bphi / M); the universal
mass-function relation gives bphi = 2 delta_c (b1 - p). T_m and T_s are the mesh
transfers applied to the clustering and shot terms (CIC power transfer or 1).

The paired odd response used to calibrate bphi is linear in c = b1 * bphi:
    [P_h(+f) - P_h(-f)] / (2 f) = c * 2 P_m T_m / M.
"""
from __future__ import annotations

import numpy as np

from ..mesh import Lattice


def universal_bphi(b1, p, delta_c=1.686, sigma_b1=0.0, sigma_p=0.0, sigma_delta_c=0.0):
    """bphi = 2 delta_c (b1 - p) and its linearly propagated 1-sigma error."""
    value = 2.0 * delta_c * (b1 - p)
    err = np.sqrt((2 * delta_c * sigma_b1) ** 2 + (2 * delta_c * sigma_p) ** 2
                  + (2 * (b1 - p) * sigma_delta_c) ** 2)
    return float(value), float(err)


def transfers(lat: Lattice, convention: str) -> tuple[np.ndarray, np.ndarray]:
    """Mesh transfers (T_m, T_s) for a named convention.

    cic_both   : CIC power transfer on clustering and shot terms (default)
    cic_matter : CIC on clustering only, unfiltered shot noise
    none       : no mesh transfer
    """
    one = np.ones_like(lat.k)
    if convention == "cic_both":
        return lat.cic_power, lat.cic_power
    if convention == "cic_matter":
        return lat.cic_power, one
    if convention == "none":
        return one, one
    raise ValueError(f"unknown mesh convention {convention!r}")


def halo_power(pm, M, b1, bphi=0.0, fnl=0.0, pshot=0.0, t_matter=1.0, t_shot=1.0) -> np.ndarray:
    bh = b1 + fnl * bphi / np.maximum(np.abs(M), 1e-30)
    p = bh * bh * pm * t_matter + pshot * t_shot
    p = np.array(p, dtype=float)
    p.flat[0] = 0.0  # zero mode (index 0 in full-FFT layout)
    return p


def mu1_tree(lat: Lattice, pm, M, scales, width, b1, bphi=0.0, fnl=0.0, pshot=0.0,
             convention="cic_both") -> np.ndarray:
    """Exact-window mu1(s) of the tree-level halo power."""
    from ..window import mu1
    tm, ts = transfers(lat, convention)
    return mu1(halo_power(pm, M, b1, bphi, fnl, pshot, tm, ts), scales, width, lat.boxsize)


def response_per_c(pm, M, t_matter=1.0) -> np.ndarray:
    """d P_h / d fNL per unit c = b1 bphi, i.e. 2 P_m T_m / M (zero mode removed)."""
    out = 2.0 * pm * t_matter / np.where(M == 0, np.inf, M)
    out = np.array(np.broadcast_to(out, np.shape(pm)), dtype=float)
    out.flat[0] = 0.0
    return out
