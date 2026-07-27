# The Deterministic Scaffold — companion repository

This is the companion repo for [*The deterministic scaffold: a case study in
compounding architecture*](paper.pdf) — a paper tracing one architectural
invariant (an LLM proposes; a deterministic gate decides) across nine
checkpoints of a real, shipped body of work.

**This repo is not the production code.** It contains small, dependency-free
reproductions of two specific claims from the paper, built so a skeptical
reader can verify them by running tests, not by trusting prose.

## What's here

- `minimal-veritas/` — a ~60-line reproduction of Veritas's `Gate` invariant:
  acceptance requires every *hard* gate to pass; a *soft* gate's dissent is
  recorded but never blocks. `test_thesis.py` replays the real Veritas P2
  moment where a soft QA gate wrongly flagged a correct `factorial()` — and
  proves the dissent didn't block acceptance.
- `minimal-hunter/` — a ~40-line reproduction of Crypto Hunter's
  monotonic-evidence gate law: an unvalidated source is excluded from
  evidence, never used to demote a candidate, except a scam-listed domain,
  which hard-fails regardless of validation.
- `examples/the_dissent_that_didnt_block.py` — a narrated, runnable replay
  of the QA-dissent moment. Run it and read the trace as it happens.
- `paper.pdf` — the full paper, rendered from the published artifact.

## Run it

```bash
pip install pytest

cd minimal-veritas && pytest -v
cd ../minimal-hunter && pytest -v
cd .. && python3 examples/the_dissent_that_didnt_block.py
```

No API key. No local model server. No Docker. Every test name here matches
a real test cited in the paper's Appendix A — this is the same claim as the
production code, not a simplified stand-in for it.

## Relationship to the real repos

This is illustrative, not extracted. The real implementations are:
[Veritas](https://github.com/MoreSalamander/veritas),
[Crypto Hunter AI](https://github.com/MoreSalamander/crypto-hunter),
[Opportunity \[Agency AI\]](https://github.com/MoreSalamander/opportunity-agency-ai),
[hunter-engine](https://github.com/MoreSalamander/hunter-engine).

Part of [MoreSalamander StudioLabs](https://moresalamander.github.io).
