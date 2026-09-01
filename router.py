import re

from knowledge_graph import KnowledgeGraph
from vector_search import VectorStore

_MULTI_HOP_MARKERS = [
    "affect", "impact on", "downstream", "related to", "because of",
    "as a result of", "in turn", "consequently",
]
_COMPLEX_MARKERS = [
    "all changes", "all policies", "summarize all", "across all",
    "every change", "comprehensive",
]

def classify_query(query: str) -> str:
    q = query.lower()
    if any(marker in q for marker in _COMPLEX_MARKERS):
        return "COMPLEX"
    if any(marker in q for marker in _MULTI_HOP_MARKERS):
        return "MULTI_HOP"
      topic_terms = ["visit cap", "prior auth", "reimbursement", "imaging",
                   "threshold"]
    hits = sum(1 for t in topic_terms if t in q)
    if hits >= 2:
        return "MULTI_HOP"
    return "SIMPLE"


class AdaptiveRouter:
    def __init__(self):
        self.vector_store = VectorStore()
        self.graph = KnowledgeGraph()

    def route(self, query: str, top_k: int = 3) -> dict:
        tier = classify_query(query)

        if tier == "SIMPLE":
            hits = self.vector_store.search(query, top_k=1)
            chunk_ids = [cid for cid, _ in hits]
            return {"tier": tier, "chunk_ids": chunk_ids, "hops_used": 0}

        if tier == "MULTI_HOP":
            hits = self.vector_store.search(query, top_k=2)
            seed_ids = [cid for cid, _ in hits]
            hop_results = self.graph.multi_hop(seed_ids, hops=1)
            hop_ids = [cid for cid, _, _ in hop_results]
            return {
                "tier": tier,
                "chunk_ids": seed_ids + hop_ids,
                "hops_used": 1,
                "seed_ids": seed_ids,
            }
        hits = self.vector_store.search(query, top_k=top_k)
        seed_ids = [cid for cid, _ in hits]
        hop_results = self.graph.multi_hop(seed_ids, hops=2)
        hop_ids = [cid for cid, _, _ in hop_results]
        return {
            "tier": tier,
            "chunk_ids": list(dict.fromkeys(seed_ids + hop_ids)),
            "hops_used": 2,
            "seed_ids": seed_ids,
        }
