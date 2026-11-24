---
title: "Concept Induction on Michalski's Trains: What Description-Logic Learning Can and Cannot Do"
subtitle: "Symbolic Learning — Project Report"
author: "Group: <member 1>, <member 2>, <member 3>"
date: "November 2026"
---

# 1. Introduction

Concept induction learns a class expression $C$ from a knowledge base
$\mathcal{O}=(\mathcal{T},\mathcal{A})$ and example sets $P$, $N$ such that
$\mathcal{O}\models C(a)$ for $a\in P$ and $\mathcal{O}\not\models C(b)$ for $b\in N$.
We apply DL-Learner [1] to the UCI *Trains* data [2], a small but genuinely
**relational** benchmark. We compare it with decision trees and random forests,
and we ask what the logical representation buys us.

<!-- RESULTS-INTRO -->

# 2. Dataset

**Source.** UCI ML Repository #103 *Trains* (Michalski & Larson 1977; Stepp & Michalski 1986).
Each train pulls 2–4 wagons behind an engine. Each wagon has a *shape* (10 values,
e.g. open rectangle, U-shaped, hexagon, jagged top), a *length* (short/long), 2 or 3
*wheels*, and carries 0–3 *loads* of one shape (circle, triangle, rectangle,
hexagon). Wagons are ordered (`infront`). The UCI documentation also gives a
hierarchy: four shapes are *open-top* and the others are *closed-top*.

We use three learning sets (Table 1):

| set | trains | pos / neg | wagons | target | source |
|---|---|---|---|---|---|
| **michalski10** | 10 | 5 / 5 | 30 | eastbound | `trains-original.data` |
| **michie24** | 24 | 12 / 12 | 82 | "OK" | `trains.supplement` (Michie's 1994 challenge) |
| **synthetic200** | 200 | 100 / 100 | 621 | eastbound | generated, hidden rule |
| **synthetic200_noise10** | 200 | 94 / 106 | 621 | eastbound | same, 10 % labels flipped |

*Table 1 – learning sets.*

The UCI page contains only 10 trains, too few to estimate test performance.
Two extra sources make the evaluation meaningful:

* **Michie's 24 trains**, from the supplement file shipped with the UCI dataset.
  They use a richer vocabulary: roof type (none/flat/peaked/jagged/arc), double walls, and diamond and inverted-triangle loads.
  The challenge's "official" rule is relational: *a wagon with a peaked roof, or two
  **adjacent** short wagons with the **same** load shape*.
* **200 synthetic trains**, drawn at random in Michalski's vocabulary (seed 42) and
  labelled by Michalski's classic answer, *"has a short closed wagon"*. The classes
  are balanced by rejection sampling. Since the true concept is known, we can
  check whether the learner **recovers** it, and how label noise affects it.

**Why this dataset suits concept induction.** A train is not a fixed-length
row. UCI's own "transformed" version must invent the columns `car2_shape … car5_shape`
and pad missing wagons with "-". A rule like "*some* wagon is short and
closed" becomes, for a propositional learner, a disjunction over wagon positions.
For a DL learner it is the single existential restriction ∃hasCar.(Short ⊓ Closed).

**Checks.** After parsing (`src/parse_data.py`), the Michalski labels agree 10/10
with the classic rule, and Michie's labels agree 24/24 with the published official rule.

# 3. Knowledge base

`src/build_ontology.py` converts each set into an OWL ontology (RDF/XML,
`ontology/*.owl`).

**Individuals.** One per train, wagon and load. For example, michalski10 has
10 trains, 30 wagons and 35 loads, so 75 individuals. synthetic200 has 1,603.

**TBox (classes).**

* `Train`, `Car`, `Load`: pairwise disjoint.
* `ShortCar` / `LongCar`, `OpenCar` / `ClosedCar`, `TwoWheelCar` / `ThreeWheelCar`:
  each pair is disjoint. These are the categorical and discretised attributes.
* One class per wagon shape, placed under `OpenCar` or `ClosedCar` following the UCI
  hierarchy (e.g. `UShapedCar ⊑ OpenCar`, `JaggedTopCar ⊑ ClosedCar`). The shapes are mutually disjoint.
* Michie only: roof classes (`PeakedRoofCar ⊑ ClosedCar`, `NoRoofCar ⊑ OpenCar`, …)
  and `DoubleWallCar`.
* One class per load shape (`CircleLoad ⊑ Load`, …), mutually disjoint.

**Object properties.** `hasCar` (Train→Car), `hasLoad` (Car→Load), and
`inFrontOf` (Car→Car, functional: the wagon *directly* behind).

**Data properties** (functional, `xsd:integer`). `carCount` (Train), `position`,
`wheels`, `loadCount` (Car). DL-Learner can build datatype restrictions such as
∃carCount.[≥ 3] from these.

**Modelling choices.**

1. *No leakage.* The direction/OK label appears nowhere in the ontology. It only
   appears in the example lists of the `.conf` files.
2. *Engine dropped.* Every Michalski train starts with an identical engine, so it carries no information.
3. *Load shape as a class of a separate load individual*, not as a wagon
   attribute. The ontology therefore keeps the three-level structure
   train → wagon → load (concept depth 3).
4. *Numbers.* `wheels` is both discretised (two classes) and kept as a data
   property. `carCount`, `position` and `loadCount` are data properties only.
5. *No missing values.* A wagon without a load simply has no `hasLoad` filler.
6. *Closure variant.* `ontology/*_closed.owl` adds, for every train,
   `hasCar only {c1,…,cn}`; for every wagon, `hasLoad only {l1,…}` (or `only ⊥`);
   for the last wagon, `inFrontOf only ⊥`; and `AllDifferent` over all
   individuals. With these axioms, ∀- and ¬-statements about the data become
   *entailed* under the open-world assumption (Section 6.4).

# 4. Learning problem

**Target and examples.** $P$ = eastbound (resp. OK) trains and $N$ = the others,
using `posNegStandard`. The sets are balanced by construction.

**Splits** (`src/splits.py`, `data/splits/`). Leave-one-out for the 10- and
24-train sets, and stratified 5-fold (seed 0) for the synthetic sets. **The same
folds** are used for DL-Learner and the baselines. Because every LOO test fold holds
one train, we report metrics on the **pooled** test predictions of all folds.

**Evaluation of a concept on test data.** DL-Learner only reports accuracy on
the examples it was given. For each fold we therefore take its best concept (solution #1)
and classify the held-out trains with our own evaluator (`src/dl_concepts.py`).
The evaluator parses DL-Learner's Manchester-style output and implements the
**closed-world semantics of DL-Learner's `closed world reasoner`**:
negation as failure, and ∀ over the asserted fillers. On the full data it reproduces
DL-Learner's reported accuracies exactly (e.g. 100 % for
∃hasCar.(ClosedCar ⊓ ShortCar), 80 % for ∃carCount.[≥3]).

**Hypothesis language.** The reference setting is CELOE with the ρ refinement
operator over **ALC(D) with qualified number restrictions**:
⊤, ⊥, atomic classes, ¬, ⊓, ⊔, ∃r.C, ∀r.C, ≥n r.C, ≤n r.C, and ∃d.[range]
over the integer data properties. We restrict this language in Section 5 (no ¬/∀;
no datatypes/cardinalities; EL only). Inverse roles, nominals and hasValue are off.
**Length** follows DL-Learner's metric: atom = 1, ¬C = 1+|C|, C⊓D = |C|+|D|+1,
∃r.C = 2+|C|, ≥n r.C = 3+|C|, ∃d.range = 3.

<!-- SECTIONS 5+ ARE FILLED IN FROM results/summary.md -->

# References

[1] J. Lehmann. DL-Learner: Learning Concepts in Description Logics. *JMLR* 10, 2009.
    J. Lehmann et al. Class expression learning for ontology engineering (CELOE). *J. Web Semantics* 9(1), 2011.
[2] R.S. Michalski, J.B. Larson. Inductive inference of VL decision rules. *SIGART Newsletter* 63, 1977. UCI ML Repository, *Trains* dataset (id 103).
[3] D. Michie, S. Muggleton, D. Page, A. Srinivasan. To the international computing community: a new East-West challenge. Oxford University Computing Laboratory, 1994.
[4] J. Lehmann, P. Hitzler. Concept learning in description logics using refinement operators. *Machine Learning* 78, 2010.
