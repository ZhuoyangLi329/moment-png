#!/usr/bin/env python
"""Rebuild certified z=1 FoF position catalogs from the Quijote group_tab binaries.

Used to extend LC_m / LC_p from real000-099 to real000-499 (the disjoint block).
Writes positions_mpc_h.npy, masses_msun_h.npy and metadata.json per realization.

    python scripts/reconstruct_catalogs.py --nodes LC_m LC_p --start 100 --stop 500
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

import numpy as np

from momentpng.catalogs import read_group_tab, select_halos
from momentpng.config import load_protocol, realization_id


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nodes", nargs="+", default=["LC_m", "LC_p"])
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--stop", type=int, required=True)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--protocol", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.protocol)
    smp = proto.raw["sample"]
    src_root, dst_root = proto.path("raw_fof"), proto.path("catalogs")
    for node in a.nodes:
        for i in range(a.start, a.stop):
            out = dst_root / node / realization_id(i)
            files = [out / "positions_mpc_h.npy", out / "masses_msun_h.npy", out / "metadata.json"]
            if all(f.exists() for f in files) and not a.overwrite:
                continue
            pos_kpc, mass_code, inputs = read_group_tab(src_root / node / realization_id(i), smp["snapnum"])
            pos, mass = select_halos(pos_kpc, mass_code, float(smp["mass_min"]), proto.boxsize)
            out.mkdir(parents=True, exist_ok=True)
            np.save(files[0], pos)
            np.save(files[1], mass)
            files[2].write_text(json.dumps({
                "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "schema": "fof_positions_metadata_v2", "cosmology": node, "realization": i,
                "input_files": [str(x) for x in inputs], "input_sha256": {str(x): sha256(x) for x in inputs},
                "parser": "moment-png scripts/reconstruct_catalogs.py", "snapnum": smp["snapnum"],
                "redshift": smp["redshift"], "boxsize_mpc_h": proto.boxsize,
                "mass_threshold_msun_h": float(smp["mass_min"]), "n_halo_total": int(len(pos_kpc)),
                "n_halo_selected": int(len(pos)),
                "mass_unit": "Msun/h (GroupMass * 1e10)", "position_unit": "Mpc/h (GroupPos / 1e3)"},
                indent=2) + "\n")
            print(f"{node}/{realization_id(i)}: {len(pos)} halos")


if __name__ == "__main__":
    main()
