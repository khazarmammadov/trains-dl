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
