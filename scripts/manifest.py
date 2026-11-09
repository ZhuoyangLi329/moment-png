#!/usr/bin/env python
"""Inventory the certified position catalogs and check selection metadata and pairing.

    python scripts/manifest.py            # -> results/manifest.json
"""
import argparse

import numpy as np

from momentpng.catalogs import inventory
from momentpng.config import load_protocol, write_json


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--protocol", default=None)
    a = ap.parse_args()
    proto = load_protocol(a.protocol)
    inv = inventory(proto.path("catalogs"), proto.nodes)
    mass_min, snap = float(proto.raw["sample"]["mass_min"]), int(proto.raw["sample"]["snapnum"])
    summary = {}
    for node, rows in inv.items():
        bad = [r["realization"] for r in rows
               if r["dtype"] != "float32" or not r["has_metadata"]
               or float(r["mass_threshold"] or 0) != mass_min or int(r["snapnum"] or -1) != snap]
        nh = np.array([r["n_halo"] for r in rows])
        summary[node] = {"n_realizations": len(rows), "first": rows[0]["realization"] if rows else None,
                         "last": rows[-1]["realization"] if rows else None,
                         "n_halo_mean": float(nh.mean()) if len(nh) else None,
                         "n_halo_min": int(nh.min()) if len(nh) else None,
                         "n_halo_max": int(nh.max()) if len(nh) else None,
                         "metadata_failures": bad}
        print(f"{node:8s} n={len(rows)}  n_halo={nh.mean():.0f} [{nh.min()}, {nh.max()}]  "
              f"metadata failures={len(bad)}")
    ids = [set(r["realization"] for r in inv[n]) for n in proto.nodes]
    paired = sorted(set.intersection(*ids))
    print(f"paired across all nodes: {len(paired)}")
    path = write_json(proto.results / "manifest.json",
                      {"catalogs": proto.path("catalogs"), "nodes": summary, "n_paired": len(paired),
                       "realizations": {n: [(r["realization"], r["n_halo"]) for r in rows] for n, rows in inv.items()}}, a)
    print(path)


if __name__ == "__main__":
    main()
