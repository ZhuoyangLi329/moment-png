#!/usr/bin/env python
"""Measure mu1, mu2, mu3, the Wick pieces and binned P_h for a block of realizations.

    python scripts/measure.py --node fiducial --start 0 --stop 500
    python scripts/measure.py --node poisson --start 0 --stop 10 --nmesh 256   # Poisson control (seeds)
    python scripts/measure.py --node LC_p --start 0 --stop 500 --dilute 2      # keep 1/2 of the halos
    python scripts/measure.py --node fiducial --start 0 --stop 500 --mass-min 1.6e13
    python scripts/measure.py --node fiducial --start 0 --stop 500 --kcut 0.08     # moments of the k<=0.08 field

Writes {results}/measurements/n{N}{variant}/{node}_real{start}-real{stop-1}.npz, where the
variant suffix encodes --dilute / --mass-min / --kcut. Shells that are empty on the grid are dropped.
"""
import argparse
import os
import time
import zlib
from concurrent.futures import ProcessPoolExecutor

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

from momentpng import products
from momentpng.catalogs import load_positions, positions_path, uniform_catalog
from momentpng.config import load_protocol, realization_id
from momentpng.mesh import binned_power, cic_paint, lattice, mode_power
from momentpng.moments import field_moments, valid_scales


def variant_tag(dilute: float, mass_min: float | None, kcut: float | None = None) -> str:
    tag = f"_d{dilute:g}" if dilute != 1 else ""
    tag += f"_m{mass_min:.3g}" if mass_min else ""
    return tag + (f"_kc{kcut:g}" if kcut else "")


def catalog(proto, node, i, dilute, mass_min):
    box = proto.boxsize
    if node == "poisson":
        pos = uniform_catalog(i, int(proto.raw["poisson_control"]["nhalo"]), box)
    else:
        pos = load_positions(proto.path("catalogs"), node, i)
        if mass_min:
            mass = np.load(positions_path(proto.path("catalogs"), node, i).with_name("masses_msun_h.npy"))
            pos = pos[mass >= mass_min]
    if dilute != 1:
        rng = np.random.default_rng([i, zlib.crc32(node.encode()), 20261109])
        pos = pos[rng.random(len(pos)) < 1.0 / dilute]
    return pos


def measure_one(job):
    proto, node, i, nmesh, scales, dilute, mass_min, kcut = job
    box = proto.boxsize
    pos = catalog(proto, node, i, dilute, mass_min)
    delta = cic_paint(pos, nmesh, box)
    if kcut:  # sharp low-pass: moments and P then use exactly the same Fourier modes
        delta = np.fft.ifftn(np.fft.fftn(delta) * (lattice(nmesh, box).k <= kcut)).real
    row = field_moments(delta, box, scales, proto.shell_width)
    k, pk, nmodes = binned_power(mode_power(delta, box), lattice(nmesh, box).k, proto.power_edges)
    row.update(P_h=pk, n_halo=len(pos))
    return row, k, nmodes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--node", required=True, help="fiducial | LC_m | LC_p | LC_m50 | poisson")
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--stop", type=int, required=True)
    ap.add_argument("--nmesh", type=int, default=None, help="default: protocol primary grid")
    ap.add_argument("--dilute", type=float, default=1.0, help="keep each halo with probability 1/dilute")
    ap.add_argument("--mass-min", type=float, default=None, help="raise the halo mass cut [Msun/h]")
    ap.add_argument("--kcut", type=float, default=None, help="sharp low-pass |k| <= kcut before measuring [h/Mpc]")
    ap.add_argument("--workers", type=int, default=1, help="processes (keep <= 6 on login nodes)")
    ap.add_argument("--protocol", "--config", dest="protocol", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.protocol)
    nmesh = a.nmesh or proto.nmesh
    fnl = proto.fnl(a.node)
    scales = valid_scales(nmesh, proto.boxsize, proto.scales, proto.shell_width)
    if len(scales) < len(proto.scales):
        print(f"dropping empty shells at n{nmesh}: {sorted(set(proto.scales) - set(scales))}")
    jobs = [(proto, a.node, i, nmesh, scales, a.dilute, a.mass_min, a.kcut) for i in range(a.start, a.stop)]
    t0 = time.time()
    if a.workers > 1:
        with ProcessPoolExecutor(a.workers) as ex:
            out = list(ex.map(measure_one, jobs, chunksize=4))
    else:
        out = [measure_one(j) for j in jobs]
    rows = [o[0] for o in out]
    path = products.block_path(proto.results, nmesh, a.node, a.start, a.stop, variant_tag(a.dilute, a.mass_min, a.kcut))
    products.save_block(path, rows, [realization_id(i) for i in range(a.start, a.stop)],
                        {"s": scales, "k": out[0][1], "nmodes": out[0][2], "fNL": fnl,
                         "nmesh": nmesh, "boxsize": proto.boxsize, "shell_width": proto.shell_width})
    print(f"{path}  ({len(rows)} realizations, {time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
