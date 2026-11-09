#!/usr/bin/env python
"""Empirical fNL inference baseline from [mu1, R_mu2 - 1] with held-out coverage.

The mean model is *emulated* from training means of the three nodes,
    m(f) = m0 + f * (m_+ - m_-)/200 + f^2 * ((m_+ + m_-)/2 - m0)/100^2,
and the covariance is the fiducial training sample covariance with diagonal
shrinkage. Each held-out realization gets a gridded posterior under a Gaussian
or a Sellentin-Heavens multivariate-t likelihood. This is the statistical
baseline for constraining power, not the analytic model.

    python scripts/fnl_likelihood.py --shrink 0.2
"""
import argparse

import numpy as np

from momentpng import products
from momentpng.config import load_protocol, write_json
from momentpng.stats import posterior_summary


def features(d, observables):
    cols = {"mu1": d["mu1"], "R": d["mu2"] / d["mu2_gaussian"] - 1, "mu2": d["mu2"]}
    return np.column_stack([cols[o] for o in observables])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--observables", nargs="+", default=["mu1", "R"], help="subset of mu1 R mu2")
    ap.add_argument("--shrink", type=float, default=0.2)
    ap.add_argument("--grid", type=float, nargs=3, default=[-200, 200, 1601])
    ap.add_argument("--protocol", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.protocol)
    train, hold = list(proto.block("train")), list(proto.block("holdout"))
    X = {node: features(products.load(proto.results, proto.nmesh, node, train + hold), a.observables)
         for node in proto.nodes}
    n = len(train)
    fp, fm = proto.nodes["LC_p"], proto.nodes["LC_m"]
    m0 = X["fiducial"][:n].mean(0)
    mp, mm = X["LC_p"][:n].mean(0), X["LC_m"][:n].mean(0)
    lin = (mp - mm) / (fp - fm)
    quad = ((mp + mm) / 2 - m0) / fp**2
    C = np.cov(X["fiducial"][:n], rowvar=False, ddof=1)
    C = (1 - a.shrink) * C + a.shrink * np.diag(np.diag(C))
    Ci = np.linalg.inv(C)
    grid = np.linspace(a.grid[0], a.grid[1], int(a.grid[2]))
    model = m0[None, :] + grid[:, None] * lin[None, :] + grid[:, None] ** 2 * quad[None, :]

    res = {}
    for node, truth in proto.nodes.items():
        res[node] = {}
        for like in ("gaussian", "student_t"):
            rows = []
            for x in X[node][n:]:
                r = x[None, :] - model
                chi2 = np.einsum("gi,ij,gj->g", r, Ci, r)
                ll = -0.5 * chi2 if like == "gaussian" else -0.5 * n * np.log1p(chi2 / (n - 1))
                rows.append(posterior_summary(grid, ll))
            rows = np.asarray(rows)
            cover = float(np.mean((rows[:, 1] <= truth) & (truth <= rows[:, 2])))
            res[node][like] = {"true_fNL": truth, "mean_median": float(rows[:, 0].mean()),
                               "scatter_median": float(rows[:, 0].std(ddof=1)),
                               "mean_halfwidth_68": float(np.mean((rows[:, 2] - rows[:, 1]) / 2)),
                               "coverage_68": cover, "intervals": rows}
            print(f"{node:8s} {like:9s} median={rows[:, 0].mean():7.1f}  "
                  f"<sigma>={res[node][like]['mean_halfwidth_68']:5.1f}  68% coverage={cover:.2f}")

    tag = "_".join(a.observables)
    path = write_json(proto.results / f"fnl_likelihood_{tag}.json",
                      {"observables": a.observables, "shrink": a.shrink, "n_train": n,
                       "n_holdout": len(hold), "results": res}, a)
    print(path)


if __name__ == "__main__":
    main()
