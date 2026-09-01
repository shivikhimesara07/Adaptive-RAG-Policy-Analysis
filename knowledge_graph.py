from collections import defaultdict

from corpus import all_chunks

class KnowledgeGraph:
    def __init__(self, chunks: dict = None):
        self.chunks = chunks or all_chunks()
        self.edges = defaultdict(list)  # chunk_id = (neighbor_id, relation)
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
