#!/usr/bin/env python3
"""Load canonical fiducial/LC_m/LC_p N-body products into one theory-ready array."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

NODES = ("fiducial", "LC_m", "LC_p")
REQUIRED = ("realization_ids", "s", "k", "P_h", "nmodes", "mu1", "mu2", "mu2_gaussian", "mu2_connected", "R_mu2", "fNL")

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def load_node(path):
    with np.load(path, allow_pickle=False) as d:
        missing = [k for k in REQUIRED if k not in d]
        if missing:
            raise ValueError(f"{path}: missing required arrays {missing}")
        return {k: np.asarray(d[k]) for k in REQUIRED}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True, help="directory containing nbody_<node>_n<N>.npz")
    ap.add_argument("--nmesh", type=int, default=64)
    ap.add_argument("--output", type=Path, required=True, help="unified .npz output path")
    args = ap.parse_args()
    arrays = []
    source = {}
    for node in NODES:
        path = args.input / f"nbody_{node}_n{args.nmesh}.npz"
        if not path.exists():
            raise FileNotFoundError(path)
        source[node] = {"path": str(path), "sha256": sha256(path)}
        arrays.append(load_node(path))
    ref = arrays[0]
    ids = np.asarray(ref["realization_ids"]).astype("U")
    s = np.asarray(ref["s"], dtype=float)
    k = np.asarray(ref["k"], dtype=float)
    for node, d in zip(NODES, arrays):
        got_ids = np.asarray(d["realization_ids"]).astype("U")
        if not np.array_equal(got_ids, ids):
            raise ValueError(f"{node}: realization IDs differ from fiducial")
        if not np.array_equal(np.asarray(d["s"], dtype=float), s) or not np.array_equal(np.asarray(d["k"], dtype=float), k):
            raise ValueError(f"{node}: shell or k grid differs from fiducial")
        n = len(ids)
        for key in ("P_h", "mu1", "mu2", "mu2_gaussian", "mu2_connected", "R_mu2"):
            if d[key].shape[0] != n:
                raise ValueError(f"{node}: {key} realization axis has shape {d[key].shape}, expected {n}")
    def stack(key):
        return np.stack([np.asarray(d[key]) for d in arrays], axis=0)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, node_names=np.asarray(NODES), fNL=np.asarray([float(d["fNL"]) for d in arrays]), realization_ids=ids, s=s, k=k, P_h=stack("P_h"), nmodes=stack("nmodes"), mu1=stack("mu1"), mu2=stack("mu2"), mu2_gaussian=stack("mu2_gaussian"), mu2_connected=stack("mu2_connected"), R_mu2=stack("R_mu2"))
    summary = {"schema":"nbody_unified_v1", "status":"PASS", "nmesh":args.nmesh, "nodes":list(NODES), "nreal":int(len(ids)), "n_s":int(len(s)), "n_k":int(len(k)), "fNL":[float(d["fNL"]) for d in arrays], "dtypes":{key:[str(np.asarray(d[key]).dtype) for d in arrays] for key in ("P_h","mu1","mu2","mu2_gaussian","mu2_connected","R_mu2")}, "source":source, "output":str(args.output), "scope":"one-command unified theory-ready N-body arrays; no PNG response fit"}
    meta = args.output.with_suffix(args.output.suffix + ".json")
    meta.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"status":"PASS", "output":str(args.output), "nodes":list(NODES), "nreal":len(ids), "n_s":len(s), "n_k":len(k)}))

if __name__ == "__main__":
    main()
