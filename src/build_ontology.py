"""Convert the processed train datasets into OWL ontologies (RDF/XML).

For every dataset in data/processed/<name>.json two files are written:

  ontology/<name>.owl         TBox + ABox (open world, no closure axioms)
  ontology/<name>_closed.owl  same + closure axioms, so that universal
                              restrictions / negations become entailed under
                              the open-world assumption (OWA experiment)

Modelling (see report section 2):
  * individuals: one per train, car and load
  * categorical attributes  -> atomic classes (ShortCar, ClosedCar, ...)
    arranged in the hierarchy given by the UCI documentation
  * relations               -> object properties hasCar, hasLoad, inFrontOf
  * numeric attributes      -> data properties (wheels, position, loadCount,
    carCount) AND, for wheels, a discretised class (TwoWheelCar/ThreeWheelCar)
  * the class label is NOT asserted anywhere (no leakage); it only appears in
    the positive/negative example lists of the DL-Learner .conf files.
"""
from __future__ import annotations

import json
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS, XSD

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
ONT = ROOT / "ontology"

BASE = "http://example.org/trains"
T = Namespace(BASE + "#")

# raw value -> class name
SHAPE_CLASS = {
    # Michalski vocabulary
    "openrect": "OpenRectCar", "opentrap": "OpenTrapCar", "ushaped": "UShapedCar",
    "dblopnrect": "DoubleOpenRectCar", "closedrect": "ClosedRectCar",
    "hexagon": "HexagonCar", "ellipse": "EllipseCar", "jaggedtop": "JaggedTopCar",
    "slopetop": "SlopeTopCar",
    # Michie vocabulary
    "rectangle": "RectangleCar", "u_shaped": "UShapedCar", "bucket": "BucketCar",
}
ROOF_CLASS = {"none": "NoRoofCar", "flat": "FlatRoofCar", "peaked": "PeakedRoofCar",
              "jagged": "JaggedRoofCar", "arc": "ArcRoofCar"}
LOAD_CLASS = {"circle": "CircleLoad", "triangle": "TriangleLoad",
              "rectangle": "RectangleLoad", "hexagon": "HexagonLoad",
              "diamond": "DiamondLoad", "utriangle": "UTriangleLoad"}
OPEN_SHAPES = {"openrect", "opentrap", "ushaped", "dblopnrect"}


class OntologyBuilder:
    def __init__(self, name: str, comment: str):
        self.g = Graph()
        self.g.bind("", T)
        self.g.bind("owl", OWL)
        ont = URIRef(f"{BASE}/{name}")
        self.g.add((ont, RDF.type, OWL.Ontology))
        self.g.add((ont, RDFS.comment, Literal(comment)))
        self.declared: set[str] = set()

    # ---- TBox helpers ---------------------------------------------------
    def cls(self, name: str, parent: str | None = None, comment: str | None = None) -> URIRef:
        c = T[name]
        if name not in self.declared:
            self.g.add((c, RDF.type, OWL.Class))
            self.declared.add(name)
            if comment:
                self.g.add((c, RDFS.comment, Literal(comment)))
        if parent:
            self.g.add((c, RDFS.subClassOf, T[parent]))
        return c

    def disjoint(self, *names: str) -> None:
        names = [n for n in names if n in self.declared]
        if len(names) < 2:
            return
        if len(names) == 2:
            self.g.add((T[names[0]], OWL.disjointWith, T[names[1]]))
            return
        node = BNode()
        self.g.add((node, RDF.type, OWL.AllDisjointClasses))
        lst = BNode()
        Collection(self.g, lst, [T[n] for n in names])
        self.g.add((node, OWL.members, lst))

    def obj_prop(self, name, domain, rng, comment=None, functional=False):
        p = T[name]
        self.g.add((p, RDF.type, OWL.ObjectProperty))
        self.g.add((p, RDFS.domain, T[domain]))
        self.g.add((p, RDFS.range, T[rng]))
        if functional:
            self.g.add((p, RDF.type, OWL.FunctionalProperty))
        if comment:
            self.g.add((p, RDFS.comment, Literal(comment)))

    def data_prop(self, name, domain, comment=None):
        p = T[name]
        self.g.add((p, RDF.type, OWL.DatatypeProperty))
        self.g.add((p, RDF.type, OWL.FunctionalProperty))
        self.g.add((p, RDFS.domain, T[domain]))
        self.g.add((p, RDFS.range, XSD.integer))
        if comment:
            self.g.add((p, RDFS.comment, Literal(comment)))

    # ---- ABox helpers ---------------------------------------------------
    def ind(self, name: str, *classes: str) -> URIRef:
        i = T[name]
        self.g.add((i, RDF.type, OWL.NamedIndividual))
        for c in classes:
            self.g.add((i, RDF.type, T[c]))
        return i

    def only_nominals(self, subject: URIRef, prop: str, members: list[URIRef]) -> None:
        """subject : ∀prop.{m1,...,mn}  (or ∀prop.⊥ if no members)."""
        restr = BNode()
        self.g.add((restr, RDF.type, OWL.Restriction))
        self.g.add((restr, OWL.onProperty, T[prop]))
        if members:
            one_of = BNode()
            self.g.add((one_of, RDF.type, OWL.Class))
            lst = BNode()
            Collection(self.g, lst, members)
            self.g.add((one_of, OWL.oneOf, lst))
            self.g.add((restr, OWL.allValuesFrom, one_of))
        else:
            self.g.add((restr, OWL.allValuesFrom, OWL.Nothing))
        self.g.add((subject, RDF.type, restr))


def build(ds: dict, closed: bool) -> Graph:
    b = OntologyBuilder(ds["name"] + ("_closed" if closed else ""),
                        ds["description"] + (" [with closure axioms]" if closed else ""))
    trains = ds["trains"]
    cars = [c for t in trains for c in t["cars"]]
    has_roof = any("roof" in c for c in cars)

    # ---------------- TBox ----------------
    b.cls("Train"); b.cls("Car"); b.cls("Load")
    b.disjoint("Train", "Car", "Load")

    b.cls("ShortCar", "Car"); b.cls("LongCar", "Car")
    b.disjoint("ShortCar", "LongCar")
    b.cls("OpenCar", "Car", "car without a roof (open top)")
    b.cls("ClosedCar", "Car", "car with a roof (closed top)")
    b.disjoint("OpenCar", "ClosedCar")
    b.cls("TwoWheelCar", "Car"); b.cls("ThreeWheelCar", "Car")
    b.disjoint("TwoWheelCar", "ThreeWheelCar")

    shapes = sorted({c["shape"] for c in cars})
    for s in shapes:
        if has_roof:  # Michie: shape is the body; open/closed comes from the roof
            b.cls(SHAPE_CLASS[s], "Car")
        else:         # Michalski: shape determines open/closed (UCI hierarchy)
            b.cls(SHAPE_CLASS[s], "OpenCar" if s in OPEN_SHAPES else "ClosedCar")
    b.disjoint(*sorted({SHAPE_CLASS[s] for s in shapes}))

    if has_roof:
        roofs = sorted({c["roof"] for c in cars})
        for r in roofs:
            b.cls(ROOF_CLASS[r], "OpenCar" if r == "none" else "ClosedCar")
        b.disjoint(*[ROOF_CLASS[r] for r in roofs])
        b.cls("DoubleWallCar", "Car")

    load_shapes = sorted({l for c in cars for l in c["loads"]})
    for l in load_shapes:
        b.cls(LOAD_CLASS[l], "Load")
    b.disjoint(*[LOAD_CLASS[l] for l in load_shapes])

    b.obj_prop("hasCar", "Train", "Car", "a train has a wagon (engine excluded)")
    b.obj_prop("hasLoad", "Car", "Load", "a wagon carries a load object")
    b.obj_prop("inFrontOf", "Car", "Car",
               "c1 inFrontOf c2: c1 is directly in front of c2 in the same train",
               functional=True)
    b.data_prop("position", "Car", "position of the wagon in the train (engine = 1)")
    b.data_prop("wheels", "Car", "number of wheels per side")
    b.data_prop("loadCount", "Car", "number of loads on the wagon")
    b.data_prop("carCount", "Train", "number of wagons (engine excluded)")

    # ---------------- ABox ----------------
    for t in trains:
        ti = b.ind(t["id"], "Train")
        b.g.add((ti, T.carCount, Literal(len(t["cars"]), datatype=XSD.integer)))
        car_inds = []
        ordered = sorted(t["cars"], key=lambda c: c["pos"])
        for c in ordered:
            classes = [SHAPE_CLASS[c["shape"]],
                       "ShortCar" if c["length"] == "short" else "LongCar",
                       "ClosedCar" if c["closed"] else "OpenCar",
                       "TwoWheelCar" if c["wheels"] == 2 else "ThreeWheelCar"]
            if has_roof:
                classes.append(ROOF_CLASS[c["roof"]])
                if c["double"]:
                    classes.append("DoubleWallCar")
            ci = b.ind(c["id"], *classes)
            car_inds.append(ci)
            b.g.add((ti, T.hasCar, ci))
            b.g.add((ci, T.position, Literal(c["pos"], datatype=XSD.integer)))
            b.g.add((ci, T.wheels, Literal(c["wheels"], datatype=XSD.integer)))
            b.g.add((ci, T.loadCount, Literal(len(c["loads"]), datatype=XSD.integer)))
            load_inds = []
            for k, l in enumerate(c["loads"], 1):
                li = b.ind(f"{c['id']}_load{k}", LOAD_CLASS[l])
                load_inds.append(li)
                b.g.add((ci, T.hasLoad, li))
            if closed:
                b.only_nominals(ci, "hasLoad", load_inds)
        for a, nxt in zip(car_inds, car_inds[1:]):
            b.g.add((a, T.inFrontOf, nxt))
        if closed:
            b.only_nominals(ti, "hasCar", car_inds)
            if car_inds:  # last car has nobody behind it
                b.only_nominals(car_inds[-1], "inFrontOf", [])

    if closed:  # unique name assumption, needed for counting / nominals
        all_inds = sorted(set(b.g.subjects(RDF.type, OWL.NamedIndividual)))
        node = BNode()
        b.g.add((node, RDF.type, OWL.AllDifferent))
        lst = BNode()
        Collection(b.g, lst, all_inds)
        b.g.add((node, OWL.distinctMembers, lst))
    return b.g


def main() -> None:
    ONT.mkdir(exist_ok=True)
    for path in sorted(PROC.glob("*.json")):
        ds = json.loads(path.read_text())
        if "flipped" in ds:  # noisy copy: same ABox as its clean twin, only labels differ
            continue
        for closed in (False, True):
            g = build(ds, closed)
            out = ONT / f"{ds['name']}{'_closed' if closed else ''}.owl"
            g.serialize(out, format="xml")
            n_ind = len(set(g.subjects(RDF.type, OWL.NamedIndividual)))
            n_cls = len(set(g.subjects(RDF.type, OWL.Class)) - set(g.subjects(RDF.type, OWL.Restriction)))
            print(f"{out.name:34s} triples={len(g):6d} individuals={n_ind:5d} classes~{n_cls}")


if __name__ == "__main__":
    main()
