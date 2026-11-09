#!/usr/bin/env python
"""Held-out test of the tree-level mu1 model at every native fNL node.

Parameters are supplied, never fitted here. Two tests per run:
  * absolute: held-out mean mu1(s) of each node vs the tree prediction;
  * response: paired held-out (LC_p - LC_m)/200 vs the predicted odd response
    (insensitive to b1 / P_shot calibration errors that cancel between nodes).

    python scripts/validate_mu1.py --b1 2.7413 --pshot 5467.8 --bphi 3.764 --tag training
    python scripts/validate_mu1.py --b1 2.7413 --pshot 5467.8 --bphi-universal 1.12 --tag universal
"""
import argparse

from momentpng import products
from momentpng.config import load_protocol, write_json
from momentpng.mesh import lattice
from momentpng.stats import compare
from momentpng.theory.inputs import load_table, on_lattice
from momentpng.theory.tree import mu1_tree, universal_bphi


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--b1", type=float, required=True)
    ap.add_argument("--pshot", type=float, default=0.0)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--bphi", type=float)
    g.add_argument("--bphi-universal", type=float, metavar="P", help="use bphi = 2 delta_c (b1 - P)")
    ap.add_argument("--convention", default="cic_both")
    ap.add_argument("--block", default="holdout")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--protocol", default=None)
    a = ap.parse_args()

    proto = load_protocol(a.protocol)
    bphi = a.bphi if a.bphi is not None else universal_bphi(a.b1, a.bphi_universal, proto.bias["delta_c"])[0]
    idx = list(proto.block(a.block))
    lat = lattice(proto.nmesh, proto.boxsize)
    pm, M = on_lattice(load_table(proto.path("theory_table")), lat)
    s, w = proto.scales, proto.shell_width
    pred = lambda fnl: mu1_tree(lat, pm, M, s, w, a.b1, bphi, fnl, a.pshot, a.convention)

    data = {node: products.load(proto.results, proto.nmesh, node, idx)["mu1"] for node in proto.nodes}
    nodes = {}
    for node, fnl in proto.nodes.items():
        nodes[node] = {"fNL": fnl, **compare(data[node], pred(fnl))}
    fp, fm = proto.nodes["LC_p"], proto.nodes["LC_m"]
    response = compare((data["LC_p"] - data["LC_m"]) / (fp - fm), (pred(fp) - pred(fm)) / (fp - fm))

    print(f"b1={a.b1}  Pshot={a.pshot}  bphi={bphi:.4f}  convention={a.convention}  n={len(idx)}")
    for node, r in nodes.items():
        print(f"  {node:8s} chi2/dof={r['chi2_dof']:8.2f}  Hartlap={r['hartlap_chi2_dof']:7.2f}  rms pull={r['rms_pull']:.2f}")
    print(f"  response chi2/dof={response['chi2_dof']:8.2f}  Hartlap={response['hartlap_chi2_dof']:7.2f}  "
          f"rms pull={response['rms_pull']:.2f}")

    tag = a.tag or f"b1{a.b1:g}_bphi{bphi:.3f}"
    out = proto.results / f"mu1_validation_{tag}.json"
    write_json(out, {"b1": a.b1, "P_shot": a.pshot, "bphi": bphi, "convention": a.convention,
                     "block": a.block, "s": s, "nodes": nodes, "response": response}, a)
    print(out)


if __name__ == "__main__":
    main()
