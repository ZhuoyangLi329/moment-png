"""ConKer-style shell moments on a periodic mesh.

For each shell radius s, with K_s the discrete top-hat shell kernel normalised to
unit sum and delta_s = K_s * delta (periodic convolution):

    eta_s(x) = delta(x) delta_s(x)
    mu1(s)   = < eta_s >
    mu2(s)   = < (eta_s - mu1)^2 >

The same pass also returns the Gaussian (Wick) prediction from the *same* field,
    mu2_G(s) = sigma0^2 sigma_s^2 + mu1(s)^2,
with sigma0^2 = <delta^2> and sigma_s^2 = <delta_s^2>; mu2 - mu2_G is the
connected (non-Gaussian + discreteness) part.
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


def field_moments(delta: np.ndarray, boxsize: float, scales, width: float) -> dict:
    """mu1, mu2 and the Wick pieces of the shell product for one overdensity field."""
    n = delta.shape[0]
    dk = np.fft.rfftn(delta)
    sigma0_sq = float(np.mean(delta * delta))
    mu1, mu2, sigma_s_sq = [], [], []
    for s in scales:
        ds = np.fft.irfftn(dk * shell_kernel_rfft(n, float(boxsize), float(s), float(width)),
                           s=delta.shape)
        eta = delta * ds
        m1 = float(eta.mean())
        mu1.append(m1)
        mu2.append(float(((eta - m1) ** 2).mean()))
        sigma_s_sq.append(float(np.mean(ds * ds)))
    mu1, mu2, sigma_s_sq = map(np.asarray, (mu1, mu2, sigma_s_sq))
    return {"mu1": mu1, "mu2": mu2, "sigma0_sq": sigma0_sq, "sigma_s_sq": sigma_s_sq,
            "mu2_gaussian": sigma0_sq * sigma_s_sq + mu1**2}


def catalog_moments(positions, boxsize: float, nmesh: int, scales, width: float) -> dict:
    return field_moments(cic_paint(positions, nmesh, boxsize), boxsize, scales, width)
