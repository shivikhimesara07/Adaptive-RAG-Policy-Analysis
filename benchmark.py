import time

from agentic_loop import run_agentic_synthesis
from router import AdaptiveRouter, classify_query

TEST_QUERIES = [
    #  single-fact lookups
    "What is the maximum number of PT visits allowed per episode of care?",
    "What is the diagnostic imaging prior-authorization dollar threshold?",
    "What percentage rate is used for out-of-network imaging reimbursement?",
    "What is the reimbursement rate for physical therapy visits?",
    "What is the physician attestation requirement in the PT policy?",
    "What is the effective date of the imaging reimbursement policy?",
    # relationship questions between two clauses (multi-hop)
    "How does the change in the PT visit maximum affect prior authorization requirements?",
    "How does the imaging authorization threshold relate to the utilization management program?",
    "How does the PT visit limit affect the physician attestation requirement?",
    "How does the reimbursement rate change relate to out-of-network imaging claims?",
    "How does the visit limit change affect the reimbursement rate section?",
    # cross-document synthesis
    "summarize all changes across all utilization management policies and quantify their financial impact.",
    "Summarize every policy change and its downstream financial impact across all documents.",
]

N_REPEATS = 20

def naive_full_pipeline(router: AdaptiveRouter, query: str) -> dict:
    hits = router.vector_store.search(query, top_k=3)
    seed_ids = [cid for cid, _ in hits]
    hop_results = router.graph.multi_hop(seed_ids, hops=2)
    hop_ids = [cid for cid, _, _ in hop_results]
    chunk_ids = list(dict.fromkeys(seed_ids + hop_ids))
    changes = run_agentic_synthesis(chunk_ids)
    return {"chunk_ids": chunk_ids, "changes": changes}


def adaptive_full_pipeline(router: AdaptiveRouter, query: str) -> dict:
    result = router.route(query)
    if result["tier"] == "COMPLEX":
        result["changes"] = run_agentic_synthesis(result["chunk_ids"])
    else:
        result["changes"] = []
    return result


def time_call(fn, n=N_REPEATS):
    start = time.perf_counter()
    for _ in range(n):
        result = fn()
    elapsed_ms = (time.perf_counter() - start) / n * 1000
    return elapsed_ms, result

def run_benchmark():
    router = AdaptiveRouter()
    rows = []
    for query in TEST_QUERIES:
        tier = classify_query(query)
        adaptive_ms, adaptive_result = time_call(lambda: adaptive_full_pipeline(router, query))
        naive_ms, naive_result = time_call(lambda: naive_full_pipeline(router, query))
        rows.append({
            "query": query,
            "tier": tier,
            "adaptive_ms": adaptive_ms,
            "adaptive_chunks": len(adaptive_result["chunk_ids"]),
            "naive_ms": naive_ms,
            "naive_chunks": len(naive_result["chunk_ids"]),
        })
    return rows

def summarize(rows):
    by_tier = {}
    for r in rows:
        by_tier.setdefault(r["tier"], []).append(r)

    print(f"{'Tier':<10} {'n':>3} {'Adaptive ms':>12} {'Naive ms':>10} {'Time saved':>11} "
          f"{'Adapt. chunks':>14} {'Naive chunks':>13} {'Chunks saved':>13}")

    total_adaptive_ms = total_naive_ms = 0.0
    total_adaptive_chunks = total_naive_chunks = 0

    for tier in ("SIMPLE", "MULTI_HOP", "COMPLEX"):
        group = by_tier.get(tier, [])
        if not group:
            continue
        n = len(group)
        avg_a_ms= sum(r["adaptive_ms"] for r in group) / n
        avg_n_ms =sum(r["naive_ms"] for r in group) / n
        avg_a_chunks = sum(r["adaptive_chunks"] for r in group) / n
        avg_n_chunks = sum(r["naive_chunks"] for r in group) / n
        time_saved = 100 * (1 - avg_a_ms / avg_n_ms) if avg_n_ms else 0
        chunks_saved = 100 * (1 - avg_a_chunks / avg_n_chunks) if avg_n_chunks else 0

        print(f"{tier:<10} {n:>3} {avg_a_ms:>12.4f} {avg_n_ms:>10.4f} {time_saved:>10.1f}% "
              f"{avg_a_chunks:>14.1f} {avg_n_chunks:>13.1f} {chunks_saved:>12.1f}%")

        total_adaptive_ms += sum(r["adaptive_ms"] for r in group)
        total_naive_ms += sum(r["naive_ms"] for r in group)
        total_adaptive_chunks += sum(r["adaptive_chunks"] for r in group)
        total_naive_chunks += sum(r["naive_chunks"] for r in group)

    n_total = len(rows)
    overall_time_saved = 100 * (1 - total_adaptive_ms / total_naive_ms) if total_naive_ms else 0
    overall_chunks_saved = 100 * (1 - total_adaptive_chunks / total_naive_chunks) if total_naive_chunks else 0
    print(f"\nOverall across {n_total} queries ({N_REPEATS} timed repetitions each):")
    print(f"  Adaptive avg latency: {total_adaptive_ms/n_total:.4f} ms/query")
    print(f"  Naive avg latency:    {total_naive_ms/n_total:.4f} ms/query")
    print(f"  End-to-end latency reduction: {overall_time_saved:.1f}%")
    print(f"  Retrieval volume reduction:   {overall_chunks_saved:.1f}%")

if __name__ == "__main__":
    rows = run_benchmark()
    summarize(rows)
