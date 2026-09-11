#!/usr/bin/env python3
"""Reconstruct certified z=1 FoF position catalogs from Quijote group_tab binaries.

The binary layout follows the public Quijote/Pylians FoF reader.  The selected
float32 arrays are byte-identical to the existing converted catalogs for the
same input, which is checked by the batch smoke audit.
"""
import argparse, datetime, hashlib, json
from pathlib import Path
import numpy as np


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_group_tab(base: Path, snapnum: int = 2):
    ext = f"{snapnum:03d}"
    files = sorted((base / f"groups_{ext}").glob(f"group_tab_{ext}.*"), key=lambda p: int(p.name.rsplit('.', 1)[1]))
    if not files:
        raise FileNotFoundError(base / f"groups_{ext}" / f"group_tab_{ext}.0")
    pos_parts, mass_parts = [], []
    total_groups = None
    nfiles_expected = None
    for path in files:
        with path.open("rb") as f:
            ng = int(np.fromfile(f, dtype=np.int32, count=1)[0])
            tg = int(np.fromfile(f, dtype=np.int32, count=1)[0])
            _nids = np.fromfile(f, dtype=np.int32, count=1)
            _totnids = np.fromfile(f, dtype=np.uint64, count=1)
            nf = int(np.fromfile(f, dtype=np.uint32, count=1)[0])
            if total_groups is None:
                total_groups, nfiles_expected = tg, nf
            if tg != total_groups or nf != nfiles_expected:
                raise ValueError(f"inconsistent header in {path}")
            glen = np.fromfile(f, dtype=np.int32, count=ng)
            if len(glen) != ng:
                raise ValueError(f"truncated GroupLen in {path}")
            _goff = np.fromfile(f, dtype=np.int32, count=ng)
            mass = np.fromfile(f, dtype=np.float32, count=ng)
            pos = np.fromfile(f, dtype=np.dtype((np.float32, 3)), count=ng)
            _vel = np.fromfile(f, dtype=np.dtype((np.float32, 3)), count=ng)
            _tlen = np.fromfile(f, dtype=np.dtype((np.float32, 6)), count=ng)
            _tmass = np.fromfile(f, dtype=np.dtype((np.float32, 6)), count=ng)
            if any(len(x) != ng for x in (mass, pos)):
                raise ValueError(f"truncated group arrays in {path}")
            if f.tell() != path.stat().st_size:
                raise ValueError(f"unparsed bytes in {path}: {f.tell()} != {path.stat().st_size}")
            pos_parts.append(pos)
            mass_parts.append(mass)
    positions = np.concatenate(pos_parts) if pos_parts else np.empty((0, 3), dtype=np.float32)
    masses = np.concatenate(mass_parts) if mass_parts else np.empty(0, dtype=np.float32)
    if len(positions) != total_groups:
        raise ValueError(f"group count mismatch {len(positions)} != {total_groups}")
    return positions, masses, files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--nodes", nargs="+", default=["LC_m", "LC_p"])
    ap.add_argument("--start", type=int, default=100)
    ap.add_argument("--stop", type=int, default=500)
    ap.add_argument("--mass-threshold", type=float, default=1e13)
    ap.add_argument("--snapnum", type=int, default=2)
    ap.add_argument("--boxsize", type=float, default=1000.0)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--manifest", type=Path, required=True)
    a = ap.parse_args()
    rows = []
    parser_sha = sha256(Path(__file__))
    for node in a.nodes:
        for rid_num in range(a.start, a.stop):
            rid = f"real{rid_num:03d}"
            source = a.input_root / node / rid
            out = a.output_root / node / rid
            pos_out = out / "positions_mpc_h.npy"
            mass_out = out / "masses_msun_h.npy"
            meta_out = out / "metadata.json"
            if pos_out.exists() and mass_out.exists() and meta_out.exists() and not a.overwrite:
                rows.append({"node": node, "realization": rid, "status": "SKIP", "positions": str(pos_out)})
                continue
            pos, mass_code, files = read_group_tab(source, a.snapnum)
            masses = (mass_code * 1e10).astype(np.float32)
            selected = masses >= a.mass_threshold
            positions = (pos[selected] / 1e3).astype(np.float32)
            masses = masses[selected]
            if np.any(positions < 0) or np.any(positions >= a.boxsize):
                raise ValueError(f"position outside box for {node}/{rid}")
            out.mkdir(parents=True, exist_ok=True)
            np.save(pos_out, positions)
            np.save(mass_out, masses)
            meta = {
                "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "schema": "fof_positions_metadata_v2",
                "cosmology": node,
                "realization": rid_num,
                "input_root": str(a.input_root),
                "input_files": [str(x) for x in files],
                "input_sha256": {str(x): sha256(x) for x in files},
                "parser": "reconstruct_fof_positions.py",
                "parser_sha256": parser_sha,
                "snapnum": a.snapnum,
                "redshift": 1.0,
                "group_dir": f"groups_{a.snapnum:03d}",
                "boxsize_mpc_h": a.boxsize,
                "mass_threshold_msun_h": a.mass_threshold,
                "mass_unit": "Msun/h after GroupMass * 1e10",
                "position_unit": "Mpc/h after GroupPos / 1e3",
                "n_halo_total": int(len(pos)),
                "n_halo_selected": int(len(positions)),
                "selected_mass_min_msun_h": float(masses.min()) if len(masses) else None,
                "selected_mass_max_msun_h": float(masses.max()) if len(masses) else None,
                "position_dtype": str(positions.dtype),
                "mass_dtype": str(masses.dtype),
                "output_positions": str(pos_out),
                "output_masses": str(mass_out),
            }
            meta_out.write_text(json.dumps(meta, indent=2) + "\n")
            rows.append({"node": node, "realization": rid, "status": "WRITE", "n_halo_total": int(len(pos)), "n_halo_selected": int(len(positions)), "positions_sha256": sha256(pos_out), "masses_sha256": sha256(mass_out), "metadata_sha256": sha256(meta_out)})
    out = {"schema": "fof_positions_reconstruction_batch_v1", "status": "PASS", "input_root": str(a.input_root), "output_root": str(a.output_root), "nodes": a.nodes, "start": a.start, "stop": a.stop, "mass_threshold_msun_h": a.mass_threshold, "snapnum": a.snapnum, "boxsize_mpc_h": a.boxsize, "parser_sha256": parser_sha, "rows": rows, "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "scope": "reconstruct positions and masses from official Quijote FoF group_tab; no model fit"}
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"status": out["status"], "n_rows": len(rows), "writes": sum(x["status"] == "WRITE" for x in rows), "parser_sha256": parser_sha}))

if __name__ == "__main__":
    main()
