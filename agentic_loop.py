"""
Agentic drafting loop, in the Self-RAG sense of "generate, then let the
model's own critic decide whether to accept, retry, or abstain" rather
than a single-shot extraction.

For each candidate change:
  1. DRAFT   - extract_structured_change() produces a candidate.
  2. CRITIQUE - verify_grounding() checks the quoted clauses are real.
  3. If ungrounded: RETRY once using the deterministic rule-based
     extractor as a verified-safe fallback strategy (this is the retry
     path that matters most in practice - it's what catches an LLM
     paraphrasing a quote instead of copying it verbatim).
  4. If still ungrounded after retry: ABSTAIN - flag for human review
     rather than emit an unverified number into the financial brief.

This loop is what the "critic agent" bullet actually refers to: not just
a single pass/fail check, but a retry-then-abstain policy around it.
"""

from corpus import get_chunk
from policy_diff import (
    _fallback_rule_based_extraction,
    extract_structured_change,
    verify_grounding,
)

MAX_RETRIES = 1


def draft_and_verify_change(v1_id: str, v2_id: str) -> dict:
    v1_chunk, v2_chunk = get_chunk(v1_id), get_chunk(v2_id)

    change = extract_structured_change(v1_chunk, v2_chunk)
    change = verify_grounding(change, v1_chunk["text"], v2_chunk["text"])
    change["retries_used"] = 0
    change["source_ids"] = (v1_id, v2_id)

    retries = 0
    while change["grounding"]["status"] != "GROUNDED" and retries < MAX_RETRIES:
        retries += 1
        change = _fallback_rule_based_extraction(v1_chunk, v2_chunk)
        change = verify_grounding(change, v1_chunk["text"], v2_chunk["text"])
        change["retries_used"] = retries
        change["source_ids"] = (v1_id, v2_id)

    change["final_status"] = (
        "GROUNDED" if change["grounding"]["status"] == "GROUNDED" else "ABSTAINED - human review"
    )
    return change


def find_changed_pairs_in(chunk_ids: list) -> list:
    """
    Given a set of retrieved chunk_ids, find which (v1, v2) section pairs
    are represented - i.e. which retrieved sections actually changed
    between versions and are therefore worth drafting a change for.
    """
    from corpus import changed_pairs

    chunk_id_set = set(chunk_ids)
    pairs = []
    for v1_id, v2_id in changed_pairs():
        if v1_id in chunk_id_set or v2_id in chunk_id_set:
            pairs.append((v1_id, v2_id))
    return pairs


def run_agentic_synthesis(chunk_ids: list) -> list:
    """
    COMPLEX-tier entry point: for every changed section touched by the
    retrieved chunk set, draft + verify a structured change, retrying
    once through the deterministic extractor if the first draft doesn't
    ground. Returns one verified (or abstained) change per section.
    """
    pairs = find_changed_pairs_in(chunk_ids)
    return [draft_and_verify_change(v1, v2) for v1, v2 in pairs]
