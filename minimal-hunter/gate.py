"""Minimal Hunter gate — the monotonic-evidence rule, isolated.

NOT the real crypto-hunter/engine/gate.py (see Appendix A.3 of the paper
for the real file). This is small enough to read in one pass, built so a
reader can reproduce the exact rule found live on Crypto Hunter's first
day, with no network calls and no API key.

The rule, in one sentence: a source that CANNOT be validated is EXCLUDED
from evidence, never used to demote a candidate — except a scam-listed
domain, which is a hard fail from anywhere, the one deliberate exception
to monotonicity.
"""

from __future__ import annotations

from dataclasses import dataclass, field


KNOWN_SCAM_DOMAINS = {"totally-legit-airdrop.xyz", "free-eth-now.info"}


@dataclass
class Source:
    domain: str
    validated: bool  # could this source actually be confirmed (e.g. RDAP resolved)?


@dataclass
class OpportunitySpec:
    name: str
    sources: list[Source] = field(default_factory=list)


@dataclass
class GateResult:
    passed: bool
    evidence: str


def evaluate(spec: OpportunitySpec) -> GateResult:
    """Evidence is monotonic: an unvalidated source is excluded from the
    count (never counted as a demotion), UNLESS its domain is scam-listed,
    which hard-fails regardless of validation status. This means an RDAP
    outage or a flaky lookup can only ever make evidence WEAKER (fewer
    countable sources), never flip a candidate to rejected on its own —
    except through the scam-list exception, which needs no validation at
    all to hard-fail."""
    for source in spec.sources:
        if source.domain in KNOWN_SCAM_DOMAINS:
            return GateResult(
                passed=False,
                evidence=f"hard fail: {source.domain} is scam-listed (validation status irrelevant)",
            )

    validated_sources = [s for s in spec.sources if s.validated]
    if not validated_sources:
        return GateResult(passed=False, evidence="no validated sources — nothing to accept on")

    return GateResult(
        passed=True,
        evidence=f"{len(validated_sources)} validated source(s), 0 scam hits",
    )
