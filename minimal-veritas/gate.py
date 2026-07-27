"""Minimal Gate — the decision engine, stripped to the invariant this paper is about.

This is NOT the real Veritas engine/gate.py. It is a deliberately small
re-derivation of the same shape, built so a reader can run it without
installing Veritas, Ollama, or any API key. Compare against the real
source cited in Appendix A.2 of the paper — same invariant, this file
is a fraction of the size.

The rule: a gate is a function Artifact -> GateResult. It is the only
thing allowed to say yes or no. An LLM (or anything else) may PROPOSE.
Nothing it proposes is trusted until a gate decides.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Artifact:
    """Something an agent produced and wants trusted. Just data — it cannot
    certify itself."""

    payload: object
    proposer: str


@dataclass
class GateResult:
    """A verdict, always with evidence. Never a bare boolean."""

    gate_name: str
    passed: bool
    evidence: str


@dataclass
class Verdict:
    """The final decision on an Artifact, after every gate has run."""

    accepted: bool
    results: list[GateResult] = field(default_factory=list)


class Gate:
    """A single check. `check` must never consult the proposer's own
    opinion of its own output — that would make the grader the thing it
    grades. `hard=True` means this gate's failure blocks acceptance.
    `hard=False` (soft) means its verdict is recorded but never blocks —
    honest advisory, not a veto. A gate that is itself an LLM (e.g. a QA
    agent judging code) MUST be soft, because it cannot certify its own
    judgment as ground truth."""

    def __init__(self, name: str, check: Callable[[Artifact], GateResult], hard: bool = True):
        self.name = name
        self._check = check
        self.hard = hard

    def run(self, artifact: Artifact) -> GateResult:
        return self._check(artifact)


def decide(artifact: Artifact, gates: list[Gate]) -> Verdict:
    """The one invariant this whole paper is about: an artifact is accepted
    if and only if at least one HARD gate exists and every HARD gate
    passes. SOFT gates always run and their results are always recorded —
    a dissenting soft gate is visible, never hidden — but a soft failure
    can never by itself block acceptance. Zero hard gates configured means
    nothing is ever silently accepted by default."""
    results = [gate.run(artifact) for gate in gates]
    hard_results = [r for g, r in zip(gates, results) if g.hard]
    accepted = len(hard_results) > 0 and all(r.passed for r in hard_results)
    return Verdict(accepted=accepted, results=results)
