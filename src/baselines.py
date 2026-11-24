"""Non-symbolic baselines on the same splits as DL-Learner.

A train is relational (variable number of wagons, each with loads), so it has
to be *propositionalised* into a fixed-length vector first. Two standard
encodings:

  positional  one column per (wagon slot, attribute), like UCI's
              trains-transformed.data; missing wagons -> "none"/0
  aggregate   counts over the wagons of each attribute value
              (n_short, n_closed, n_shape=X, n_load=Y, carCount, ...).
              Note: these do NOT contain conjunctions such as
              "number of short AND closed wagons" -- that would hand the
              target concept to the learner.

Models: decision tree (CART, sklearn defaults, random_state=0) and random
forest (200 trees, random_state=0).
Output: results/baseline_runs.csv (same metric columns as dl_runs.csv) and
results/baseline_trees.txt (the full-data decision trees as rules).
"""
from __future__ import annotations

import csv
import sys
import time
from collections import Counter
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, export_text

sys.path.insert(0, str(Path(__file__).resolve().parent))
from splits import DATASETS, load_dataset, load_splits  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
CAR_ATTRS = ["shape", "length", "closed", "wheels", "roof", "double"]


def car_values(c: dict) -> dict:
    v = {a: c[a] for a in CAR_ATTRS if a in c}
    v["nloads"] = len(c["loads"])
    v["load"] = c["loads"][0] if c["loads"] else "none"
    return v


def positional(ds: dict) -> pd.DataFrame:
    max_cars = max(len(t["cars"]) for t in ds["trains"])
    rows = []
    for t in ds["trains"]:
        r = {"carCount": len(t["cars"])}
        cars = sorted(t["cars"], key=lambda c: c["pos"])
        for k in range(max_cars):
            v = car_values(cars[k]) if k < len(cars) else None
            for a in CAR_ATTRS + ["nloads", "load"]:
                if v is None:
                    r[f"car{k + 1}_{a}"] = "none" if a not in ("wheels", "nloads") else 0
                elif a in v:
                    r[f"car{k + 1}_{a}"] = v[a]
        rows.append(r)
    df = pd.DataFrame(rows, index=[t["id"] for t in ds["trains"]])
    cat = [c for c in df.columns if df[c].dtype == object or df[c].dtype == bool]
    df[cat] = df[cat].astype(str)
    return pd.get_dummies(df, columns=cat, dtype=int)


def aggregate(ds: dict) -> pd.DataFrame:
    rows = []
    for t in ds["trains"]:
        cnt: Counter = Counter()
        for c in t["cars"]:
            for a, val in car_values(c).items():
                if a in ("wheels", "nloads"):
                    cnt[f"sum_{a}"] += val
                    cnt[f"max_{a}"] = max(cnt[f"max_{a}"], val)
                else:
                    cnt[f"n_{a}={val}"] += 1
            for l in c["loads"]:
                cnt[f"n_loads_of={l}"] += 1
        cnt["carCount"] = len(t["cars"])
        rows.append(cnt)
    return pd.DataFrame(rows, index=[t["id"] for t in ds["trains"]]).fillna(0).astype(int)


MODELS = {
    "dt": lambda: DecisionTreeClassifier(random_state=0),
    "rf": lambda: RandomForestClassifier(n_estimators=200, random_state=0),
}
ENCODINGS = {"positional": positional, "aggregate": aggregate}


def complexity(model) -> int:
    if isinstance(model, DecisionTreeClassifier):
        return int(model.tree_.node_count)
    return int(sum(e.tree_.node_count for e in model.estimators_))


def main() -> None:
    rows, tree_txt = [], []
    for ds_name in DATASETS:
        ds = load_dataset(ds_name)
        y = pd.Series({t["id"]: t["label"] for t in ds["trains"]})
        folds = load_splits(ds_name)
        for enc_name, enc in ENCODINGS.items():
            X = enc(ds)
            for m_name, make in MODELS.items():
                setting = f"{m_name}_{enc_name}"
                # full-data model (for interpretation)
                full = make().fit(X, y[X.index])
                if m_name == "dt":
                    tree_txt.append(f"===== {setting} on {ds_name} "
                                    f"({full.tree_.node_count} nodes, depth {full.get_depth()})\n"
                                    + export_text(full, feature_names=list(X.columns)))
                for k, f in enumerate(folds):
                    t0 = time.time()
                    m = make().fit(X.loc[f["train"]], y[f["train"]])
                    wall = time.time() - t0
                    p_tr = m.predict(X.loc[f["train"]])
                    p_te = m.predict(X.loc[f["test"]])
                    yt = y[f["test"]].values
                    rows.append({
                        "setting": setting, "dataset": ds_name, "fold": f"fold{k:02d}",
                        "n_train": len(f["train"]), "n_test": len(f["test"]),
                        "train_acc": round(float((p_tr == y[f["train"]].values).mean()), 4),
                        "tp": int(((yt == 1) & (p_te == 1)).sum()),
                        "tn": int(((yt == 0) & (p_te == 0)).sum()),
                        "fp": int(((yt == 0) & (p_te == 1)).sum()),
                        "fn": int(((yt == 1) & (p_te == 0)).sum()),
                        "wall_s": round(wall, 3), "n_features": X.shape[1],
                        "complexity": complexity(m),
                        "test_pred": " ".join(f"{i}:{int(p)}" for i, p in zip(f["test"], p_te)),
                    })
        print(f"{ds_name}: positional={positional(ds).shape[1]} features, "
              f"aggregate={aggregate(ds).shape[1]} features")
    out = RESULTS / "baseline_runs.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (RESULTS / "baseline_trees.txt").write_text("\n".join(tree_txt))
    print(f"wrote {out} ({len(rows)} rows) and baseline_trees.txt")


if __name__ == "__main__":
    main()
