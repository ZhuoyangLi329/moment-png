"""Protocol loading and realization bookkeeping."""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml

REPO = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = REPO / "configs" / "protocol.yaml"


def realization_id(i: int) -> str:
    return f"real{int(i):03d}"


def realization_index(rid: str) -> int:
    return int(str(rid).removeprefix("real"))


@dataclass(frozen=True)
class Protocol:
    raw: dict

    @property
    def boxsize(self) -> float:
        return float(self.raw["sample"]["boxsize"])

    @property
    def nodes(self) -> dict[str, float]:
        return {k: float(v) for k, v in self.raw["nodes"].items()}

    @property
    def scales(self) -> np.ndarray:
        return np.asarray(self.raw["estimator"]["scales"], dtype=float)

    @property
    def shell_width(self) -> float:
        return float(self.raw["estimator"]["shell_width"])

    @property
    def nmesh(self) -> int:
        return int(self.raw["estimator"]["nmesh"])

    @property
    def power_bins(self) -> tuple[float, float]:
        b = self.raw["estimator"]["power_bins"]
        return float(b["dk"]), float(b["kmax"])

    def block(self, name: str) -> range:
        """Realization indices of a named split block ('train', 'holdout', 'disjoint')."""
        start, stop = self.raw["split"][name]
        return range(int(start), int(stop))

    def path(self, key: str) -> Path:
        p = Path(self.raw["paths"][key])
        return p if p.is_absolute() else REPO / p

    @property
    def results(self) -> Path:
        return self.path("results")

    @property
    def bias(self) -> dict:
        return self.raw["bias"]


def load_protocol(path: str | Path | None = None) -> Protocol:
    path = Path(path) if path else DEFAULT_PROTOCOL
    return Protocol(yaml.safe_load(path.read_text()))


def git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"],
                               capture_output=True, text=True, check=True).stdout.strip()
        return out + ("-dirty" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return None


def write_json(path: str | Path, payload: dict, args=None) -> Path:
    """Write a result JSON with a minimal provenance header (commit + CLI arguments)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    header = {"git_commit": git_commit()}
    if args is not None:
        header["arguments"] = {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()}
    path.write_text(json.dumps({"provenance": header, **payload}, indent=2, default=_jsonable) + "\n")
    return path


def _jsonable(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, Path):
        return str(x)
    raise TypeError(f"not JSON serialisable: {type(x)}")
