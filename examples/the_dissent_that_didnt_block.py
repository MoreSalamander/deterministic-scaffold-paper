"""Run with: python3 examples/the_dissent_that_didnt_block.py

A narrated replay of one real moment (Veritas P2, cited in the paper and
in Appendix A.2): llama3.1:8b shipped a correct factorial() with a
ValueError guard on negative input. A soft QA gate — itself an LLM —
wrongly flagged it as suspicious. The system recorded the dissent and
shipped the code anyway, because the hard gates had already decided.

This script does not assert anything; it just prints the trace so you
can watch it happen instead of reading a description of it happening.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "minimal-veritas"))

from gate import Artifact, GateResult, Gate, decide  # noqa: E402
from model import ScriptedProvider  # noqa: E402

CORRECT_FACTORIAL = """
def factorial(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    return 1 if n == 0 else n * factorial(n - 1)
"""


def syntax_gate() -> Gate:
    def check(a: Artifact) -> GateResult:
        return GateResult("syntax", passed="def " in str(a.payload), evidence="has a function def")

    return Gate("syntax", check, hard=True)


def acceptance_gate() -> Gate:
    def check(a: Artifact) -> GateResult:
        has_guard = "raise ValueError" in str(a.payload)
        return GateResult("acceptance", passed=has_guard, evidence="ValueError guard present")

    return Gate("acceptance", check, hard=True)


def qa_gate() -> Gate:
    def check(a: Artifact) -> GateResult:
        opinion = ScriptedProvider(
            by_role={"qa": "REJECT — this looks suspicious to me"}
        ).propose(role="qa", prompt=str(a.payload))
        return GateResult("qa", passed=False, evidence=opinion)

    return Gate("qa", check, hard=False)


def main() -> None:
    print("Proposer (llama3.1:8b) submits:")
    print(CORRECT_FACTORIAL)

    artifact = Artifact(payload=CORRECT_FACTORIAL, proposer="llama3.1:8b")
    verdict = decide(artifact, gates=[syntax_gate(), acceptance_gate(), qa_gate()])

    print("Gate results:")
    for r in verdict.results:
        tag = "PASS" if r.passed else "FAIL"
        print(f"  [{tag}] {r.gate_name}: {r.evidence}")

    print()
    print(f"Final verdict: {'ACCEPTED' if verdict.accepted else 'REJECTED'}")
    print(
        "The QA gate's dissent is visible above and changed nothing — "
        "it is soft, so it is recorded, not obeyed."
    )


if __name__ == "__main__":
    main()
