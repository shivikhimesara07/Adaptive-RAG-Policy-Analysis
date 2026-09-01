"""
Adaptive retrieval router.

Classifies each incoming query into one of three complexity tiers and
routes it to the matching retrieval strategy, in the spirit of
Adaptive-RAG (match retrieval effort to query complexity) rather than
always paying for the most expensive path:

  SIMPLE    - a single-fact lookup ("what is the visit cap in v2?").
              -> vector search only, top-1 chunk, no graph hop needed.

  MULTI_HOP - asks how one clause affects or relates to another
              ("how does the visit cap change affect prior auth?").
              -> vector search for the entry point(s), then a 2-hop
                 knowledge-graph traversal to pull in dependent clauses.

  COMPLEX   - asks for a comprehensive, cross-document synthesis
              ("summarize all changes across all UM policies and their
              financial impact").
              -> vector search + multi-hop over ALL matched entry points,
                 then handed to the agentic draft/critique/retry loop to
                 extract + verify + simulate each change found.

Classification is rule-based (keyword + structure heuristics), not an
LLM call - matches this repo's existing pattern of keeping the
control-flow layer deterministic and cheap, and reserving the LLM/agentic
budget for the step that actually needs it.
"""

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
    # A query naming two distinct topical nouns (e.g. "visit cap" and
    # "prior auth") without an explicit relational marker still likely
    # needs a hop - a lightweight heuristic rather than a hard rule.
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
            # 1 hop: enough to follow an explicit cross-reference from the
            # entry point to the clause it depends on. A hub document (like
            # the UM overview) legitimately IS the right entry point when a
            # query spans two topics it cross-references - but walking 2
            # full hops out from a hub in a small corpus pulls in nearly
            # everything, which defeats the point of a *targeted* hop.
            hop_results = self.graph.multi_hop(seed_ids, hops=1)
            hop_ids = [cid for cid, _, _ in hop_results]
            return {
                "tier": tier,
                "chunk_ids": seed_ids + hop_ids,
                "hops_used": 1,
                "seed_ids": seed_ids,
            }

        # COMPLEX
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
