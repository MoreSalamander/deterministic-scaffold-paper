"""A scripted stand-in for an LLM proposer.

The real Veritas swaps this class for OllamaProvider / ClaudeProvider behind
the identical `propose()` interface — that seam is the whole point (see
checkpoint III of the paper). This file only needs to prove the CONTRACT,
not talk to a real model, so a reader can run the tests with no API key
and no local model server.
"""

from __future__ import annotations


class ScriptedProvider:
    """Returns a canned answer per role. Deterministic fake — proves the
    pipeline works with no model actually running."""

    def __init__(self, by_role: dict[str, str]):
        self._by_role = by_role

    def propose(self, *, role: str, prompt: str) -> str:
        if role not in self._by_role:
            raise KeyError(f"no scripted response for role {role!r}")
        return self._by_role[role]
