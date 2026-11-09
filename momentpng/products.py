"""On-disk measurement products.

Layout:  results/measurements/n{N}/{node}_real{a:03d}-real{b:03d}.npz
Each file holds one contiguous realization block for one node (or the Poisson
control, node="poisson", indexed by seed). Arrays are stacked along axis 0 in
realization order. ``load`` merges blocks and selects realizations by index.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from .config import realization_index

PER_REALIZATION = ("mu1", "mu2", "sigma0_sq", "sigma_s_sq", "mu2_gaussian", "P_h", "n_halo")


def block_path(results: Path, nmesh: int, node: str, start: int, stop: int) -> Path:
    return Path(results) / "measurements" / f"n{nmesh}" / f"{node}_real{start:03d}-real{stop - 1:03d}.npz"


def save_block(path: Path, rows: list[dict], ids: list[str], shared: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = {k: np.asarray([r[k] for r in rows]) for k in PER_REALIZATION}
    np.savez(path, realization_ids=np.asarray(ids), **arrays, **shared)


def load(results: Path, nmesh: int, node: str, indices=None) -> dict:
    """Load and merge measurement blocks; ``indices`` selects realizations (in that order)."""
    files = sorted((Path(results) / "measurements" / f"n{nmesh}").glob(f"{node}_real*.npz"))
    if not files:
        raise FileNotFoundError(f"no measurements for node={node} nmesh={nmesh} under {results}")
    blocks = [dict(np.load(f)) for f in files]
    ids = np.concatenate([b["realization_ids"] for b in blocks]).astype(str)
    lookup = {realization_index(r): i for i, r in enumerate(ids)}
    if len(lookup) != len(ids):
        raise ValueError(f"duplicate realizations across blocks for {node} n{nmesh}")
    order = sorted(lookup) if indices is None else list(indices)
    missing = [i for i in order if i not in lookup]
    if missing:
        raise KeyError(f"{node} n{nmesh}: realizations not measured: {missing[:5]}...")
    sel = [lookup[i] for i in order]
    out = {k: np.concatenate([b[k] for b in blocks])[sel] for k in PER_REALIZATION}
    out["realization_ids"] = ids[sel]
    for k in ("s", "k", "nmodes", "fNL", "nmesh", "boxsize", "shell_width"):
        out[k] = blocks[0][k]
    out["mu2_connected"] = out["mu2"] - out["mu2_gaussian"]
    return out
