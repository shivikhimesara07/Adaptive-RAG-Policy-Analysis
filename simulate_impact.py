"""
Applies an extracted policy change to a synthetic claims population and
computes the financial/operational impact - the "so what" number a
payment-integrity team would want before a policy change goes live.

Three change types are handled, matching the three patterns the
extraction layer recognizes:
  - visit_cap:        PT visit-cap tightening/loosening
  - dollar_threshold:  prior-authorization dollar threshold changes
  - percentage_rate:   reimbursement percentage changes

Each returns a common shape (total items, items affected, dollar delta)
so a caller can aggregate across change types without special-casing.
"""


def simulate_visit_cap_change(episodes: list, old_cap: int, new_cap: int) -> dict:
    total_old_paid = total_new_paid = 0.0
    affected = []

    for ep in episodes:
        visits_used, rate = ep["visits_used"], ep["rate_per_visit"]
        paid_old = min(visits_used, old_cap) * rate
        paid_new = min(visits_used, new_cap) * rate
        total_old_paid += paid_old
        total_new_paid += paid_new
        if min(visits_used, old_cap) != min(visits_used, new_cap):
            affected.append({
                "item_id": ep["episode_id"],
                "detail": f"used {visits_used} visits",
                "dollar_delta": round(paid_new - paid_old, 2),
            })

    return _summarize("visit_cap", len(episodes), affected, total_old_paid, total_new_paid)


def simulate_dollar_threshold_change(claims: list, old_threshold: float, new_threshold: float) -> dict:
    """
    A lower threshold means more claims newly require prior authorization.
    Impact metric: total contracted-cost dollars that move from
    "no auth required" to "auth required" - i.e. dollars now subject to
    utilization review that weren't before.
    """
    newly_requires_auth = []
    for c in claims:
        cost = c["contracted_cost"]
        required_before = cost > old_threshold
        required_after = cost > new_threshold
        if required_after and not required_before:
            newly_requires_auth.append({
                "item_id": c["claim_id"],
                "detail": f"{c['procedure']}, ${cost:,.2f}",
                "dollar_delta": round(cost, 2),
            })

    total_old = sum(c["contracted_cost"] for c in claims if c["contracted_cost"] > old_threshold)
    total_new = sum(c["contracted_cost"] for c in claims if c["contracted_cost"] > new_threshold)

    return _summarize("dollar_threshold", len(claims), newly_requires_auth, total_old, total_new,
                       delta_label="dollars newly subject to prior authorization")


def simulate_percentage_rate_change(claims: list, old_pct: float, new_pct: float) -> dict:
    """
    Applies to out-of-network claims only (per the imaging policy's
    reimbursement-terms clause). Impact metric: change in total
    reimbursement paid out.
    """
    oon_claims = [c for c in claims if c["network_status"] == "out_of_network"]
    affected = []
    total_old_paid = total_new_paid = 0.0

    for c in oon_claims:
        cost = c["contracted_cost"]
        paid_old = cost * (old_pct / 100)
        paid_new = cost * (new_pct / 100)
        total_old_paid += paid_old
        total_new_paid += paid_new
        if paid_old != paid_new:
            affected.append({
                "item_id": c["claim_id"],
                "detail": f"{c['procedure']} (out-of-network), ${cost:,.2f}",
                "dollar_delta": round(paid_new - paid_old, 2),
            })

    return _summarize("percentage_rate", len(oon_claims), affected, total_old_paid, total_new_paid)


def _summarize(change_type, total_items, affected, total_old, total_new, delta_label="net financial impact"):
    return {
        "change_type": change_type,
        "total_items": total_items,
        "items_affected": len(affected),
        "pct_affected": round(100 * len(affected) / total_items, 1) if total_items else 0.0,
        "total_old": round(total_old, 2),
        "total_new": round(total_new, 2),
        "total_delta": round(total_new - total_old, 2),
        "delta_label": delta_label,
        "affected_detail": affected,
    }
