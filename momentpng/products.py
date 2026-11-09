"""On-disk measurement products.

Layout:  {results}/measurements/n{N}{variant}/{node}_real{a:03d}-real{b:03d}.npz
Each file holds one contiguous realization block for one node (or the Poisson
control, node="poisson", indexed by seed). ``variant`` tags a modified catalog
(e.g. "_d2" for 1/2 dilution, "_m1.6e13" for a raised mass cut). Arrays are
stacked along axis 0 in realization order. ``load`` merges blocks and selects
realizations by index.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from .config import realization_index
from .moments import gaussian_moments

PER_REALIZATION = ("mu1", "mu2", "mu3", "sigma0_sq", "sigma_s_sq", "mu2_gaussian", "P_h", "n_halo")
SHARED = ("s", "k", "nmodes", "fNL", "nmesh", "boxsize", "shell_width")


def block_path(results: Path, nmesh: int, node: str, start: int, stop: int, variant: str = "") -> Path:
    return (Path(results) / "measurements" / f"n{nmesh}{variant}"
            / f"{node}_real{start:03d}-real{stop - 1:03d}.npz")


def save_block(path: Path, rows: list[dict], ids: list[str], shared: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = {k: np.asarray([r[k] for r in rows]) for k in PER_REALIZATION if k in rows[0]}
    np.savez(path, realization_ids=np.asarray(ids), **arrays, **shared)


def load(results: Path, nmesh: int, node: str, indices=None, variant: str = "") -> dict:
    """Load and merge measurement blocks; ``indices`` selects realizations (in that order)."""
    files = sorted((Path(results) / "measurements" / f"n{nmesh}{variant}").glob(f"{node}_real*.npz"))
    if not files:
        raise FileNotFoundError(f"no measurements for node={node} n{nmesh}{variant} under {results}")
    blocks = [dict(np.load(f)) for f in files]
    ids = np.concatenate([b["realization_ids"] for b in blocks]).astype(str)
    lookup = {realization_index(r): i for i, r in enumerate(ids)}
    if len(lookup) != len(ids):
        raise ValueError(f"duplicate realizations across blocks for {node} n{nmesh}{variant}")
    for b, f in zip(blocks[1:], files[1:]):
        if not np.array_equal(b["s"], blocks[0]["s"]):
            raise ValueError(f"shell list differs between blocks: {f}")
    order = sorted(lookup) if indices is None else list(indices)
    missing = [i for i in order if i not in lookup]
    if missing:
        raise KeyError(f"{node} n{nmesh}{variant}: realizations not measured: {missing[:5]}...")
    sel = [lookup[i] for i in order]
    keys = [k for k in PER_REALIZATION if all(k in b for b in blocks)]
    out = {k: np.concatenate([b[k] for b in blocks])[sel] for k in keys}
    out["realization_ids"] = ids[sel]
    out.update({k: blocks[0][k] for k in SHARED})
    out["mu2_connected"] = out["mu2"] - out["mu2_gaussian"]
    if "mu3" in out:
        out["mu3_gaussian"] = gaussian_moments(out["mu1"], out["sigma0_sq"], out["sigma_s_sq"])["mu3_gaussian"]
        out["mu3_connected"] = out["mu3"] - out["mu3_gaussian"]
    return out


def features(d: dict, names, smin: float = 0.0, smax: float = np.inf, kmax: float = np.inf) -> np.ndarray:
    """Stack observables [n_real, n_data] from a loaded product, e.g. names=['P', 'mu1', 'mu2c'].

    P: binned P_h(k <= kmax); mu1, mu2, mu3; mu2G/mu3G: Wick predictions; mu2c/mu3c: connected
    parts (mu_n - mu_nG); R: mu2/mu2G - 1. Moment columns are restricted to smin <= s <= smax.
    """
    s = (d["s"] >= smin) & (d["s"] <= smax)
    cols = {"P": lambda: d["P_h"][:, d["k"] <= kmax],
            "mu1": lambda: d["mu1"][:, s], "mu2": lambda: d["mu2"][:, s], "mu3": lambda: d["mu3"][:, s],
            "mu2G": lambda: d["mu2_gaussian"][:, s], "mu2c": lambda: d["mu2_connected"][:, s],
            "R": lambda: (d["mu2"] / d["mu2_gaussian"] - 1)[:, s],
            "mu3G": lambda: d["mu3_gaussian"][:, s], "mu3c": lambda: d["mu3_connected"][:, s]}
    unknown = [n for n in names if n not in cols]
    if unknown:
        raise KeyError(f"unknown observables {unknown}; choose from {sorted(cols)}")
    return np.column_stack([cols[n]() for n in names])
