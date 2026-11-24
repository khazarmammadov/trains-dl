# Data

## Source
UCI Machine Learning Repository, *Trains* (id 103), downloaded from
https://archive.ics.uci.edu/dataset/103/trains into `raw/` (unmodified; `trains.tar.Z`
only duplicates the other files).

| file | content |
|---|---|
| `raw/trains-original.data` | Michalski's 10 trains in relational (VL21) form, 5 east / 5 west |
| `raw/trains-transformed.data` | the same 10 trains flattened into 32 attributes |
| `raw/trains.supplement` | Michie's 1994 24-train challenge (12 OK / 12 not OK), Prolog facts, plus published rules |
| `raw/trains.names` | attribute documentation and the open/closed shape hierarchy |

## Processed (`src/parse_data.py`)
| dataset | trains | pos / neg | cars | target |
|---|---|---|---|---|
| `michalski10` | 10 | 5 / 5 | 30 | eastbound |
| `michie24` | 24 | 12 / 12 | 82 | OK |
| `synthetic200` | 200 | 100 / 100 | 621 | eastbound (hidden rule ∃hasCar.(Short ⊓ Closed)) |
| `synthetic200_noise10` | 200 | 94 / 106 | 621 | same trains, 10 % labels flipped |

## Why this dataset fits concept induction
It is **relational**, not a flat table: a train has a variable number (2–4) of
wagons; each wagon has its own attributes and 0–3 loads, and wagons are ordered
(`inFrontOf`). The UCI "transformed" version has to invent positional columns
(`car2_shape`, …, `car5_shape`) padded with `-`, so a rule like "*some* car is short
and closed" becomes a disjunction over positions for a propositional learner.

## Modelling / cleaning choices
* The engine (always position 1, identical in every Michalski train) is dropped: it carries no information.
* `closed` is derived from the shape hierarchy in `trains.names`
  (openrect, opentrap, ushaped, dblopnrect → open; others → closed). For Michie's
  trains, closed = roof ≠ none.
* `ncar`, `npl`, `infront` are not stored: they are derivable from the car list.
* There are no missing values. A car with no load simply has an empty load list.

## Sanity checks
* Michalski labels agree 10/10 with "∃ a short closed car".
* Michie labels agree 24/24 with the published official rule
  ("a car with a peaked roof, or two adjacent short cars with the same load shape").

## Synthetic data
The real sets are tiny (10 and 24 trains), so test-set metrics are very noisy. The
synthetic set uses the same vocabulary (2–4 wagons, 9 shapes, 4 load shapes) and
labels each train with a known rule, balanced by rejection sampling (seed 42). Because
the true concept is known, it shows whether the learner *recovers* it and how it
behaves with label noise.
