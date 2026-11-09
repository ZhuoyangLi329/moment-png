#!/usr/bin/env python
"""Held-out test of the tree-level mu1 model at every native fNL node.

Parameters are supplied, never fitted here. Two tests per run:
  * absolute: held-out mean mu1(s) of each node vs the tree prediction;
  * response: paired held-out (LC_p - LC_m)/200 vs the predicted odd response
    (insensitive to b1 / P_shot calibration errors that cancel between nodes).
The covariance of the held-out mean is estimated from the independent calibration
realizations (--cov-blocks, default train+disjoint), scaled to the held-out size.
Pass criterion (pre-declared): Hartlap chi2 p-value > 0.01 for every node and the response.

    python scripts/validate_mu1.py --b1 2.756 --pshot poisson --bphi 5.0 --db1 -4e-4 --tag A3
    python scripts/validate_mu1.py --b1 2.7413 --pshot 5467.8 --bphi-universal 1.12 --tag universal
"""
import argparse

import numpy as np

from momentpng import products
from momentpng.config import load_protocol, write_json
from momentpng.mesh import lattice
from momentpng.stats import compare
from momentpng.theory.inputs import load_table, on_lattice
from momentpng.theory.tree import mu1_tree, universal_bphi

P_PASS = 0.01


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--b1", type=float, required=True)
    ap.add_argument("--pshot", default="0", help="value, or 'poisson' for 1/nbar of the fiducial holdout")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--bphi", type=float)
    g.add_argument("--bphi-universal", type=float, metavar="P", help="use bphi = 2 delta_c (b1 - P)")
    ap.add_argument("--db1", type=float, default=0.0, help="scale-independent PNG bias d b1 / d fNL")
    ap.add_argument("--convention", default="cic_both")
    ap.add_argument("--block", default="holdout")
    ap.add_argument("--cov-blocks", default="train+disjoint", help="'self' to use the held-out scatter")
    ap.add_argument("--extra-nodes", nargs="*", default=[], help="out-of-sample nodes to add, e.g. LC_m50")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--config", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.config)
    bphi = a.bphi if a.bphi is not None else universal_bphi(a.b1, a.bphi_universal, proto.bias["delta_c"])[0]
    idx = proto.indices(a.block)
    cov_idx = None if a.cov_blocks == "self" else proto.indices(a.cov_blocks)
    nodes = {**proto.nodes, **{n: proto.fnl(n) for n in a.extra_nodes}}
    lat = lattice(proto.nmesh, proto.boxsize)
    pm, M = on_lattice(load_table(proto.path("theory_table")), lat)
    s, w = proto.scales, proto.shell_width
    load = lambda node, ii: products.load(proto.results, proto.nmesh, node, ii)

    hold = {n: load(n, idx) for n in nodes}
    ext = {n: load(n, cov_idx)["mu1"] for n in nodes} if cov_idx else {n: None for n in nodes}
    pshot = (proto.boxsize**3 / float(np.mean(hold["fiducial"]["n_halo"])) if a.pshot == "poisson"
             else float(a.pshot))
    pred = lambda fnl: mu1_tree(lat, pm, M, s, w, a.b1, bphi, fnl, pshot, a.convention, a.db1)

    res = {n: {"fNL": f, **compare(hold[n]["mu1"], pred(f), ext[n])} for n, f in nodes.items()}
    fp, fm = proto.nodes["LC_p"], proto.nodes["LC_m"]
    pair = lambda d: None if d["LC_p"] is None else (d["LC_p"] - d["LC_m"]) / (fp - fm)
    response = compare(pair({n: hold[n]["mu1"] for n in ("LC_p", "LC_m")}),
                       (pred(fp) - pred(fm)) / (fp - fm), pair(ext))
    passed = all(r["p_value"] > P_PASS for r in [*res.values(), response])

    print(f"b1={a.b1}  Pshot={pshot:.1f}  bphi={bphi:.4f}  db1={a.db1:g}  {a.convention}  "
          f"n={len(idx)}  cov from {a.cov_blocks}")
    for node, r in [*res.items(), ("response", response)]:
        print(f"  {node:9s} Hartlap chi2/dof={r['hartlap_chi2_dof']:8.2f}  p={r['p_value']:.3g}  "
              f"rms pull={r['rms_pull']:.2f}")
    print("PASS" if passed else "FAIL", f"(criterion: every p > {P_PASS})")

    tag = a.tag or f"b1{a.b1:g}_bphi{bphi:.3f}_db1{a.db1:g}"
    out = proto.results / f"mu1_validation_{tag}.json"
    write_json(out, {"b1": a.b1, "P_shot": pshot, "bphi": bphi, "db1": a.db1, "convention": a.convention,
                     "block": a.block, "cov_blocks": a.cov_blocks, "s": s, "nodes": res,
                     "response": response, "passed": passed, "p_threshold": P_PASS}, a)
    print(out)


if __name__ == "__main__":
    main()
