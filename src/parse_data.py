"""Parse the UCI Trains data into a common relational JSON format.

Produces three datasets in data/processed/:

  michalski10.json   Michalski's original 10 trains (east vs west), from
                     data/raw/trains-original.data
  michie24.json      Michie's 24-train challenge (OK vs not_OK), from the
                     Prolog facts in data/raw/trains.supplement
  synthetic200.json  200 random trains in Michalski's vocabulary, labelled by
                     a hidden rule (see generate_synthetic) -- used to get
                     meaningful train/test splits
  synthetic200_noise10.json  same trains, 10% of labels flipped

Common schema
-------------
{
  "name": str, "target": str, "description": str,
  "trains": [
    {"id": str, "label": 0|1,
     "cars": [{"id": str, "pos": int, "shape": str, "length": "short"|"long",
               "wheels": int, "closed": bool, "roof": str, "double": bool,
               "loads": [load_shape, ...]}]}
  ]
}
Only attributes present in the source are filled; "roof" and "double" exist
only for Michie's trains.
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

# Value hierarchy given with the UCI data (trains.names, section 4)
OPEN_TOP = {"openrect", "opentrap", "ushaped", "dblopnrect"}
CLOSED_TOP = {"hexagon", "ellipse", "closedrect", "jaggedtop", "slopetop", "engine"}
LOAD_NAMES = {"circlelod": "circle", "hexagonlod": "hexagon",
              "rectanglod": "rectangle", "trianglod": "triangle"}


# --------------------------------------------------------------------------
# Michalski's 10 trains
# --------------------------------------------------------------------------
def parse_michalski() -> dict:
    text = (RAW / "trains-original.data").read_text()
    blocks = re.split(r"%TRAIN\s+(\w)", text)[1:]  # [name, body, name, body, ...]
    trains = []
    for name, body in zip(blocks[0::2], blocks[1::2]):
        facts = re.findall(r"\[([^\]]+)\]", body)
        cars: dict[str, dict] = {}
        loads_of: dict[str, list[str]] = {}
        load_shape: dict[str, str] = {}
        direction = None

        def car(cid: str) -> dict:
            return cars.setdefault(cid, {"id": cid, "loads": []})

        for f in facts:
            f = f.replace(" ", "")
            if m := re.fullmatch(r"ccont\(t1,(\w+)\)", f):
                car(m[1])
            elif m := re.fullmatch(r"loc\((\w+)\)=(\d+)", f):
                car(m[1])["pos"] = int(m[2])
            elif m := re.fullmatch(r"nwhl\((\w+)\)=(\d+)", f):
                car(m[1])["wheels"] = int(m[2])
            elif m := re.fullmatch(r"ln\((\w+)\)=(\w+)", f):
                car(m[1])["length"] = m[2]
            elif m := re.fullmatch(r"cshape\((\w+)\)=(\w+)", f):
                car(m[1])["shape"] = m[2]
            elif m := re.fullmatch(r"lcont\((\w+),(\w+)\)", f):
                loads_of.setdefault(m[1], []).append(m[2])
            elif m := re.fullmatch(r"lshape\((\w+)\)=(\w+)", f):
                load_shape[m[1]] = LOAD_NAMES[m[2]]
            elif m := re.fullmatch(r"direction=(\w+)", f):
                direction = m[1]
            # ncar, npl, infront are derivable from the above -> ignored

        out_cars = []
        for cid, c in sorted(cars.items(), key=lambda kv: kv[1]["pos"]):
            if c["shape"] == "engine":
                # every train starts with an identical engine: no information,
                # dropped (same choice as the UCI "transformed" version)
                continue
            c["closed"] = c["shape"] in CLOSED_TOP
            c["loads"] = [load_shape[l] for l in loads_of.get(cid, [])]
            c["id"] = f"{name}_{cid}"
            out_cars.append(c)
        trains.append({"id": f"train{name}", "label": int(direction == "east"),
                       "cars": out_cars})
    return {
        "name": "michalski10",
        "target": "Eastbound",
        "description": "Michalski's 10 trains (UCI #103); positive = eastbound",
        "trains": trains,
    }


# --------------------------------------------------------------------------
# Michie's 24 trains (Computing magazine challenge, Nov 1994)
# --------------------------------------------------------------------------
CAR_RE = re.compile(
    r"c\((\d+),(\w+),(\w+),(\w+),(\w+),(\d+),l\((\w+),(\d+)\)\)")


def parse_michie() -> dict:
    text = (RAW / "trains.supplement").read_text()
    # problem section only (ends before the RESULTS section)
    text = text.split("24 TRAINS: THE RESULTS")[0]
    trains = []
    for i, m in enumerate(re.finditer(r":-(not_OK|OK)\((\[.*?\])\)\.", text, re.S)):
        label = int(m[1] == "OK")
        body = re.sub(r"\s+", "", m[2])
        cars = []
        for c in CAR_RE.finditer(body):
            pos, shape, length, double, roof, wheels, lshape, n = c.groups()
            cars.append({
                "id": f"m{i + 1}_c{pos}", "pos": int(pos), "shape": shape,
                "length": length, "double": double == "double", "roof": roof,
                "closed": roof != "none", "wheels": int(wheels),
                "loads": [lshape] * int(n) if lshape != "none" else [],
            })
        trains.append({"id": f"m{i + 1}", "label": label, "cars": cars})
    assert len(trains) == 24, len(trains)
    return {
        "name": "michie24",
        "target": "OK",
        "description": ("Michie's 24-train challenge (trains.supplement); "
                        "positive = OK. Official rule: a car with a peaked "
                        "roof, or two adjacent short cars with the same load "
                        "shape."),
        "trains": trains,
    }


# --------------------------------------------------------------------------
# Synthetic trains in Michalski's vocabulary
# --------------------------------------------------------------------------
SYN_SHAPES = sorted((OPEN_TOP | CLOSED_TOP) - {"engine"})
SYN_LOADS = ["circle", "hexagon", "rectangle", "triangle"]


def hidden_rule(train: dict) -> int:
    """Ground truth for the synthetic set = Michalski's classic answer:
    'a train goes east iff it has a short, closed car'
    (DL: Train ⊓ ∃hasCar.(ShortCar ⊓ ClosedCar))."""
    return int(any(c["length"] == "short" and c["closed"] for c in train["cars"]))


def random_train(rng: random.Random, tid: str) -> dict:
    cars = []
    for k in range(rng.randint(2, 4)):  # 2-4 wagons behind the engine
        length = rng.choice(["short", "long"])
        shape = rng.choice(SYN_SHAPES)
        wheels = 3 if (length == "long" and rng.random() < 0.4) else 2
        nloads = rng.choice([0, 1, 1, 1, 2, 3] if length == "long" else [0, 1, 1, 2])
        lshape = rng.choice(SYN_LOADS)
        cars.append({
            "id": f"{tid}_car{k + 2}", "pos": k + 2, "shape": shape,
            "length": length, "wheels": wheels, "closed": shape in CLOSED_TOP,
            "loads": [lshape] * nloads,
        })
    return {"id": tid, "cars": cars}


def generate_synthetic(n: int = 200, seed: int = 42) -> dict:
    """Rejection-sample a balanced set of n trains (n/2 per class)."""
    rng = random.Random(seed)
    pos, neg, i = [], [], 0
    while len(pos) < n // 2 or len(neg) < n // 2:
        i += 1
        t = random_train(rng, f"s{i}")
        t["label"] = hidden_rule(t)
        bucket = pos if t["label"] else neg
        if len(bucket) < n // 2:
            bucket.append(t)
    trains = pos + neg
    rng.shuffle(trains)
    for k, t in enumerate(trains):  # renumber for readability
        old = t["id"]
        t["id"] = f"s{k + 1}"
        for c in t["cars"]:
            c["id"] = c["id"].replace(old + "_", t["id"] + "_", 1)
    return {
        "name": f"synthetic{n}",
        "target": "Eastbound",
        "description": (f"{n} random trains (seed {seed}) in Michalski's vocabulary, "
                        "labelled by the hidden rule ∃hasCar.(Short ⊓ Closed); balanced."),
        "trains": trains,
    }


def add_label_noise(ds: dict, rate: float = 0.10, seed: int = 7) -> dict:
    rng = random.Random(seed)
    noisy = json.loads(json.dumps(ds))
    idx = rng.sample(range(len(noisy["trains"])), int(rate * len(noisy["trains"])))
    for i in idx:
        noisy["trains"][i]["label"] ^= 1
    noisy["name"] += f"_noise{int(rate * 100)}"
    noisy["description"] += f" {int(rate * 100)}% of labels flipped (seed {seed})."
    noisy["flipped"] = sorted(noisy["trains"][i]["id"] for i in idx)
    return noisy


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    syn = generate_synthetic()
    for ds in (parse_michalski(), parse_michie(), syn, add_label_noise(syn)):
        path = OUT / f"{ds['name']}.json"
        path.write_text(json.dumps(ds, indent=1))
        n_pos = sum(t["label"] for t in ds["trains"])
        n_cars = sum(len(t["cars"]) for t in ds["trains"])
        print(f"{ds['name']:24s} trains={len(ds['trains']):3d} pos={n_pos:3d} "
              f"neg={len(ds['trains']) - n_pos:3d} cars={n_cars}")


if __name__ == "__main__":
    main()
