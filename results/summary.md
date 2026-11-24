# Results summary

Pooled test predictions over all folds (LOO for the 10/24-train sets, stratified 5-fold for synthetic). `len` = concept length (DL) or number of tree nodes summed over the forest (ML).

## michalski10

| method | setting | test acc | prec | rec | F1 | train acc | len | time s |
|---|---|---|---|---|---|---|---|---|
| DL-Learner | celoe_alc | 0.900 | 0.833 | 1.000 | 0.909 | 1.000 | 5.0 | 7.55 |
| DL-Learner | celoe_no_data_card | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5.0 | 8.28 |
| DL-Learner | celoe_no_neg_all | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5.0 | 7.99 |
| DL-Learner | celoe_noise10 | 0.900 | 0.833 | 1.000 | 0.909 | 1.000 | 5.0 | 7.74 |
| DL-Learner | celoe_t1 | 0.900 | 0.833 | 1.000 | 0.909 | 1.000 | 5.0 | 3.56 |
| DL-Learner | celoe_t20 | 0.900 | 0.833 | 1.000 | 0.909 | 1.000 | 5.0 | 22.34 |
| DL-Learner | eltl_el | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5.8 | 8.04 |
| DL-Learner | ocel_alc | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 9.0 | 7.65 |
| DL-Learner | owa_hermit_closed | 0.500 | 0.500 | 1.000 | 0.667 | 0.500 | 1.0 | 12.02 |
| DL-Learner | owa_hermit_open | 0.800 | 0.714 | 1.000 | 0.833 | 0.800 | 3.0 | 7.71 |
| ML | dt_aggregate | 0.500 | 0.500 | 0.800 | 0.615 | 1.000 | 5.0 | 0.00 |
| ML | dt_positional | 0.400 | 0.333 | 0.200 | 0.250 | 1.000 | 4.8 | 0.01 |
| ML | rf_aggregate | 0.600 | 0.571 | 0.800 | 0.667 | 1.000 | 1027.0 | 0.23 |
| ML | rf_positional | 0.700 | 0.667 | 0.800 | 0.727 | 1.000 | 1040.8 | 0.26 |

| setting | concept learned on all data | distinct fold concepts | candidates tested |
|---|---|---|---|
| celoe_alc | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 2.0 | 25491 |
| celoe_no_data_card | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 1.0 | 19460 |
| celoe_no_neg_all | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 1.0 | 30236 |
| celoe_noise10 | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 2.0 | 36962 |
| celoe_t1 | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 2.0 | 6988 |
| celoe_t20 | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 2.0 | 98091 |
| eltl_el | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 2.0 | – |
| ocel_alc | `∃hasCar.(ClosedCar ⊓ ShortCar) ⊓ ∃carCount.[>=3]` | 1.0 | 27759 |
| owa_hermit_closed | `⊤` | 1.0 | 16 |
| owa_hermit_open | `∃carCount.[>=3]` | 1.0 | 135 |

## michie24

| method | setting | test acc | prec | rec | F1 | train acc | len | time s |
|---|---|---|---|---|---|---|---|---|
| DL-Learner | celoe_alc | 0.625 | 0.600 | 0.750 | 0.667 | 0.866 | 7.9 | 7.70 |
| DL-Learner | celoe_no_data_card | 0.667 | 0.625 | 0.833 | 0.714 | 0.875 | 8.0 | 8.19 |
| DL-Learner | celoe_no_neg_all | 0.875 | 0.909 | 0.833 | 0.870 | 0.960 | 9.0 | 8.27 |
| DL-Learner | celoe_noise10 | 0.833 | 0.900 | 0.750 | 0.818 | 0.957 | 9.3 | 7.69 |
| DL-Learner | celoe_t1 | 0.625 | 0.588 | 0.833 | 0.690 | 0.861 | 7.5 | 3.56 |
| DL-Learner | celoe_t20 | 0.875 | 0.909 | 0.833 | 0.870 | 0.960 | 9.0 | 22.77 |
| DL-Learner | eltl_el | 0.542 | 0.529 | 0.750 | 0.621 | 0.699 | 11.7 | 8.48 |
| DL-Learner | ocel_alc | 0.542 | 0.529 | 0.750 | 0.621 | 0.754 | 19.3 | 8.22 |
| DL-Learner | owa_hermit_closed | 0.500 | 0.500 | 1.000 | 0.667 | 0.500 | 1.0 | 20.92 |
| DL-Learner | owa_hermit_open | 0.500 | 0.500 | 1.000 | 0.667 | 0.500 | 1.0 | 11.12 |
| ML | dt_aggregate | 0.792 | 0.818 | 0.750 | 0.783 | 1.000 | 8.8 | 0.00 |
| ML | dt_positional | 0.458 | 0.455 | 0.417 | 0.435 | 1.000 | 11.1 | 0.00 |
| ML | rf_aggregate | 0.667 | 0.667 | 0.667 | 0.667 | 1.000 | 2397.8 | 0.25 |
| ML | rf_positional | 0.750 | 0.714 | 0.833 | 0.769 | 1.000 | 2662.7 | 0.24 |

| setting | concept learned on all data | distinct fold concepts | candidates tested |
|---|---|---|---|
| celoe_alc | `∃hasCar.(DoubleWallCar ⊔ (ClosedCar ⊓ (LongCar ⊔ UShapedCar)))` | 7.0 | 30771 |
| celoe_no_data_card | `∃hasCar.(DoubleWallCar ⊔ (ClosedCar ⊓ (LongCar ⊔ UShapedCar)))` | 5.0 | 27523 |
| celoe_no_neg_all | `∃hasCar.(DoubleWallCar ⊔ (PeakedRoofCar ⊔ (ClosedCar ⊓ RectangleCar)))` | 4.0 | 37310 |
| celoe_noise10 | `∃hasCar.(PeakedRoofCar ⊔ (DoubleWallCar ⊓ ∃hasLoad.¬DiamondLoad))` | 6.0 | 38745 |
| celoe_t1 | `∀hasCar.(ClosedCar ⊔ ShortCar)` | 5.0 | 6429 |
| celoe_t20 | `∃hasCar.(DoubleWallCar ⊔ (PeakedRoofCar ⊔ (ClosedCar ⊓ RectangleCar)))` | 4.0 | 154800 |
| eltl_el | `∃hasCar.(OpenCar ⊓ ShortCar) ⊓ ∃hasCar.(ShortCar ⊓ ∃inFrontOf.ShortCar)` | 6.0 | – |
| ocel_alc | `≥2 hasCar.(ShortCar ⊓ (RectangleCar ⊔ (∃loadCount.[<=1] ⊓ ∃position.[>=2])) ⊓ ¬HexagonCar ⊓ ∃wheels.[<=2])` | 8.0 | 14231 |
| owa_hermit_closed | `⊤` | 1.0 | 5 |
| owa_hermit_open | `⊤` | 1.0 | 17 |

## synthetic200

| method | setting | test acc | prec | rec | F1 | train acc | len | time s |
|---|---|---|---|---|---|---|---|---|
| DL-Learner | celoe_alc | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5.0 | 8.23 |
| DL-Learner | celoe_no_data_card | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5.0 | 8.30 |
| DL-Learner | celoe_no_neg_all | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5.0 | 9.37 |
| DL-Learner | celoe_noise10 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5.0 | 7.95 |
| DL-Learner | celoe_t1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5.0 | 3.73 |
| DL-Learner | celoe_t20 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5.0 | 22.83 |
| DL-Learner | eltl_el | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5.0 | 9.38 |
| DL-Learner | ocel_alc | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5.0 | 8.70 |
| ML | dt_aggregate | 0.825 | 0.842 | 0.800 | 0.821 | 1.000 | 48.2 | 0.00 |
| ML | dt_positional | 0.905 | 0.918 | 0.890 | 0.904 | 1.000 | 35.8 | 0.00 |
| ML | rf_aggregate | 0.880 | 0.888 | 0.870 | 0.879 | 1.000 | 11969.2 | 0.26 |
| ML | rf_positional | 0.920 | 0.920 | 0.920 | 0.920 | 1.000 | 14420.4 | 0.21 |

| setting | concept learned on all data | distinct fold concepts | candidates tested |
|---|---|---|---|
| celoe_alc | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 1.0 | 5951 |
| celoe_no_data_card | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 1.0 | 5019 |
| celoe_no_neg_all | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 1.0 | 4558 |
| celoe_noise10 | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 1.0 | 7167 |
| celoe_t1 | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 1.0 | 1050 |
| celoe_t20 | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 1.0 | 19747 |
| eltl_el | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 1.0 | – |
| ocel_alc | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 1.0 | 20008 |

## synthetic200_noise10

| method | setting | test acc | prec | rec | F1 | train acc | len | time s | acc vs true |
|---|---|---|---|---|---|---|---|---|---|
| DL-Learner | celoe_alc | 0.580 | 0.529 | 0.957 | 0.682 | 0.624 | 6.6 | 7.95 | 0.650 |
| DL-Learner | celoe_no_data_card | 0.580 | 0.529 | 0.957 | 0.682 | 0.624 | 6.6 | 8.37 | 0.650 |
| DL-Learner | celoe_no_neg_all | 0.580 | 0.529 | 0.957 | 0.682 | 0.624 | 6.6 | 8.74 | 0.650 |
| DL-Learner | celoe_noise10 | 0.900 | 0.870 | 0.926 | 0.897 | 0.900 | 5.0 | 7.89 | 1.000 |
| DL-Learner | celoe_t1 | 0.580 | 0.529 | 0.979 | 0.687 | 0.611 | 3.4 | 3.55 | 0.630 |
| DL-Learner | celoe_t20 | 0.600 | 0.543 | 0.947 | 0.690 | 0.649 | 8.0 | 23.50 | 0.680 |
| DL-Learner | eltl_el | 0.580 | 0.529 | 0.979 | 0.687 | 0.619 | 5.8 | 8.76 | 0.630 |
| DL-Learner | ocel_alc | 0.650 | 0.576 | 0.968 | 0.722 | 0.709 | 15.0 | 8.53 | 0.710 |
| ML | dt_aggregate | 0.690 | 0.678 | 0.649 | 0.663 | 1.000 | 75.0 | 0.00 | 0.740 |
| ML | dt_positional | 0.665 | 0.648 | 0.628 | 0.638 | 1.000 | 70.2 | 0.01 | 0.735 |
| ML | rf_aggregate | 0.740 | 0.739 | 0.691 | 0.714 | 1.000 | 14902.4 | 0.30 | 0.840 |
| ML | rf_positional | 0.720 | 0.711 | 0.681 | 0.696 | 1.000 | 17660.4 | 0.29 | 0.790 |

| setting | concept learned on all data | distinct fold concepts | candidates tested |
|---|---|---|---|
| celoe_alc | `∃hasCar.ClosedCar ⊓ ∃hasCar.TwoWheelCar` | 3.0 | 6475 |
| celoe_no_data_card | `∃hasCar.ClosedCar ⊓ ∃hasCar.TwoWheelCar` | 3.0 | 5125 |
| celoe_no_neg_all | `∃hasCar.ClosedCar ⊓ ∃hasCar.TwoWheelCar` | 3.0 | 4774 |
| celoe_noise10 | `∃hasCar.(ClosedCar ⊓ ShortCar)` | 1.0 | 7633 |
| celoe_t1 | `∃hasCar.ClosedCar` | 2.0 | 1216 |
| celoe_t20 | `∃hasCar.ClosedCar ⊓ ∃hasCar.TwoWheelCar` | 4.0 | 25703 |
| eltl_el | `∃hasCar.ClosedCar ⊓ ∃hasCar.TwoWheelCar` | 3.0 | – |
| ocel_alc | `∃hasCar.(ClosedCar ⊓ (ShortCar ⊔ (¬EllipseCar ⊓ ∃hasLoad.⊤ ⊓ ∃position.[<=4])))` | 4.0 | 19982 |
