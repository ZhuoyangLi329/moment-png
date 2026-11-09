"""Halo catalogs: certified position products and the Quijote FoF group_tab reader."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .config import realization_id


def positions_path(root: Path, node: str, index: int) -> Path:
    return Path(root) / node / realization_id(index) / "positions_mpc_h.npy"


def load_positions(root: Path, node: str, index: int) -> np.ndarray:
    return np.load(positions_path(root, node, index), mmap_mode="r")


def uniform_catalog(seed: int, nhalo: int, boxsize: float) -> np.ndarray:
    """Matched iid-Poisson control catalog (same RNG convention as the legacy controls)."""
    return np.random.default_rng(seed).uniform(0, boxsize, size=(nhalo, 3))


def read_group_tab(base: Path, snapnum: int = 2):
    """Read FoF group positions [kpc/h] and masses [1e10 Msun/h] from Quijote group_tab files.

    Binary layout follows the public Quijote/Pylians FoF reader; every byte is
    accounted for, so a layout mismatch fails loudly.
    """
    ext = f"{snapnum:03d}"
    files = sorted((Path(base) / f"groups_{ext}").glob(f"group_tab_{ext}.*"),
                   key=lambda p: int(p.name.rsplit(".", 1)[1]))
    if not files:
        raise FileNotFoundError(Path(base) / f"groups_{ext}" / f"group_tab_{ext}.0")
    pos_parts, mass_parts, total, nfiles = [], [], None, None
    for path in files:
        with path.open("rb") as f:
            ng = int(np.fromfile(f, dtype=np.int32, count=1)[0])
            tg = int(np.fromfile(f, dtype=np.int32, count=1)[0])
            np.fromfile(f, dtype=np.int32, count=1)        # Nids
            np.fromfile(f, dtype=np.uint64, count=1)       # TotNids
            nf = int(np.fromfile(f, dtype=np.uint32, count=1)[0])
            if total is None:
                total, nfiles = tg, nf
            if (tg, nf) != (total, nfiles):
                raise ValueError(f"inconsistent header in {path}")
            np.fromfile(f, dtype=np.int32, count=ng)       # GroupLen
            np.fromfile(f, dtype=np.int32, count=ng)       # GroupOffset
            mass = np.fromfile(f, dtype=np.float32, count=ng)
            pos = np.fromfile(f, dtype=np.dtype((np.float32, 3)), count=ng)
            np.fromfile(f, dtype=np.dtype((np.float32, 3)), count=ng)  # velocities
            np.fromfile(f, dtype=np.dtype((np.float32, 6)), count=ng)  # GroupLenType
            np.fromfile(f, dtype=np.dtype((np.float32, 6)), count=ng)  # GroupMassType
            if len(mass) != ng or len(pos) != ng or f.tell() != path.stat().st_size:
                raise ValueError(f"unexpected group_tab layout in {path}")
        pos_parts.append(pos)
        mass_parts.append(mass)
    positions = np.concatenate(pos_parts)
    masses = np.concatenate(mass_parts)
    if len(positions) != total:
        raise ValueError(f"group count mismatch {len(positions)} != {total}")
    return positions, masses, files


def select_halos(positions_kpc, masses_code, mass_min: float, boxsize: float):
    """Apply the mass cut and convert to Mpc/h positions wrapped into the box."""
    masses = masses_code.astype(np.float64) * 1e10
    keep = masses >= mass_min
    pos = np.mod(positions_kpc[keep] / 1e3, boxsize).astype(np.float32)
    return pos, masses[keep]


def inventory(root: Path, nodes) -> dict:
    """Realizations with positions + metadata per node, with the selection fields checked."""
    out = {}
    for node in nodes:
        rows = []
        for d in sorted((Path(root) / node).glob("real*")):
            p, m = d / "positions_mpc_h.npy", d / "metadata.json"
            if not p.exists():
                continue
            x = np.load(p, mmap_mode="r")
            md = json.loads(m.read_text()) if m.exists() else {}
            rows.append({"realization": d.name, "n_halo": int(x.shape[0]), "dtype": str(x.dtype),
                         "mass_threshold": md.get("mass_threshold_msun_h"),
                         "snapnum": md.get("snapnum"), "has_metadata": m.exists()})
        out[node] = rows
    return out
