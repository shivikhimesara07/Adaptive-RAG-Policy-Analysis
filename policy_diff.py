import json
import os
import re

GEMINI_MODEL = "gemini-2.0-flash"

EXTRACTION_SYSTEM_PROMPT = """You are a healthcare policy analyst. You will be given
one section of a policy in two versions (v1 and v2). Identify the single most
significant substantive change between them.

Respond with ONLY a JSON object (no markdown fences, no commentary) with these fields:
{
  "field_changed": 
  short label for what changed,
  "change_type": one of "visit_cap", "dollar_threshold", "percentage_rate", "other",
  "old_value": the old numeric value (number only, no symbols),
  "new_value": the new numeric value (number only, no symbols),
  "effective_date": the effective date of the new policy version, if stated,
  "quoted_clause_v1": the exact sentence from v1 that states the old value (verbatim, no edits),
  "quoted_clause_v2": the exact sentence from v2 that states the new value (verbatim, no edits)
}
"""
_VALUE_PATTERNS = [
    (r"maximum of (\d+) visits", "visit_cap", "Visit cap"),
    (r"exceeding \$([\d,]+)", "dollar_threshold", "Prior-auth dollar threshold"),
    (r"reimbursed at (\d+)% of", "percentage_rate", "Reimbursement rate"),
]

def extract_structured_change(v1_chunk: dict, v2_chunk: dict) -> dict:
    if os.environ.get("GEMINI_API_KEY"):
        try:
            return _extract_with_gemini(v1_chunk["text"], v2_chunk["text"])
        except Exception as e:
            print(f"[warn] Gemini extraction failed ({e}); using rule-based fallback.")
    return _fallback_rule_based_extraction(v1_chunk, v2_chunk)


def _parse_json_response(raw_text: str) -> dict:
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def _extract_with_gemini(policy_v1: str, policy_v2: str) -> dict:
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = f"{EXTRACTION_SYSTEM_PROMPT}\n\nSECTION V1:\n{policy_v1}\n\nSECTION V2:\n{policy_v2}"
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return _parse_json_response(response.text)


def _find_sentence(text: str, keyword_pattern: str) -> str:
    for para in re.split(r"\n\s*\n", text.strip()):
        for sentence in re.split(r"(?<=[.])\s+", para.replace("\n", " ").strip()):
            if re.search(keyword_pattern, sentence):
                return sentence.strip()
    return ""


def _fallback_rule_based_extraction(v1_chunk: dict, v2_chunk: dict) -> dict:
    v1_text, v2_text = v1_chunk["text"], v2_chunk["text"]

    for pattern, change_type, field_label in _VALUE_PATTERNS:
        m1 = re.search(pattern, v1_text)
        m2 = re.search(pattern, v2_text)
        if m1 and m2:
            old_val = m1.group(1).replace(",", "")
            new_val = m2.group(1).replace(",", "")
            if old_val == new_val:
                continue
            return {
                "field_changed": f"{field_label} ({v1_chunk['doc']}, {v1_chunk['section']})",
                "change_type": change_type,
                "old_value": old_val,
                "new_value": new_val,
                "effective_date": v2_chunk["effective_date"],
                "quoted_clause_v1": _find_sentence(v1_text, pattern.split(" ")[0]) or v1_text.strip().split(".")[0] + ".",
                "quoted_clause_v2": _find_sentence(v2_text, pattern.split(" ")[0]) or v2_text.strip().split(".")[0] + ".",
            }

    return {
        "field_changed": f"Qualitative change ({v1_chunk['doc']}, {v1_chunk['section']})",
        "change_type": "other",
        "old_value": None,
        "new_value": None,
        "effective_date": v2_chunk["effective_date"],
        "quoted_clause_v1": v1_text.strip().split(".")[0] + ".",
        "quoted_clause_v2": v2_text.strip().split(".")[0] + ".",
    }


def verify_grounding(change: dict, v1_text: str, v2_text: str) -> dict:
    """
    Critic step, with two types of independent checks and both of them must pass:

    1. Quote-verbatim: does the quoted clause actually appear
       (near-verbatim,whitespace/case-normalized) in source text?
       Catches an extractor paraphrasing instead of copying.
    2. Value-grounded: does the quoted clause actually CONTAIN the
       old_value/new_value being claimed? A quote can be 100% verbatim -
       genuinely present in the source, while being the wrong clause,
       i.e. real text that doesn't support the number attached to it.
       Checking verbatim-presence alone misses this; this is the failure
       mode that actually matters for a financial extraction.
    """
    def normalize(s: str) -> str:
        return re.sub(r"\s+", " ", s or "").strip().lower()

    v1_norm, v2_norm = normalize(v1_text), normalize(v2_text)
    q1_norm = normalize(change.get("quoted_clause_v1", ""))
    q2_norm = normalize(change.get("quoted_clause_v2", ""))

    grounded_v1 = bool(q1_norm) and q1_norm in v1_norm
    grounded_v2 = bool(q2_norm) and q2_norm in v2_norm

    old_val, new_val = change.get("old_value"), change.get("new_value")
    if old_val is not None and new_val is not None:
      
        q1_digits = re.sub(r"[^0-9.]", "", q1_norm)
        q2_digits = re.sub(r"[^0-9.]", "", q2_norm)
        value_grounded_v1 = str(old_val) in q1_norm or str(old_val) in q1_digits
        value_grounded_v2 = str(new_val) in q2_norm or str(new_val) in q2_digits
    else:
     
        value_grounded_v1 = value_grounded_v2 = True

    fully_grounded = grounded_v1 and grounded_v2 and value_grounded_v1 and value_grounded_v2

    change["grounding"] = {
        "v1_quote_verified": grounded_v1,
        "v2_quote_verified": grounded_v2,
        "v1_value_grounded": value_grounded_v1,
        "v2_value_grounded": value_grounded_v2,
        "status": "GROUNDED" if fully_grounded else "FLAGGED - manual review required",
    }
    return change
