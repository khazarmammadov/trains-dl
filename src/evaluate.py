"""Aggregate DL-Learner and baseline runs into tables and figures.

Metrics (per dataset x setting), computed on the POOLED test predictions of
all folds (the only sensible choice for leave-one-out, where each fold has a
single test train):
  accuracy, precision, recall, F1 on test; mean train accuracy;
  for 5-fold CV also mean ± std of per-fold test accuracy;
  for the noisy set also accuracy w.r.t. the TRUE (clean) labels;
  DL only: mean concept length, #distinct concepts over folds (stability),
           the most frequent fold concept, the concept learned on all data,
           mean runtime and #candidate concepts tested.
Outputs: results/summary.csv, results/summary.md, results/fig_*.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from splits import DATASETS, load_dataset  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"

# reference categorical palette (dataviz skill, validated): slot 1 / slot 2
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, SURFACE, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"


def safe_div(a, b):
    return a / b if b else float("nan")


def clean_labels() -> dict:
    return {t["id"]: t["label"] for t in load_dataset("synthetic200")["trains"]}


def summarise(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    truth = clean_labels()
    out = []
    for (setting, ds), g in df.groupby(["setting", "dataset"]):
        folds = g[g["fold"] != "full"]
        tp, tn, fp, fn = (int(folds[c].sum()) for c in ("tp", "tn", "fp", "fn"))
        n = tp + tn + fp + fn
        p, r = safe_div(tp, tp + fp), safe_div(tp, tp + fn)
        row = {"kind": kind, "dataset": ds, "setting": setting, "folds": len(folds),
               "test_acc": safe_div(tp + tn, n), "precision": p, "recall": r,
               "f1": safe_div(2 * tp, 2 * tp + fp + fn),
               "train_acc": folds["train_acc"].astype(float).mean(),
               "time_s": folds["wall_s"].astype(float).mean()}
        if len(folds) <= 6:  # k-fold: per-fold spread
            accs = (folds["tp"] + folds["tn"]) / folds["n_test"]
            row["acc_fold_mean"], row["acc_fold_std"] = accs.mean(), accs.std()
        if ds.endswith("_noise10") and "test_pred" in folds:
            preds = [x.split(":") for s in folds["test_pred"].dropna() for x in s.split()]
            row["acc_true_labels"] = sum(int(v) == truth[i] for i, v in preds) / len(preds)
        if kind == "DL-Learner":
            full = g[g["fold"] == "full"]
            row.update(
                length=folds["length"].astype(float).mean(),
                tested=folds["tested"].astype(float).mean(),
                n_distinct=folds["concept"].nunique(),
                modal_concept=folds["concept_dl"].mode().iat[0] if folds["concept_dl"].notna().any() else None,
                full_concept=full["concept_dl"].iat[0] if len(full) else None,
                full_length=full["length"].iat[0] if len(full) else None,
            )
        else:
            row["length"] = folds["complexity"].astype(float).mean()  # tree nodes
        out.append(row)
    return pd.DataFrame(out)


def fmt(x, nd=3):
    if isinstance(x, float):
        return "–" if pd.isna(x) else f"{x:.{nd}f}"
    return "–" if x is None else str(x)


def markdown(summary: pd.DataFrame) -> str:
    lines = ["# Results summary", "",
             "Pooled test predictions over all folds (LOO for the 10/24-train sets, "
             "stratified 5-fold for synthetic). `len` = concept length (DL) or number "
             "of tree nodes summed over the forest (ML).", ""]
    for ds in DATASETS:
        s = summary[summary["dataset"] == ds].sort_values(["kind", "setting"])
        if s.empty:
            continue
        extra = "acc_true_labels" in s and s["acc_true_labels"].notna().any()
        lines += [f"## {ds}", "",
                  "| method | setting | test acc | prec | rec | F1 | train acc | len | time s |"
                  + (" acc vs true |" if extra else ""),
                  "|---|---|---|---|---|---|---|---|---|" + ("---|" if extra else "")]
        for _, r in s.iterrows():
            lines.append(
                f"| {r['kind']} | {r['setting']} | {fmt(r['test_acc'])} | {fmt(r['precision'])} | "
                f"{fmt(r['recall'])} | {fmt(r['f1'])} | {fmt(r['train_acc'])} | "
                f"{fmt(r['length'], 1)} | {fmt(r['time_s'], 2)} |"
                + (f" {fmt(r.get('acc_true_labels'))} |" if extra else ""))
        dl = s[s["kind"] == "DL-Learner"]
        if not dl.empty:
            lines += ["", "| setting | concept learned on all data | distinct fold concepts | candidates tested |",
                      "|---|---|---|---|"]
            for _, r in dl.iterrows():
                lines.append(f"| {r['setting']} | `{r['full_concept']}` | {r['n_distinct']} | "
                             f"{fmt(r['tested'], 0)} |")
        lines.append("")
    return "\n".join(lines)


def style(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8, length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def fig_comparison(summary: pd.DataFrame) -> None:
    """Small multiples: test accuracy per method, one panel per dataset."""
    picks = [("DL-Learner", "celoe_alc", "CELOE (ALC)"),
             ("DL-Learner", "celoe_noise10", "CELOE noise 10%"),
             ("DL-Learner", "eltl_el", "ELTL (EL)"),
             ("DL-Learner", "ocel_alc", "OCEL"),
             ("ML", "dt_positional", "Tree, positional"),
             ("ML", "dt_aggregate", "Tree, aggregate"),
             ("ML", "rf_positional", "Forest, positional"),
             ("ML", "rf_aggregate", "Forest, aggregate")]
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), sharey=True, facecolor=SURFACE)
    for ax, ds in zip(axes, DATASETS):
        vals, labels, colors = [], [], []
        for kind, setting, label in picks:
            r = summary[(summary.dataset == ds) & (summary.setting == setting)]
            vals.append(float(r["test_acc"].iat[0]) if len(r) else float("nan"))
            labels.append(label)
            colors.append(BLUE if kind == "DL-Learner" else ORANGE)
        y = range(len(vals))[::-1]
        ax.barh(list(y), vals, color=colors, height=0.62, edgecolor=SURFACE, linewidth=2)
        for yi, v in zip(y, vals):
            if v == v:
                ax.text(v + 0.015, yi, f"{v:.2f}", va="center", fontsize=7.5, color=INK2)
        ax.set_xlim(0, 1.12)
        ax.axvline(0.5, color=INK2, linewidth=0.8, linestyle=(0, (3, 3)))
        ax.set_title(ds, fontsize=9.5, color=INK, loc="left")
        ax.set_yticks(list(y))
        ax.set_yticklabels(labels)
        style(ax)
    axes[0].text(0.5, -0.9, "chance", fontsize=7, color=INK2, ha="center")
    handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color=ORANGE)]
    fig.legend(handles, ["Concept induction (DL-Learner)", "Classical ML"], loc="upper right",
               ncol=2, frameon=False, fontsize=8.5, labelcolor=INK)
    fig.suptitle("Test accuracy (pooled over CV folds)", x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(RES / "fig_test_accuracy.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)


def fig_time_budget(summary: pd.DataFrame) -> None:
    """Effect of the runtime budget (1/5/20 s) on accuracy and concept length.
    Two measures -> two panels (no dual axis)."""
    budgets = [("celoe_t1", 1), ("celoe_alc", 5), ("celoe_t20", 20)]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.2), facecolor=SURFACE)
    palette = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # fixed categorical order
    for ds, col in zip(DATASETS, palette):
        rows = [summary[(summary.dataset == ds) & (summary.setting == s)] for s, _ in budgets]
        xs = [b for (_, b), r in zip(budgets, rows) if len(r)]
        acc = [float(r["test_acc"].iat[0]) for r in rows if len(r)]
        ln = [float(r["length"].iat[0]) for r in rows if len(r)]
        a1.plot(xs, acc, marker="o", markersize=6, linewidth=2, color=col, label=ds)
        a2.plot(xs, ln, marker="o", markersize=6, linewidth=2, color=col, label=ds)
    for ax, title in ((a1, "Test accuracy"), (a2, "Mean concept length")):
        ax.set_xscale("log")
        ax.set_xticks([1, 5, 20])
        ax.set_xticklabels(["1 s", "5 s", "20 s"])
        ax.set_title(title, fontsize=9.5, color=INK, loc="left")
        style(ax)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.grid(axis="x", visible=False)
    a1.legend(frameon=False, fontsize=7.5, labelcolor=INK)
    fig.suptitle("CELOE runtime budget", x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(RES / "fig_time_budget.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    dl = pd.read_csv(RES / "dl_runs.csv")
    ml = pd.read_csv(RES / "baseline_runs.csv")
    summary = pd.concat([summarise(dl, "DL-Learner"), summarise(ml, "ML")], ignore_index=True)
    summary.to_csv(RES / "summary.csv", index=False, float_format="%.4f")
    (RES / "summary.md").write_text(markdown(summary))
    fig_comparison(summary)
    fig_time_budget(summary)
    errors = dl[dl.get("error").notna()] if "error" in dl else []
    print(f"summary rows={len(summary)}; DL runs with errors={len(errors)}")


if __name__ == "__main__":
    main()
