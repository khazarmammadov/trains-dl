"""Train/test splits shared by DL-Learner and the ML baselines.

* michalski10, michie24 : leave-one-out (10 and 24 folds) -- too few trains
                          for k-fold; metrics are computed on the pooled
                          predictions of all folds.
* synthetic200(_noise10): stratified 5-fold CV (seed 0).

Splits are written to data/splits/<dataset>.json as
{"folds": [{"train": [ids], "test": [ids]}, ...]}
"""
from __future__ import annotations

import json
from pathlib import Path

from sklearn.model_selection import LeaveOneOut, StratifiedKFold

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
SPLITS = ROOT / "data" / "splits"

DATASETS = ["michalski10", "michie24", "synthetic200", "synthetic200_noise10"]


def load_dataset(name: str) -> dict:
    return json.loads((PROC / f"{name}.json").read_text())


def make_splits(name: str) -> list[dict]:
    ds = load_dataset(name)
    ids = [t["id"] for t in ds["trains"]]
    y = [t["label"] for t in ds["trains"]]
    if len(ids) <= 30:
        it = LeaveOneOut().split(ids)
    else:
        it = StratifiedKFold(n_splits=5, shuffle=True, random_state=0).split(ids, y)
    return [{"train": [ids[i] for i in tr], "test": [ids[i] for i in te]} for tr, te in it]


def load_splits(name: str) -> list[dict]:
    return json.loads((SPLITS / f"{name}.json").read_text())["folds"]


def main() -> None:
    SPLITS.mkdir(parents=True, exist_ok=True)
    for name in DATASETS:
        folds = make_splits(name)
        (SPLITS / f"{name}.json").write_text(json.dumps({"folds": folds}, indent=1))
        print(f"{name:22s} folds={len(folds)} test sizes={sorted({len(f['test']) for f in folds})}")


if __name__ == "__main__":
    main()
