#!/usr/bin/env python
"""Measure mu1, mu2, the Wick pieces and binned P_h for a block of realizations.

    python scripts/measure.py --node fiducial --start 0 --stop 500
    python scripts/measure.py --node poisson --start 0 --stop 10 --nmesh 256   # Poisson control (seeds)

Writes results/measurements/n{N}/{node}_real{start}-real{stop-1}.npz.
"""
import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

from momentpng import products
from momentpng.catalogs import load_positions, uniform_catalog
from momentpng.config import load_protocol, realization_id
from momentpng.mesh import binned_power, cic_paint, lattice, mode_power
from momentpng.moments import field_moments


def measure_one(job):
    proto, node, i, nmesh = job
    box = proto.boxsize
    if node == "poisson":
        pos = uniform_catalog(i, int(proto.raw["poisson_control"]["nhalo"]), box)
    else:
        pos = load_positions(proto.path("catalogs"), node, i)
    delta = cic_paint(pos, nmesh, box)
    row = field_moments(delta, box, proto.scales, proto.shell_width)
    dk, kmax = proto.power_bins
    k, pk, nmodes = binned_power(mode_power(delta, box), lattice(nmesh, box).k, dk, kmax)
    row.update(P_h=pk, n_halo=len(pos))
    return row, k, nmodes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--node", required=True, help="fiducial | LC_m | LC_p | poisson")
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--stop", type=int, required=True)
    ap.add_argument("--nmesh", type=int, default=None, help="default: protocol primary grid")
    ap.add_argument("--workers", type=int, default=1, help="processes (keep <= 6 on login nodes)")
    ap.add_argument("--protocol", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.protocol)
    nmesh = a.nmesh or proto.nmesh
    fnl = 0.0 if a.node == "poisson" else proto.nodes[a.node]
    jobs = [(proto, a.node, i, nmesh) for i in range(a.start, a.stop)]
    t0 = time.time()
    if a.workers > 1:
        with ProcessPoolExecutor(a.workers) as ex:
            out = list(ex.map(measure_one, jobs, chunksize=4))
    else:
        out = [measure_one(j) for j in jobs]
    rows = [o[0] for o in out]
    path = products.block_path(proto.results, nmesh, a.node, a.start, a.stop)
    products.save_block(path, rows, [realization_id(i) for i in range(a.start, a.stop)],
                        {"s": proto.scales, "k": out[0][1], "nmodes": out[0][2], "fNL": fnl,
                         "nmesh": nmesh, "boxsize": proto.boxsize, "shell_width": proto.shell_width})
    print(f"{path}  ({len(rows)} realizations, {time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
