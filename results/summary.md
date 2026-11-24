# Results summary

Pooled test predictions over all folds (LOO for the 10/24-train sets, stratified 5-fold for synthetic). `len` = concept length (DL) or number of tree nodes summed over the forest (ML).

## michalski10

| method | setting | test acc | prec | rec | F1 | train acc | len | time s |
|---|---|---|---|---|---|---|---|---|
| DL-Learner | celoe_alc | 0.900 | 0.833 | 1.000 | 0.909 | 1.000 | 5.0 | 7.87 |
| ML | dt_aggregate | 0.500 | 0.500 | 0.800 | 0.615 | 1.000 | 5.0 | 0.00 |
| ML | dt_positional | 0.400 | 0.333 | 0.200 | 0.250 | 1.000 | 4.8 | 0.01 |
| ML | rf_aggregate | 0.600 | 0.571 | 0.800 | 0.667 | 1.000 | 1027.0 | 0.23 |
| ML | rf_positional | 0.700 | 0.667 | 0.800 | 0.727 | 1.000 | 1040.8 | 0.26 |

| setting | concept learned on all data | distinct fold concepts | candidates tested |
|---|---|---|---|
| celoe_alc | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 2.0 | 27202 |

## michie24

| method | setting | test acc | prec | rec | F1 | train acc | len | time s |
|---|---|---|---|---|---|---|---|---|
| ML | dt_aggregate | 0.792 | 0.818 | 0.750 | 0.783 | 1.000 | 8.8 | 0.00 |
| ML | dt_positional | 0.458 | 0.455 | 0.417 | 0.435 | 1.000 | 11.1 | 0.00 |
| ML | rf_aggregate | 0.667 | 0.667 | 0.667 | 0.667 | 1.000 | 2397.8 | 0.25 |
| ML | rf_positional | 0.750 | 0.714 | 0.833 | 0.769 | 1.000 | 2662.7 | 0.24 |

## synthetic200

| method | setting | test acc | prec | rec | F1 | train acc | len | time s |
|---|---|---|---|---|---|---|---|---|
| ML | dt_aggregate | 0.825 | 0.842 | 0.800 | 0.821 | 1.000 | 48.2 | 0.00 |
| ML | dt_positional | 0.905 | 0.918 | 0.890 | 0.904 | 1.000 | 35.8 | 0.00 |
| ML | rf_aggregate | 0.880 | 0.888 | 0.870 | 0.879 | 1.000 | 11969.2 | 0.26 |
| ML | rf_positional | 0.920 | 0.920 | 0.920 | 0.920 | 1.000 | 14420.4 | 0.21 |

## synthetic200_noise10

| method | setting | test acc | prec | rec | F1 | train acc | len | time s | acc vs true |
|---|---|---|---|---|---|---|---|---|---|
| ML | dt_aggregate | 0.690 | 0.678 | 0.649 | 0.663 | 1.000 | 75.0 | 0.00 | 0.740 |
| ML | dt_positional | 0.665 | 0.648 | 0.628 | 0.638 | 1.000 | 70.2 | 0.01 | 0.735 |
| ML | rf_aggregate | 0.740 | 0.739 | 0.691 | 0.714 | 1.000 | 14902.4 | 0.30 | 0.840 |
| ML | rf_positional | 0.720 | 0.711 | 0.681 | 0.696 | 1.000 | 17660.4 | 0.29 | 0.790 |
