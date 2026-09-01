"""
Knowledge graph over policy clauses.

Nodes = chunks (doc, section, version). Edges are built from two real
relationships already present in the corpus data, not invented for the
graph:
  - "references": chunk A's text explicitly cites chunk B (corpus.refs)
  - "supersedes": chunk A (v2) is the next version of chunk B (v1) for the
    same (doc, section)

Multi-hop retrieval means: start from the vector-search hit(s), then walk
these edges N hops out to pull in clauses that are related but wouldn't
themselves score highly against the raw query text (e.g. a query about
"visit cap change" surfaces Section 4.2 directly via vector search, then
a graph hop surfaces Section 4.4, which depends on 4.2 but never uses the
word "cap").
"""

from collections import defaultdict

from corpus import all_chunks


class KnowledgeGraph:
    def __init__(self, chunks: dict = None):
        self.chunks = chunks or all_chunks()
        self.edges = defaultdict(list)  # chunk_id -> [(neighbor_id, relation)]
        self._build()

    def _build(self):
        for chunk_id, chunk in self.chunks.items():
            for ref_id in chunk.get("refs", []):
                if ref_id in self.chunks:
                    self.edges[chunk_id].append((ref_id, "references"))
                    self.edges[ref_id].append((chunk_id, "referenced_by"))

            if chunk["version"] == "v2":
                v1_id = chunk_id.replace("_v2", "_v1")
                if v1_id in self.chunks:
                    self.edges[chunk_id].append((v1_id, "supersedes"))
                    self.edges[v1_id].append((chunk_id, "superseded_by"))

    def neighbors(self, chunk_id: str) -> list:
        return self.edges.get(chunk_id, [])

    def multi_hop(self, seed_ids: list, hops: int = 2) -> list:
        """
        Breadth-first traversal from seed_ids out to `hops` edges.
        Returns [(chunk_id, hop_distance, relation_path)] for every node
        reached, excluding the seeds themselves at distance 0.
        """
        visited = {cid: 0 for cid in seed_ids}
        frontier = [(cid, []) for cid in seed_ids]
        results = []

        for hop in range(1, hops + 1):
            next_frontier = []
            for chunk_id, path in frontier:
                for neighbor_id, relation in self.neighbors(chunk_id):
                    if neighbor_id in visited:
                        continue
                    visited[neighbor_id] = hop
                    new_path = path + [relation]
                    results.append((neighbor_id, hop, new_path))
                    next_frontier.append((neighbor_id, new_path))
            frontier = next_frontier
            if not frontier:
                break

        return results
