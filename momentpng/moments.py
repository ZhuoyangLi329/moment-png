"""ConKer-style shell moments on a periodic mesh.

For each shell radius s, with K_s the discrete top-hat shell kernel normalised to
unit sum and delta_s = K_s * delta (periodic convolution):

    eta_s(x) = delta(x) delta_s(x)
    mu1(s)   = < eta_s >
    mu2(s)   = < (eta_s - mu1)^2 >

    mu3(s)   = < (eta_s - mu1)^3 >

The same pass also returns the Gaussian (Wick) predictions from the *same* field,
for jointly Gaussian delta, delta_s with sigma0^2 = <delta^2>, sigma_s^2 = <delta_s^2>:
    mu2_G = sigma0^2 sigma_s^2 + mu1^2
    mu3_G = 6 mu1 sigma0^2 sigma_s^2 + 2 mu1^3
mu_n - mu_n,G is the connected (non-Gaussian + discreteness) part.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from .mesh import cic_paint


def shell_kernel(nmesh: int, boxsize: float, radius: float, width: float) -> np.ndarray:
    """Unit-sum periodic top-hat shell, cells with |r| in [radius - w/2, radius + w/2)."""
    q = np.arange(nmesh)
    q = np.minimum(q, nmesh - q) * boxsize / nmesh
    r = np.sqrt(q[:, None, None] ** 2 + q[None, :, None] ** 2 + q[None, None, :] ** 2)
    mask = (r >= radius - width / 2) & (r < radius + width / 2)
    if not mask.any():
        raise ValueError(f"empty shell radius={radius} width={width} at nmesh={nmesh}")
    k = mask.astype(float)
    return k / k.sum()


@lru_cache(maxsize=64)
def shell_kernel_rfft(nmesh: int, boxsize: float, radius: float, width: float) -> np.ndarray:
    """Real-valued rfftn of the (inversion-symmetric) shell kernel."""
    w = np.fft.rfftn(shell_kernel(nmesh, boxsize, radius, width))
    return np.ascontiguousarray(w.real)


def gaussian_moments(mu1, sigma0_sq, sigma_s_sq) -> dict:
    """Wick predictions for mu2 and mu3 of eta = delta * delta_s (jointly Gaussian fields)."""
    mu1 = np.asarray(mu1, dtype=float)
    s0 = np.asarray(sigma0_sq, dtype=float)
    var = (s0[..., None] if s0.ndim else s0) * np.asarray(sigma_s_sq, dtype=float)
    return {"mu2_gaussian": var + mu1**2, "mu3_gaussian": 6 * mu1 * var + 2 * mu1**3}


def valid_scales(nmesh: int, boxsize: float, scales, width: float) -> np.ndarray:
    """Subset of ``scales`` whose discrete shell is non-empty on this grid."""
    q = np.arange(nmesh)
    q = np.minimum(q, nmesh - q) * boxsize / nmesh
    r = np.unique(np.sqrt(q[:, None, None] ** 2 + q[None, :, None] ** 2 + q[None, None, :] ** 2))
    return np.asarray([s for s in scales
                       if np.any((r >= s - width / 2) & (r < s + width / 2))], dtype=float)


def field_moments(delta: np.ndarray, boxsize: float, scales, width: float) -> dict:
    """mu1, mu2, mu3 and the Wick pieces of the shell product for one overdensity field."""
    n = delta.shape[0]
    dk = np.fft.rfftn(delta)
    sigma0_sq = float(np.mean(delta * delta))
    mu1, mu2, mu3, sigma_s_sq = [], [], [], []
    for s in scales:
        ds = np.fft.irfftn(dk * shell_kernel_rfft(n, float(boxsize), float(s), float(width)),
                           s=delta.shape)
        eta = delta * ds
        m1 = float(eta.mean())
        d = eta - m1
        d2 = d * d
        mu1.append(m1)
        mu2.append(float(d2.mean()))
        mu3.append(float((d2 * d).mean()))
        sigma_s_sq.append(float(np.mean(ds * ds)))
    mu1, mu2, mu3, sigma_s_sq = map(np.asarray, (mu1, mu2, mu3, sigma_s_sq))
    return {"mu1": mu1, "mu2": mu2, "mu3": mu3, "sigma0_sq": sigma0_sq, "sigma_s_sq": sigma_s_sq,
            **gaussian_moments(mu1, sigma0_sq, sigma_s_sq)}


def catalog_moments(positions, boxsize: float, nmesh: int, scales, width: float) -> dict:
    return field_moments(cic_paint(positions, nmesh, boxsize), boxsize, scales, width)
