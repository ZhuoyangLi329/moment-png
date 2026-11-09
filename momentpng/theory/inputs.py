"""External z=1 linear-theory table and its evaluation on the mesh lattice.

Table columns (data/quijote_fiducial_z1_plin_pphi_M.dat, copied from the MARISA-B
analysis): k [h/Mpc], P_L [(Mpc/h)^3], P_phi [(Mpc/h)^3], M(k, z=1), with
delta_L(k) = M(k) phi(k). Not calibrated on any PNG response.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from ..mesh import Lattice


def load_table(path: str | Path) -> dict:
    k, pm, pphi, m = np.loadtxt(path, comments="#").T
    return {"k": k, "Pm": pm, "Pphi": pphi, "M": m}


def on_lattice(table: dict, lat: Lattice) -> tuple[np.ndarray, np.ndarray]:
    """P_m and M at every lattice |k| (linear interpolation, clipped to the table range).

    The zero mode gets P_m = 0 and M = 1 so that 1/M stays finite.
    """
    kt = table["k"]
    kk = np.clip(lat.k, kt.min(), kt.max())
    pm = np.interp(kk, kt, table["Pm"])
    m = np.interp(kk, kt, table["M"])
    pm[lat.zero] = 0.0
    m[lat.zero] = 1.0
    return pm, m
