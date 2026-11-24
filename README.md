# Concept Induction on Michalski's Trains (Symbolic Learning project)

Learning Description-Logic class expressions with DL-Learner on the UCI
[Trains dataset](https://archive.ics.uci.edu/dataset/103/trains), compared
with classical ML baselines (decision tree, random forest).

## Layout
| Folder | Content |
|---|---|
| `data/` | raw UCI files + parsed relational CSVs (+ synthetic trains) |
| `src/` | Python code: parsing, ontology building, conf generation, evaluation, baselines |
| `ontology/` | generated `.owl` knowledge bases |
| `conf/` | DL-Learner `.conf` files used in the experiments |
| `results/` | metrics tables and figures |
| `report/` | report draft |
| `tools/` | DL-Learner launcher (`dlcli.sh`) and `setup.sh` |

## Setup
```bash
tools/setup.sh          # downloads DL-Learner 1.5.0 + creates .venv
```
DL-Learner 1.5.0 needs extra `--add-opens` flags on Java 17+; `tools/dlcli.sh` adds them.

## Reproduce everything
```bash
tools/setup.sh                              # DL-Learner 1.5.0 + Python venv
.venv/bin/python src/parse_data.py          # data/processed/*.json
.venv/bin/python src/build_ontology.py      # ontology/*.owl
.venv/bin/python src/splits.py              # data/splits/*.json (shared CV folds)
.venv/bin/python src/run_experiments.py     # conf/**.conf + DL-Learner runs (~35 min, 4 parallel)
.venv/bin/python src/baselines.py           # decision tree / random forest
.venv/bin/python src/evaluate.py            # results/summary.{csv,md}, figures
./make_submission.sh                        # submission/*.zip
```
`run_experiments.py` resumes: finished runs (output + wall time in `results/runs/`) are re-scored, not re-run (`--force` to re-run).

## Headline results (test accuracy, pooled over folds)
| dataset | best DL-Learner | concept | best tree/forest |
|---|---|---|---|
| michalski10 (LOO) | 1.00 (CELOE no ¬/∀, ELTL, OCEL); 0.90 reference | ∃hasCar.(ClosedCar ⊓ ShortCar) | 0.70 |
| michie24 (LOO) | 0.875 (CELOE no ¬/∀, or 20 s) | ∃hasCar.(DoubleWallCar ⊔ PeakedRoofCar ⊔ (ClosedCar ⊓ RectangleCar)) | 0.79 |
| synthetic200 (5-fold) | 1.00 (all settings) | ∃hasCar.(ClosedCar ⊓ ShortCar) = hidden rule | 0.92 |
| synthetic200_noise10 | 0.90 (1.00 vs true labels), CELOE noise 10 % | ∃hasCar.(ClosedCar ⊓ ShortCar) | 0.74 (0.84 vs true) |

Full tables: `results/summary.md`; report: `report/report.md`.
