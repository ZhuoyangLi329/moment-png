"""Minimal production guardrails for pure analytic PNG predictions."""

from pathlib import Path


def require_provenance(config):
    required = ["bphi_source", "bphidelta_source", "matter_power_source"]
    missing = [x for x in required if not config.get(x)]
    if missing:
        raise RuntimeError(
            "Missing independent theory provenance: " + ", ".join(missing)
        )


def forbid_response_fit(metadata):
    forbidden = ["fit_to_png_response", "fit_fnl", "empirical_response_template"]
    used = [x for x in forbidden if metadata.get(x, False)]
    if used:
        raise RuntimeError(
            "Production analytic mode forbids: " + ", ".join(used)
        )


if __name__ == "__main__":
    print("guardrails module")
