"""Run with: pip install pytest && pytest

Each test replays a real gate law found live on Crypto Hunter's first
production day (Checkpoint VI of the paper, Appendix A.3). Same claim,
same test names in spirit, a fraction of the real file's size.
"""

from gate import GateResult, OpportunitySpec, Source, evaluate


def test_evidence_is_monotonic():
    """An unresolvable/unvalidated source must not, by itself, sink an
    otherwise-legitimate candidate that has at least one real validated
    source. It is excluded from the count, not treated as a demotion."""
    spec = OpportunitySpec(
        name="Real Airdrop",
        sources=[
            Source(domain="official-project.io", validated=True),
            Source(domain="some-aggregator-that-timed-out.example", validated=False),
        ],
    )
    result = evaluate(spec)
    assert result.passed is True, "one validated source should be enough despite one unresolved source"


def test_no_validated_sources_fails_honestly():
    """If literally nothing can be validated, the candidate must fail —
    monotonic doesn't mean 'benefit of the doubt', it means 'bad evidence
    can't actively demote', which is a different, narrower guarantee."""
    spec = OpportunitySpec(
        name="Unverifiable Thing",
        sources=[Source(domain="cant-resolve.example", validated=False)],
    )
    result = evaluate(spec)
    assert result.passed is False


def test_scam_taint_is_the_monotonicity_exception():
    """The one deliberate exception: a scam-listed domain anywhere in the
    source list hard-fails the candidate, even alongside a validated
    legitimate source. Monotonicity protects against FLAKY evidence, not
    against KNOWN-BAD evidence."""
    spec = OpportunitySpec(
        name="Impersonation Attempt",
        sources=[
            Source(domain="official-project.io", validated=True),
            Source(domain="totally-legit-airdrop.xyz", validated=True),
        ],
    )
    result = evaluate(spec)
    assert result.passed is False
    assert "scam-listed" in result.evidence
