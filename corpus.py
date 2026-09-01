CORPUS = {
  
    # Doc1: Outpatient Physical Therapy Coverage Policy

    "pt_4.1_v1": {
        "doc": "Outpatient PT Coverage Policy",
        "section": "4.1 Overview",
        "version": "v1",
        "effective_date": "2025-01-01",
        "text": (
            "This policy governs coverage for outpatient physical therapy "
            "services delivered as part of a single episode of care. See "
            "Section 4.2 for visit limits and Section 4.4 for prior "
            "authorization requirements."
        ),
        "refs": ["pt_4.2_v1", "pt_4.4_v1"],
    },
    "pt_4.1_v2": {
        "doc": "Outpatient PT Coverage Policy",
        "section": "4.1 Overview",
        "version": "v2",
        "effective_date": "2026-03-01",
        "text": (
            "This policy governs coverage for outpatient physical therapy "
            "services delivered as part of a single episode of care. See "
            "Section 4.2 for visit limits and Section 4.4 for prior "
            "authorization requirements."
        ),
        "refs": ["pt_4.2_v2", "pt_4.4_v2"],
    },
    "pt_4.2_v1": {
        "doc": "Outpatient PT Coverage Policy",
        "section": "4.2 Visit Limits",
        "version": "v1",
        "effective_date": "2025-01-01",
        "text": (
            "The plan covers outpatient physical therapy visits related to "
            "a single episode of care up to a maximum of 20 visits, "
            "provided that continued medical necessity is documented at "
            "each reassessment interval. This visit cap applies per "
            "episode of care. Visits beyond this threshold require prior "
            "authorization per Section 4.4."
        ),
        "refs": ["pt_4.4_v1"],
    },
    "pt_4.2_v2": {
        "doc": "Outpatient PT Coverage Policy",
        "section": "4.2 Visit Limits",
        "version": "v2",
        "effective_date": "2026-03-01",
        "text": (
            "The plan covers outpatient physical therapy visits related to "
            "a single episode of care up to a maximum of 12 visits, "
            "provided that continued medical necessity is documented at "
            "each reassessment interval. This visit cap applies per "
            "episode of care. Visits beyond this threshold require prior "
            "authorization per Section 4.4."
        ),
        "refs": ["pt_4.4_v2"],
    },
    "pt_4.3_v1": {
        "doc": "Outpatient PT Coverage Policy",
        "section": "4.3 Reimbursement Rate",
        "version": "v1",
        "effective_date": "2025-01-01",
        "text": (
            "Each covered visit is reimbursed at the contracted per-visit "
            "rate on file for the treating provider."
        ),
        "refs": [],
    },
    "pt_4.3_v2": {
        "doc": "Outpatient PT Coverage Policy",
        "section": "4.3 Reimbursement Rate",
        "version": "v2",
        "effective_date": "2026-03-01",
        "text": (
            "Each covered visit is reimbursed at the contracted per-visit "
            "rate on file for the treating provider. This rate is "
            "unchanged from the prior policy version."
        ),
        "refs": [],
    },
    "pt_4.4_v1": {
        "doc": "Outpatient PT Coverage Policy",
        "section": "4.4 Prior Authorization Requirements",
        "version": "v1",
        "effective_date": "2025-01-01",
        "text": (
            "Prior authorization is required once a member's episode of "
            "care exceeds the visit limit defined in Section 4.2 (20 "
            "visits). Requests must include the treating provider's plan "
            "of care and evidence of continued medical necessity."
        ),
        "refs": ["pt_4.2_v1"],
    },
    "pt_4.4_v2": {
        "doc": "Outpatient PT Coverage Policy",
        "section": "4.4 Prior Authorization Requirements",
        "version": "v2",
        "effective_date": "2026-03-01",
        "text": (
            "Prior authorization is required once a member's episode of "
            "care exceeds the visit limit defined in Section 4.2 (12 "
            "visits). Requests must include the treating provider's plan "
            "of care, evidence of continued medical necessity, and as of "
            "this version, a physician attestation for any extension "
            "beyond 16 total visits."
        ),
        "refs": ["pt_4.2_v2"],
    },
    # Document 2: Diagnostic Imaging Prior-Authorization Policy
    "img_2.1_v1": {
        "doc": "Diagnostic Imaging Prior-Authorization Policy",
        "section": "2.1 Overview",
        "version": "v1",
        "effective_date": "2025-01-01",
        "text": (
            "This policy governs prior-authorization thresholds and "
            "reimbursement terms for outpatient diagnostic imaging "
            "services. See Section 2.2 for the authorization threshold "
            "and Section 2.3 for reimbursement terms."
        ),
        "refs": ["img_2.2_v1", "img_2.3_v1"],
    },
    "img_2.1_v2": {
        "doc": "Diagnostic Imaging Prior-Authorization Policy",
        "section": "2.1 Overview",
        "version": "v2",
        "effective_date": "2026-03-01",
        "text": (
            "This policy governs prior-authorization thresholds and "
            "reimbursement terms for outpatient diagnostic imaging "
            "services. See Section 2.2 for the authorization threshold "
            "and Section 2.3 for reimbursement terms."
        ),
        "refs": ["img_2.2_v2", "img_2.3_v2"],
    },
    "img_2.2_v1": {
        "doc": "Diagnostic Imaging Prior-Authorization Policy",
        "section": "2.2 Prior-Authorization Threshold",
        "version": "v1",
        "effective_date": "2025-01-01",
        "text": (
            "Prior authorization is required for any outpatient diagnostic "
            "imaging service with a contracted cost exceeding $1,500."
        ),
        "refs": [],
    },
    "img_2.2_v2": {
        "doc": "Diagnostic Imaging Prior-Authorization Policy",
        "section": "2.2 Prior-Authorization Threshold",
        "version": "v2",
        "effective_date": "2026-03-01",
        "text": (
            "Prior authorization is required for any outpatient diagnostic "
            "imaging service with a contracted cost exceeding $800."
        ),
        "refs": [],
    },
    "img_2.3_v1": {
        "doc": "Diagnostic Imaging Prior-Authorization Policy",
        "section": "2.3 Reimbursement Terms",
        "version": "v1",
        "effective_date": "2025-01-01",
        "text": (
            "Out-of-network diagnostic imaging is reimbursed at 100% of "
            "the contracted in-network rate on file."
        ),
        "refs": [],
    },
    "img_2.3_v2": {
        "doc": "Diagnostic Imaging Prior-Authorization Policy",
        "section": "2.3 Reimbursement Terms",
        "version": "v2",
        "effective_date": "2026-03-01",
        "text": (
            "Out-of-network diagnostic imaging is reimbursed at 90% of "
            "the contracted in-network rate on file."
        ),
        "refs": [],
    },
    # Document 3: Utilization Management Program Overview (hub doc -
   
    "um_1.1_v1": {
        "doc": "Utilization Management Program Overview",
        "section": "1.1 Program Scope",
        "version": "v1",
        "effective_date": "2025-01-01",
        "text": (
            "The Utilization Management Program applies prior-authorization "
            "and visit/threshold controls across service categories. For "
            "physical therapy visit limits and prior authorization, see "
            "Section 4.2 and Section 4.4 of the Outpatient PT Coverage "
            "Policy. For diagnostic imaging authorization thresholds, see "
            "Section 2.2 of the Diagnostic Imaging Prior-Authorization "
            "Policy."
        ),
        "refs": ["pt_4.2_v1", "pt_4.4_v1", "img_2.2_v1"],
    },
    "um_1.1_v2": {
        "doc": "Utilization Management Program Overview",
        "section": "1.1 Program Scope",
        "version": "v2",
        "effective_date": "2026-03-01",
        "text": (
            "The Utilization Management Program applies prior-authorization "
            "and visit/threshold controls across service categories. For "
            "physical therapy visit limits and prior authorization, see "
            "Section 4.2 and Section 4.4 of the Outpatient PT Coverage "
            "Policy. For diagnostic imaging authorization thresholds, see "
            "Section 2.2 of the Diagnostic Imaging Prior-Authorization "
            "Policy."
        ),
        "refs": ["pt_4.2_v2", "pt_4.4_v2", "img_2.2_v2"],
    },
}


def get_chunk(chunk_id: str) -> dict:
    return CORPUS[chunk_id]


def all_chunks() -> dict:
    return CORPUS


def changed_pairs():
    """
    Returns (v1_id, v2_id) pairs for every section that has both a v1 and
    v2 revision - i.e. every candidate "policy change" in the corpus.
    """
    pairs = []
    seen = set()
    for chunk_id, chunk in CORPUS.items():
        if chunk["version"] != "v1":
            continue
        key = (chunk["doc"], chunk["section"])
        if key in seen:
            continue
        seen.add(key)
        v2_id = chunk_id.replace("_v1", "_v2")
        if v2_id in CORPUS and CORPUS[chunk_id]["text"] != CORPUS[v2_id]["text"]:
            pairs.append((chunk_id, v2_id))
    return pairs
