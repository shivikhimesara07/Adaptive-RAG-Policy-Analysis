"""

Three trial types:
  CLEAN: correct quote, correct value. Critic should pass it.
  WRONG_CLAUSE: a real sentence from elsewhere in the same document, swapped in as quote. Verbatim-only checking would wrongly pass this; value-grounded checking should catch it.
  WORD_EDIT : a genuinely paraphrased quote (word swapped). Included for completeness, but reported separately since it's the easy case both check types will always catch.
"""

import random
import re

from corpus import changed_pairs, get_chunk
from policy_diff import _fallback_rule_based_extraction, verify_grounding

_WORD_SUBS = {
    "maximum":"upper limit",
    "visits": "sessions",
    "exceeding":  "above",
    "reimbursed":"paid",
    "contracted" : "agreed",
}

def _split_sentences(text: str) -> list:
    sentences=[]
    for para in re.split(r"\n\s*\n", text.strip()):
        for s in re.split(r"(?<=[.])\s+", para.replace("\n", " ").strip()):
            s = s.strip()
            if s:
                sentences.append(s)
    return sentences


def _word_edit(quote: str) -> str:
    words = quote.split()
    for i, w in enumerate(words):
        key = w.strip(".,").lower()
        if key in _WORD_SUBS:
            words[i] = _WORD_SUBS[key]
            break
    else:
        if len(words) > 4:
            del words[len(words) // 2]
    return " ".join(words)


def _wrong_clause(correct_quote: str, source_text: str, claimed_value, rng: random.Random):

    candidates = [
        s for s in _split_sentences(source_text)
        if s != correct_quote and (claimed_value is None or str(claimed_value) not in s)
    ]
    return rng.choice(candidates) if candidates else None


def run_eval(n_trials: int = 200, seed: int = 42) -> dict:
    rng = random.Random(seed)
    pairs = changed_pairs()
    if not pairs:
        raise ValueError("No changed pairs found in corpus.")

    counts = {
        "CLEAN": {"total": 0, "flagged": 0},
        "WRONG_CLAUSE_QUANT": {"total": 0, "flagged": 0},
        "WRONG_CLAUSE_QUAL": {"total": 0, "flagged": 0},
        "WORD_EDIT": {"total": 0, "flagged": 0},
    }

    for _ in range(n_trials):
        v1_id, v2_id = rng.choice(pairs)
        v1_chunk, v2_chunk = get_chunk(v1_id), get_chunk(v2_id)
        change = _fallback_rule_based_extraction(v1_chunk, v2_chunk)

        trial_type = rng.choice(["CLEAN", "WRONG_CLAUSE", "WORD_EDIT"])

        if trial_type == "WRONG_CLAUSE":
            side, source_text = rng.choice([
                ("quoted_clause_v1", v1_chunk["text"]),
                ("quoted_clause_v2", v2_chunk["text"]),
            ])
            claimed_value = change["old_value"] if side.endswith("v1") else change["new_value"]
            swap = _wrong_clause(change[side], source_text, claimed_value, rng)
            if swap is None:
                trial_type = "CLEAN"
            else:
                change[side] = swap
                trial_type = "WRONG_CLAUSE_QUANT" if claimed_value is not None else "WRONG_CLAUSE_QUAL"

        elif trial_type == "WORD_EDIT":
            side = rng.choice(["quoted_clause_v1", "quoted_clause_v2"])
            change[side] = _word_edit(change[side])

        change = verify_grounding(change, v1_chunk["text"], v2_chunk["text"])
        flagged = change["grounding"]["status"] != "GROUNDED"

        counts[trial_type]["total"] += 1
        counts[trial_type]["flagged"] += int(flagged)

    def rate(t):
        c = counts[t]
        return round(100 * c["flagged"] / c["total"], 1) if c["total"] else None

    return {
        "n_trials": n_trials,
        "clean_total": counts["CLEAN"]["total"],
        "clean_false_flagged": counts["CLEAN"]["flagged"],
        "false_positive_rate": rate("CLEAN"),
        "wrong_clause_quant_total": counts["WRONG_CLAUSE_QUANT"]["total"],
        "wrong_clause_quant_caught": counts["WRONG_CLAUSE_QUANT"]["flagged"],
        "wrong_clause_quant_catch_rate": rate("WRONG_CLAUSE_QUANT"),
        "wrong_clause_qual_total": counts["WRONG_CLAUSE_QUAL"]["total"],
        "wrong_clause_qual_caught": counts["WRONG_CLAUSE_QUAL"]["flagged"],
        "wrong_clause_qual_catch_rate": rate("WRONG_CLAUSE_QUAL"),
        "word_edit_total": counts["WORD_EDIT"]["total"],
        "word_edit_caught": counts["WORD_EDIT"]["flagged"],
        "word_edit_catch_rate": rate("WORD_EDIT"),
    }


if __name__ == "__main__":
    r = run_eval()
    print(f"Trials: {r['n_trials']}")
    print(f"False positive rate on clean quotes: {r['false_positive_rate']}% "
          f"({r['clean_false_flagged']}/{r['clean_total']})")
    print(f"Catch rate, wrong-clause/ quantifiable changes: {r['wrong_clause_quant_catch_rate']}% "
          f"({r['wrong_clause_quant_caught']}/{r['wrong_clause_quant_total']})")
    print(f"Catch rate, wrong-clause /qualitative changes: {r['wrong_clause_qual_catch_rate']}% "
          f"({r['wrong_clause_qual_caught']}/{r['wrong_clause_qual_total']})  <- known gap, no value to check")
    print(f"Catch rate, paraphrased quotes: {r['word_edit_catch_rate']}% "
          f"({r['word_edit_caught']}/{r['word_edit_total']})")
