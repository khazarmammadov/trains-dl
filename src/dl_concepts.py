"""Parse DL-Learner class expressions (Manchester-like syntax) and evaluate them
on an ontology's ABox under closed-world semantics.

Why our own evaluator?  DL-Learner reports the accuracy of a concept on the
examples it was *trained* on. To measure generalisation on held-out trains we
need to classify unseen individuals with the learned concept. We do this with
the same semantics as DL-Learner's "closed world reasoner":

  * an individual is an instance of an atomic class A iff A (or a subclass of
    A) is asserted for it                                  (told + TBox closure)
  * ¬C             : not an instance of C                 (negation as failure)
  * ∃r.C           : some asserted r-filler is in C
  * ∀r.C           : every asserted r-filler is in C (vacuously true if none)
  * ≥n r.C / ≤n r.C / =n r.C : count of asserted r-fillers in C
  * ∃d.range       : some asserted value of data property d is in the range

Concept length follows DL-Learner's default "cel_metric":
  A, ⊤, ⊥ = 1;  ¬C = 1+|C|;  C⊓D, C⊔D = |C|+|D|+1 (n-ary: Σ + n-1);
  ∃r.C, ∀r.C = 1+1+|C|;  ≥n r.C = 1+1+1+|C| (the number counts as 1);
  ∃d.range = 1+1+1 (property, quantifier, range).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS

# ---------------------------------------------------------------------------
# AST
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Atomic:
    name: str  # local name, "Thing" or "Nothing"


@dataclass(frozen=True)
class Not:
    arg: "Concept"


@dataclass(frozen=True)
class And:
    args: tuple


@dataclass(frozen=True)
class Or:
    args: tuple


@dataclass(frozen=True)
class Some:
    prop: str
    filler: "Concept"


@dataclass(frozen=True)
class Only:
    prop: str
    filler: "Concept"


@dataclass(frozen=True)
class Card:
    kind: str  # min | max | exactly
    n: int
    prop: str
    filler: "Concept"


@dataclass(frozen=True)
class DataSome:
    prop: str
    facets: tuple  # ((op, value), ...)  op in >=,>,<=,<


@dataclass(frozen=True)
class DataValue:
    prop: str
    value: float


Concept = object  # union of the dataclasses above (py3.9-compatible alias)

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------
TOKEN_RE = re.compile(r"\s*(>=|<=|>|<|\(|\)|\[|\]|,|\{|\}|[^\s()\[\],{}]+)")
KEYWORDS = {"and", "or", "not", "some", "only", "min", "max", "exactly", "value"}
DATATYPES = {"integer", "int", "double", "float", "decimal", "xsd:integer",
             "xsd:int", "xsd:double", "xsd:decimal", "long", "xsd:long"}


def _local(name: str) -> str:
    name = name.strip("<>")
    for sep in ("#", "/", ":"):
        if sep in name:
            name = name.rsplit(sep, 1)[1]
    return name


class _Parser:
    def __init__(self, text: str):
        self.toks = TOKEN_RE.findall(text.strip())
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def take(self, expected=None):
        tok = self.peek()
        if tok is None or (expected is not None and tok != expected):
            raise ValueError(f"expected {expected!r}, got {tok!r} in {' '.join(self.toks)}")
        self.i += 1
        return tok

    def parse(self) -> Concept:
        c = self.or_expr()
        if self.peek() is not None:
            raise ValueError(f"trailing tokens: {self.toks[self.i:]}")
        return c

    def or_expr(self):
        args = [self.and_expr()]
        while self.peek() == "or":
            self.take()
            args.append(self.and_expr())
        return args[0] if len(args) == 1 else Or(tuple(args))

    def and_expr(self):
        args = [self.unary()]
        while self.peek() == "and":
            self.take()
            args.append(self.unary())
        return args[0] if len(args) == 1 else And(tuple(args))

    def unary(self):
        tok = self.peek()
        if tok == "not":
            self.take()
            return Not(self.unary())
        if tok == "(":
            self.take()
            c = self.or_expr()
            self.take(")")
            return c
        name = self.take()
        nxt = self.peek()
        if nxt in ("some", "only"):
            self.take()
            if self.peek() in DATATYPES:
                return DataSome(_local(name), self.datarange())
            filler = self.unary()
            return Some(_local(name), filler) if nxt == "some" else Only(_local(name), filler)
        if nxt in ("min", "max", "exactly"):
            self.take()
            n = int(self.take())
            filler = self.unary() if self.peek() not in (None, ")", "and", "or") else Atomic("Thing")
            return Card(nxt, n, _local(name), filler)
        if nxt == "value":
            self.take()
            v = self.take().strip('"').split("^^")[0].strip('"')
            return DataValue(_local(name), float(v))
        return Atomic(_local(name))

    def datarange(self):
        self.take()  # datatype name
        facets = []
        if self.peek() == "[":
            self.take("[")
            while self.peek() != "]":
                op = self.take()
                val = float(self.take().strip('"').split("^^")[0].strip('"'))
                facets.append((op, val))
                if self.peek() == ",":
                    self.take()
            self.take("]")
        return tuple(facets)


@lru_cache(maxsize=4096)
def parse(text: str) -> Concept:
    return _Parser(text).parse()


# ---------------------------------------------------------------------------
# Length / depth / pretty printing
# ---------------------------------------------------------------------------
def length(c: Concept) -> int:
    if isinstance(c, Atomic):
        return 1
    if isinstance(c, Not):
        return 1 + length(c.arg)
    if isinstance(c, (And, Or)):
        return sum(length(a) for a in c.args) + len(c.args) - 1
    if isinstance(c, (Some, Only)):
        return 2 + length(c.filler)
    if isinstance(c, Card):
        return 3 + length(c.filler)
    if isinstance(c, (DataSome, DataValue)):
        return 3
    raise TypeError(c)


def depth(c: Concept) -> int:
    if isinstance(c, (Atomic, DataSome, DataValue)):
        return 1
    if isinstance(c, Not):
        return depth(c.arg)
    if isinstance(c, (And, Or)):
        return max(depth(a) for a in c.args)
    if isinstance(c, (Some, Only, Card)):
        return 1 + depth(c.filler)
    raise TypeError(c)


def to_dl(c: Concept) -> str:
    """Pretty-print in DL notation (for the report)."""
    def paren(x):
        s = to_dl(x)
        return f"({s})" if isinstance(x, (And, Or)) else s
    if isinstance(c, Atomic):
        return {"Thing": "⊤", "Nothing": "⊥"}.get(c.name, c.name)
    if isinstance(c, Not):
        return "¬" + paren(c.arg)
    if isinstance(c, And):
        return " ⊓ ".join(paren(a) for a in c.args)
    if isinstance(c, Or):
        return " ⊔ ".join(paren(a) for a in c.args)
    if isinstance(c, Some):
        return f"∃{c.prop}.{paren(c.filler)}"
    if isinstance(c, Only):
        return f"∀{c.prop}.{paren(c.filler)}"
    if isinstance(c, Card):
        sym = {"min": "≥", "max": "≤", "exactly": "="}[c.kind]
        return f"{sym}{c.n} {c.prop}.{paren(c.filler)}"
    if isinstance(c, DataSome):
        rng = ", ".join(f"{op}{v:g}" for op, v in c.facets)
        return f"∃{c.prop}.[{rng}]"
    if isinstance(c, DataValue):
        return f"∃{c.prop}.{{{c.value:g}}}"
    raise TypeError(c)


# ---------------------------------------------------------------------------
# Closed-world model of an ontology
# ---------------------------------------------------------------------------
class ClosedWorldModel:
    def __init__(self, owl_path: str | Path):
        g = Graph()
        g.parse(str(owl_path), format="xml")
        loc = lambda u: _local(str(u))
        # TBox: named superclasses (reflexive-transitive closure)
        parents: dict[str, set[str]] = {}
        for s, o in g.subject_objects(RDFS.subClassOf):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                parents.setdefault(loc(s), set()).add(loc(o))

        def supers(c, seen=None):
            seen = seen or set()
            if c in seen:
                return seen
            seen.add(c)
            for p in parents.get(c, ()):
                supers(p, seen)
            return seen

        self.individuals: set[str] = {loc(s) for s in g.subjects(RDF.type, OWL.NamedIndividual)}
        self.types: dict[str, set[str]] = {i: {"Thing"} for i in self.individuals}
        obj_props = {loc(p) for p in g.subjects(RDF.type, OWL.ObjectProperty)}
        data_props = {loc(p) for p in g.subjects(RDF.type, OWL.DatatypeProperty)}
        self.obj: dict[str, dict[str, list[str]]] = {p: {} for p in obj_props}
        self.data: dict[str, dict[str, list[float]]] = {p: {} for p in data_props}
        for s, p, o in g:
            if not isinstance(s, URIRef):
                continue
            si = loc(s)
            if si not in self.individuals:
                continue
            if p == RDF.type and isinstance(o, URIRef) and o != OWL.NamedIndividual:
                self.types[si] |= supers(loc(o))
            elif loc(p) in obj_props:
                self.obj[loc(p)].setdefault(si, []).append(loc(o))
            elif loc(p) in data_props and isinstance(o, Literal):
                self.data[loc(p)].setdefault(si, []).append(float(o.toPython()))
        self._cache: dict[Concept, frozenset[str]] = {}

    def extension(self, c: Concept) -> frozenset[str]:
        if c in self._cache:
            return self._cache[c]
        res = frozenset(i for i in self.individuals if self.holds(c, i))
        self._cache[c] = res
        return res

    def holds(self, c: Concept, i: str) -> bool:
        if isinstance(c, Atomic):
            if c.name == "Thing":
                return True
            if c.name == "Nothing":
                return False
            return c.name in self.types.get(i, ())
        if isinstance(c, Not):
            return not self.holds(c.arg, i)
        if isinstance(c, And):
            return all(self.holds(a, i) for a in c.args)
        if isinstance(c, Or):
            return any(self.holds(a, i) for a in c.args)
        fillers = self.obj.get(getattr(c, "prop", ""), {}).get(i, [])
        if isinstance(c, Some):
            return any(self.holds(c.filler, j) for j in fillers)
        if isinstance(c, Only):
            return all(self.holds(c.filler, j) for j in fillers)
        if isinstance(c, Card):
            k = sum(self.holds(c.filler, j) for j in fillers)
            return {"min": k >= c.n, "max": k <= c.n, "exactly": k == c.n}[c.kind]
        if isinstance(c, DataSome):
            return any(all(_facet(v, op, x) for op, x in c.facets)
                       for v in self.data.get(c.prop, {}).get(i, []))
        if isinstance(c, DataValue):
            return c.value in self.data.get(c.prop, {}).get(i, [])
        raise TypeError(c)

    def classify(self, concept: str | Concept, individuals) -> list[int]:
        c = parse(concept) if isinstance(concept, str) else concept
        return [int(self.holds(c, i)) for i in individuals]


def _facet(v: float, op: str, x: float) -> bool:
    return {">=": v >= x, ">": v > x, "<=": v <= x, "<": v < x}[op]


if __name__ == "__main__":  # tiny self-test
    for s in ["hasCar some (ClosedCar and ShortCar)",
              "(not (LongCar)) and (hasCar some (ClosedCar and ShortCar))",
              "carCount some integer[>= 3 , <= 4]",
              "hasCar min 2 (ShortCar or (hasLoad only CircleLoad))",
              "Train and (hasCar only (OpenCar or LongCar))"]:
        c = parse(s)
        print(f"{to_dl(c):60s} len={length(c)} depth={depth(c)}")
