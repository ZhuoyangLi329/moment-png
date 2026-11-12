#!/usr/bin/env python
"""Gaussian-field mocks that calibrate the simulation-Fisher machinery (configs/gauss_mock.yaml).

On the lattice, with g1..g4 independent unit white noises shared by all nodes of a realization,
    delta = b(k) sqrt(P_m) g1 + sqrt(S) g2 [+ sqrt(e1) g3 + sqrt(e2) g4],   b(k) = b1 + fNL (bphi/M + db1),
sharply cut at |k| <= kcut, with S = 1/nbar of the halo sample. P is then a sufficient statistic, so no
combination with moments may beat the exact mode-level P Fisher printed at the end: any apparent gain
is a defect of the estimator. Nodes fiducial / LC_p / LC_m (fNL = 0, +-100) and nuisance variants that
mimic the halo ones, nested in two steps (extra shot noise is an independent added component, like
thinning): '_m1' (b1 + 0.1, S + 0.2 S), '_m2' (b1 + 0.2, S + 0.4 S), '_d1' (S + 0.25 S), '_d2' (S + 0.5 S).

    python scripts/gaussian_mocks.py --kcut 0.08
    python scripts/information.py --config configs/gauss_mock.yaml --variant _kc0.08 --kmax 0.08 --smin 10 \\
        --sets P P+mu2G P+mu2 P+mu1+mu2+mu3 --nuisance _m1_kc0.08:_m2_kc0.08 _d1_kc0.08:_d2_kc0.08 --cv 5
"""
import argparse
import os
from concurrent.futures import ProcessPoolExecutor

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

from momentpng import products
from momentpng.config import load_protocol, realization_id
from momentpng.mesh import binned_power, lattice, mode_power
from momentpng.moments import field_moments, valid_scales
from momentpng.theory.inputs import load_table, on_lattice

B1, BPHI, DB1, NHALO = 2.756, 4.896, -3.868e-4, 195535
# node/variant -> (fNL, b1, extra shot in units of S: first and second nested component)
CASES = {("fiducial", ""): (0, B1, 0, 0), ("LC_p", ""): (100, B1, 0, 0), ("LC_m", ""): (-100, B1, 0, 0),
         ("fiducial", "_m1"): (0, B1 + 0.1, 0.2, 0), ("fiducial", "_m2"): (0, B1 + 0.2, 0.2, 0.2),
         ("fiducial", "_d1"): (0, B1, 0.25, 0), ("fiducial", "_d2"): (0, B1, 0.25, 0.25)}


def setup(proto, nmesh, kcut):
    lat = lattice(nmesh, proto.boxsize)
    pm, M = on_lattice(load_table(proto.path("theory_table")), lat)
    keep = (lat.k <= kcut) & ~lat.zero
    return lat, pm, M, keep, NHALO / proto.boxsize**3


def one(job):
    proto, nmesh, kcut, scales, i = job
    lat, pm, M, keep, nbar = setup(proto, nmesh, kcut)
    box, shot = proto.boxsize, 1.0 / nbar
    rng = np.random.default_rng([i, 777])
    g = [np.fft.fftn(rng.normal(size=(nmesh,) * 3)) for _ in range(4)]
    amp = lambda power: np.sqrt(power * nmesh**3 / box**3) * keep
    out = {}
    for key, (fnl, b1, e1, e2) in CASES.items():
        b = b1 + fnl * (BPHI / M + DB1)
        dk = g[0] * amp(b**2 * pm) + g[1] * amp(shot) + g[2] * amp(e1 * shot) + g[3] * amp(e2 * shot)
        delta = np.fft.ifftn(dk).real
        row = field_moments(delta, box, scales, proto.shell_width)
        row.update(P_h=binned_power(mode_power(delta, box), lat.k, proto.power_edges)[1], n_halo=NHALO)
        out[key] = row
    return out


def exact_p_fisher(proto, nmesh, kcut):
    """Mode-level Fisher of the Gaussian power for (fNL, b1, S): sigma(fNL) unmarginalised / marginalised."""
    lat, pm, M, keep, nbar = setup(proto, nmesh, kcut)
    p = B1**2 * pm + 1 / nbar
    d = [2 * B1 * (BPHI / M + DB1) * pm, 2 * B1 * pm, np.ones_like(pm)]
    F = np.array([[0.5 * np.sum((a * b / p**2)[keep]) for b in d] for a in d])
    return 1 / np.sqrt(F[0, 0]), np.sqrt(np.linalg.inv(F)[0, 0])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kcut", type=float, default=0.08)
    ap.add_argument("--nmesh", type=int, default=64)
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--config", default="configs/gauss_mock.yaml")
    a = ap.parse_args()

    proto = load_protocol(a.config)
    scales = valid_scales(a.nmesh, proto.boxsize, proto.scales, proto.shell_width)
    jobs = [(proto, a.nmesh, a.kcut, scales, i) for i in range(a.n)]
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(one, jobs, chunksize=10))
    k, _, nmodes = binned_power(np.zeros((a.nmesh,) * 3), lattice(a.nmesh, proto.boxsize).k, proto.power_edges)
    ids = [realization_id(i) for i in range(a.n)]
    for node, var in CASES:
        path = products.block_path(proto.results, a.nmesh, node, 0, a.n, f"{var}_kc{a.kcut:g}")
        products.save_block(path, [r[(node, var)] for r in res], ids,
                            {"s": scales, "k": k, "nmodes": nmodes, "fNL": proto.fnl(node), "nmesh": a.nmesh,
                             "boxsize": proto.boxsize, "shell_width": proto.shell_width})
        print(path)
    u, m = exact_p_fisher(proto, a.nmesh, a.kcut)
    print(f"exact mode-level P Fisher: sigma(fNL) = {u:.2f} unmarginalised, {m:.2f} marginalised over (b1, S)")


if __name__ == "__main__":
    main()
