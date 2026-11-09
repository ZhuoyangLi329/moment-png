#!/usr/bin/env python
"""Matter field from the z=1 DM snapshots: P_mm, P_hm and the matter shell moments (plan A2).

For each realization the 512^3 particles are CIC-assigned file by file (constant memory),
then the same estimator as for halos is applied. Writes a product with node="matter_<node>":
P_h holds P_mm, P_cross holds the halo x matter cross power, n_halo the particle count.

    python scripts/matter_fields.py --node fiducial --start 100 --stop 133 --config configs/explore_z1.yaml
"""
import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import h5py
import hdf5plugin
import numpy as np

from momentpng import products
from momentpng.catalogs import load_positions
from momentpng.config import load_protocol, realization_id
from momentpng.mesh import binned_power, cic_counts, cic_paint, lattice, mode_cross_power, mode_power
from momentpng.moments import field_moments, valid_scales

hdf5plugin.register()  # Blosc filter used by the compressed Quijote snapshots


def matter_delta(proto, node, i, nmesh):
    snap = proto.path("dm") / node / str(i) / "snapdir_002"
    files = sorted(snap.glob("snap_002.*.hdf5"), key=lambda p: int(p.name.split(".")[1]))
    if not files:
        raise FileNotFoundError(snap)
    grid, npart = None, 0
    for f in files:
        with h5py.File(f, "r") as h:
            unit = float(h["Header"].attrs["BoxSize"]) / proto.boxsize      # kpc/h -> Mpc/h
            pos = np.mod(h["PartType1/Coordinates"][:].astype(np.float64) / unit, proto.boxsize)
        grid = cic_counts(pos, nmesh, proto.boxsize, grid)
        npart += len(pos)
    return grid / grid.mean() - 1.0, npart


def one(job):
    proto, node, i, nmesh, scales = job
    box = proto.boxsize
    dm, npart = matter_delta(proto, node, i, nmesh)
    dh = cic_paint(load_positions(proto.path("catalogs"), node, i), nmesh, box)
    row = field_moments(dm, box, scales, proto.shell_width)
    dk, kmax = proto.power_bins
    kmag = lattice(nmesh, box).k
    k, pmm, nm = binned_power(mode_power(dm, box), kmag, dk, kmax)
    row.update(P_h=pmm, P_cross=binned_power(mode_cross_power(dh, dm, box), kmag, dk, kmax)[1], n_halo=npart)
    return row, k, nm


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--node", required=True)
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--stop", type=int, required=True)
    ap.add_argument("--nmesh", type=int, default=None)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--config", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.config)
    nmesh = a.nmesh or proto.nmesh
    scales = valid_scales(nmesh, proto.boxsize, proto.scales, proto.shell_width)
    jobs = [(proto, a.node, i, nmesh, scales) for i in range(a.start, a.stop)]
    t0 = time.time()
    if a.workers > 1:
        with ProcessPoolExecutor(a.workers) as ex:
            out = list(ex.map(one, jobs))
    else:
        out = [one(j) for j in jobs]
    path = products.block_path(proto.results, nmesh, f"matter_{a.node}", a.start, a.stop)
    products.save_block(path, [o[0] for o in out], [realization_id(i) for i in range(a.start, a.stop)],
                        {"s": scales, "k": out[0][1], "nmodes": out[0][2], "fNL": proto.fnl(a.node),
                         "nmesh": nmesh, "boxsize": proto.boxsize, "shell_width": proto.shell_width})
    print(f"{path}  ({len(out)} realizations, {time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
