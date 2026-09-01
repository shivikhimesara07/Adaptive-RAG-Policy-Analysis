from corpus import get_chunk
from policy_diff import (
    _fallback_rule_based_extraction,
    extract_structured_change, verify_grounding,
)

MAX_RETRIES = 1

def draft_and_verify_change(v1_id: str, v2_id: str) -> dict:
    
  v1_chunk, v2_chunk = get_chunk(v1_id), get_chunk(v2_id)

    change= extract_structured_change(v1_chunk, v2_chunk)
    change= verify_grounding(change, v1_chunk["text"], v2_chunk["text"])
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
  
    from corpus import changed_pairs
    chunk_id_set= set(chunk_ids)
    pairs = []
    for v1_id, v2_id in changed_pairs():
        if v1_id in chunk_id_set or v2_id in chunk_id_set:
            pairs.append((v1_id, v2_id))
    return pairs

def run_agentic_synthesis(chunk_ids: list) -> list:
    pairs = find_changed_pairs_in(chunk_ids)
    return [draft_and_verify_change(v1, v2) for v1, v2 in pairs]
