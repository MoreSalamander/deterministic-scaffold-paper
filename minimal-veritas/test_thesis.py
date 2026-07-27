"""Run with: pip install pytest && pytest

Each test here is a runnable version of a claim made in the paper's
Checkpoint III (Veritas). Nothing here talks to a real model or the
network — that's the point. If these pass on your machine, you have
independently reproduced the invariant, not just read about it.
"""

from gate import Artifact, Gate, decide
from model import ScriptedProvider


def _syntax_gate() -> Gate:
    """A real, deterministic check: does the proposed code contain a
    function definition at all? Hard — its failure blocks acceptance."""

    def check(artifact: Artifact) -> "GateResult":
        from gate import GateResult

        code = str(artifact.payload)
        passed = "def " in code
        return GateResult(gate_name="syntax", passed=passed, evidence=code[:60])

    return Gate("syntax", check, hard=True)


def _acceptance_gate(expects_raises: bool) -> Gate:
    """A real, deterministic check: does the function raise ValueError on
    negative input, per spec? Hard — this is the actual behavioral spec,
    not a model's opinion of the behavioral spec."""

    def check(artifact: Artifact) -> "GateResult":
        from gate import GateResult

        code = str(artifact.payload)
        has_guard = "raise ValueError" in code
        return GateResult(
            gate_name="acceptance",
            passed=has_guard == expects_raises,
            evidence=f"raise ValueError present: {has_guard}",
        )

    return Gate("acceptance", check, hard=True)


def _qa_gate_that_wrongly_flags() -> Gate:
    """A stand-in for an LLM-judged QA gate. This one is SCRIPTED to be
    wrong on purpose — replaying the real P2 moment where the QA agent
    flagged a correct factorial() implementation. Soft — its opinion is
    recorded, never a veto."""

    def check(artifact: Artifact) -> "GateResult":
        from gate import GateResult

        qa_opinion = ScriptedProvider(
            by_role={"qa": "REJECT — looks suspicious to me"}
        ).propose(role="qa", prompt=str(artifact.payload))
        return GateResult(gate_name="qa", passed=False, evidence=qa_opinion)

    return Gate("qa", check, hard=False)


CORRECT_FACTORIAL = """
def factorial(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    return 1 if n == 0 else n * factorial(n - 1)
"""


def test_zero_hard_gates_never_accept():
    """No hard gate configured -> never accepted, no matter what a soft
    gate or the proposer thinks. This is the floor the paper calls
    'nothing is ever silently accepted by default.'"""
    artifact = Artifact(payload=CORRECT_FACTORIAL, proposer="llama3.1:8b")
    verdict = decide(artifact, gates=[_qa_gate_that_wrongly_flags()])
    assert verdict.accepted is False


def test_qa_dissent_does_not_block_hard_verified_code():
    """The real live moment from Veritas P2: a correct factorial() with a
    ValueError guard, judged INCORRECTLY by a soft QA gate. The paper's
    claim is that this dissent is recorded but never blocks. Prove it."""
    artifact = Artifact(payload=CORRECT_FACTORIAL, proposer="llama3.1:8b")
    gates = [_syntax_gate(), _acceptance_gate(expects_raises=True), _qa_gate_that_wrongly_flags()]

    verdict = decide(artifact, gates)

    assert verdict.accepted is True, "hard gates passed; QA's wrong opinion must not block"

    qa_result = next(r for r in verdict.results if r.gate_name == "qa")
    assert qa_result.passed is False, "the dissent must be ON THE RECORD, not smoothed over"


def test_a_failing_hard_gate_blocks_even_with_a_happy_soft_gate():
    """The mirror case: if the real behavioral spec fails (no ValueError
    guard), acceptance must fail regardless of what any soft gate says."""
    broken_factorial = "def factorial(n):\n    return 1 if n == 0 else n * factorial(n - 1)\n"
    artifact = Artifact(payload=broken_factorial, proposer="llama3.1:8b")
    gates = [_syntax_gate(), _acceptance_gate(expects_raises=True)]

    verdict = decide(artifact, gates)

    assert verdict.accepted is False
