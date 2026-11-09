"""Periodic mesh conventions shared by the estimator and the theory projection.

Conventions (frozen v1):
  * CIC (trilinear) assignment of halo counts; delta = n / <n> - 1.
  * Fourier modes in full ``numpy.fft.fftn`` layout, k = 2 pi fftfreq(N, L/N).
  * Power per mode P(k) = V / N^6 |FFT[delta](k)|^2, zero mode removed.
  * CIC *field* transfer A(k) = prod_i sinc^2(k_i H / 2); the *power* transfer is A^2.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np


def cic_paint(positions, nmesh: int, boxsize: float) -> np.ndarray:
    """CIC overdensity field delta = n/<n> - 1 on a periodic nmesh^3 grid."""
    u = np.asarray(positions, dtype=float) / boxsize * nmesh
    i0 = np.floor(u).astype(np.int64)
    f = u - i0
    grid = np.zeros(nmesh**3, dtype=np.float64)
    for dx in (0, 1):
        wx = (1 - f[:, 0]) if dx == 0 else f[:, 0]
        ix = (i0[:, 0] + dx) % nmesh
        for dy in (0, 1):
            wy = (1 - f[:, 1]) if dy == 0 else f[:, 1]
            iy = (i0[:, 1] + dy) % nmesh
            for dz in (0, 1):
                wz = (1 - f[:, 2]) if dz == 0 else f[:, 2]
                iz = (i0[:, 2] + dz) % nmesh
                grid += np.bincount((ix * nmesh + iy) * nmesh + iz, weights=wx * wy * wz,
                                    minlength=nmesh**3)
    grid = grid.reshape(nmesh, nmesh, nmesh)
    return grid / grid.mean() - 1.0


class Lattice:
    """Full-FFT wavevector lattice of a periodic box, with CIC transfers."""

    def __init__(self, nmesh: int, boxsize: float):
        self.nmesh = int(nmesh)
        self.boxsize = float(boxsize)
        self.volume = self.boxsize**3
        self.cell = self.boxsize / self.nmesh
        k1 = 2 * np.pi * np.fft.fftfreq(self.nmesh, d=self.cell)
        self.kx, self.ky, self.kz = np.meshgrid(k1, k1, k1, indexing="ij", sparse=True)
        self.k = np.sqrt(self.kx**2 + self.ky**2 + self.kz**2)
        self.zero = self.k == 0

    @property
    def cic_field(self) -> np.ndarray:
        """CIC field transfer A(k) = prod_i sinc^2(k_i H / 2)."""
        h = self.cell / (2 * np.pi)
        return np.sinc(self.kx * h) ** 2 * np.sinc(self.ky * h) ** 2 * np.sinc(self.kz * h) ** 2

    @property
    def cic_power(self) -> np.ndarray:
        """CIC power transfer A(k)^2 = prod_i sinc^4(k_i H / 2)."""
        return self.cic_field**2


@lru_cache(maxsize=8)
def lattice(nmesh: int, boxsize: float) -> Lattice:
    return Lattice(nmesh, boxsize)


def mode_power(delta: np.ndarray, boxsize: float) -> np.ndarray:
    """Power per Fourier mode, V/N^6 |FFT delta|^2, with the zero mode set to 0."""
    n = delta.shape[0]
    p = boxsize**3 / n**6 * np.abs(np.fft.fftn(delta)) ** 2
    p[0, 0, 0] = 0.0
    return p


def binned_power(power: np.ndarray, kmag: np.ndarray, dk: float = 0.005, kmax: float = 0.3):
    """Isotropic shell average of a mode-power cube.

    Bins are [i dk, (i+1) dk) up to kmax; empty bins and k=0 are dropped.
    Returns (k_center, P_mean, n_modes).
    """
    km = np.broadcast_to(kmag, power.shape).ravel()
    edges = np.arange(0, kmax + dk, dk)
    ib = np.digitize(km, edges) - 1
    ok = (ib >= 0) & (ib < len(edges) - 1) & (km > 0)
    counts = np.bincount(ib[ok], minlength=len(edges) - 1)
    sums = np.bincount(ib[ok], weights=power.ravel()[ok], minlength=len(edges) - 1)
    good = counts > 0
    centers = 0.5 * (edges[:-1] + edges[1:])
    return centers[good], sums[good] / counts[good], counts[good]


def bin_average(values: np.ndarray, kmag: np.ndarray, dk: float = 0.005, kmax: float = 0.3):
    """Average any lattice quantity (e.g. a CIC transfer) on the binned_power bins."""
    return binned_power(np.broadcast_to(values, np.broadcast(values, kmag).shape), kmag, dk, kmax)[1]
