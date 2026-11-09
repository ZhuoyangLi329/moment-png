#!/usr/bin/env python
"""Connected mu2 = mu2 - mu2_G: Poisson contact control, halo excess, resolution, PNG response.

Uses realizations real000-real009 at every grid (and the Poisson seeds), plus the
primary-grid train+holdout block for the normalised response R = mu2/mu2_G - 1.

  1. Poisson control: measured connected mu2 vs the iid and exact-CIC contact terms.
  2. Halo excess: halo connected mu2 minus the CIC Poisson contact at the halo nbar.
  3. Grid stability: |<x_N> - <x_64>| for mu1 (tol 2e-4) and connected mu2 (tol 1e-4),
     paired realizations; reports the longest contiguous shell run common to all nodes/grids.
  4. Odd PNG response of R per grid.
"""
import argparse

import numpy as np

from momentpng import products
from momentpng.config import load_protocol, write_json
from momentpng.moments import shell_kernel
from momentpng.theory.contact import poisson_contact_cic, poisson_contact_iid

TOL = {"mu1": 2e-4, "mu2_connected": 1e-4}


def longest_run(shells, step):
    best, cur = [], []
    for x in sorted(shells):
        cur = cur + [x] if cur and abs(x - cur[-1] - step) < 1e-6 else [x]
        best = cur if len(cur) > len(best) else best
    return best


def pulls(samples, model):
    mean = samples.mean(0)
    se = samples.std(0, ddof=1) / np.sqrt(len(samples))
    p = (mean - model) / se
    return {"mean": mean, "model": model, "se": se, "pull": p, "rms_pull": float(np.sqrt(np.mean(p**2))),
            "max_abs_pull": float(np.max(np.abs(p)))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nreal", type=int, default=10, help="realizations/seeds used at every grid")
    ap.add_argument("--protocol", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.protocol)
    s, w, box = proto.scales, proto.shell_width, proto.boxsize
    grids = [proto.nmesh] + list(proto.raw["estimator"]["nmesh_resolution"])
    ids = list(range(a.nreal))
    out = {"s": s, "grids": grids, "poisson": {}, "halo_excess": {}, "stability": {}, "response_R": {}}

    contact = {}
    for n in grids:
        pc = products.load(proto.results, n, "poisson", ids)
        lam = float(np.mean(pc["n_halo"])) * (box / n) ** 3 / box**3
        kern = [shell_kernel(n, box, float(x), w) for x in s]
        iid = np.array([poisson_contact_iid(k, lam) for k in kern])
        cic = np.array([poisson_contact_cic(k, lam) for k in kern])
        contact[n] = kern
        out["poisson"][n] = {"lambda_cell": lam, "iid": pulls(pc["mu2_connected"], iid),
                             "cic": pulls(pc["mu2_connected"], cic)}
        print(f"Poisson n{n}: rms pull iid={out['poisson'][n]['iid']['rms_pull']:.2f}  "
              f"cic={out['poisson'][n]['cic']['rms_pull']:.2f}")

    data = {(node, n): products.load(proto.results, n, node, ids) for node in proto.nodes for n in grids}
    for node in proto.nodes:
        out["halo_excess"][node] = {}
        for n in grids:
            d = data[(node, n)]
            lam = float(np.mean(d["n_halo"])) * (box / n) ** 3 / box**3
            cic = np.array([poisson_contact_cic(k, lam) for k in contact[n]])
            iid = np.array([poisson_contact_iid(k, lam) for k in contact[n]])
            out["halo_excess"][node][n] = {"vs_cic": pulls(d["mu2_connected"], cic),
                                           "vs_iid": pulls(d["mu2_connected"], iid)}
        print(f"halo excess {node:8s}: rms pull vs CIC contact " +
              "  ".join(f"n{n}={out['halo_excess'][node][n]['vs_cic']['rms_pull']:.2f}" for n in grids))

    step = float(s[1] - s[0])
    for obs, tol in TOL.items():
        common = set(map(float, s))
        per = {}
        for node in proto.nodes:
            for n in grids[1:]:
                diff = data[(node, n)][obs].mean(0) - data[(node, grids[0])][obs].mean(0)
                ok = [float(x) for x, d_ in zip(s, diff) if abs(d_) <= tol]
                common &= set(ok)
                per[f"{node}_n{n}"] = {"mean_difference": diff, "stable_shells": ok}
        run = longest_run(common, step)
        out["stability"][obs] = {"tolerance": tol, "per_node_grid": per, "common_stable": sorted(common),
                                 "longest_contiguous": run}
        print(f"stability {obs}: longest common contiguous run {run}")

    fp, fm = proto.nodes["LC_p"], proto.nodes["LC_m"]
    for n in grids:
        R = {node: data[(node, n)]["mu2"] / data[(node, n)]["mu2_gaussian"] - 1 for node in ("LC_m", "LC_p")}
        odd = (R["LC_p"] - R["LC_m"]) / (fp - fm)
        out["response_R"][n] = {"n": a.nreal, "mean": odd.mean(0), "se": odd.std(0, ddof=1) / np.sqrt(len(odd))}
    first = list(proto.block("train")) + list(proto.block("holdout"))
    R = {node: (lambda d: d["mu2"] / d["mu2_gaussian"] - 1)(products.load(proto.results, proto.nmesh, node, first))
         for node in ("LC_m", "LC_p")}
    odd = (R["LC_p"] - R["LC_m"]) / (fp - fm)
    out["response_R"]["primary_train_holdout"] = {"n": len(first), "mean": odd.mean(0),
                                                  "se": odd.std(0, ddof=1) / np.sqrt(len(odd))}
    print("odd dR/dfNL at s=%g: " % s[0] + "  ".join(f"n{n}={out['response_R'][n]['mean'][0]:.3e}" for n in grids))

    path = write_json(proto.results / "mu2_connected.json", out, a)
    print(path)


if __name__ == "__main__":
    main()
