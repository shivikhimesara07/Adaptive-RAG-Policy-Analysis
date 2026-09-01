import math
import re
from collections import Counter

from corpus import all_chunks

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list:
    return _TOKEN_RE.findall(text.lower())


class VectorStore:
    def __init__(self, chunks: dict = None):
        self.chunks = chunks or all_chunks()
        self.chunk_ids = list(self.chunks.keys())
    
        self._doc_tokens = {
            cid: _tokenize(f"{c['doc']} {c['section']} {c['text']} {c['text']}")
            for cid, c in self.chunks.items()
        }
        self._idf = self._build_idf()
        self._doc_vectors = {
            cid: self._tfidf_vector(toks) for cid, toks in self._doc_tokens.items()
        }

    def _build_idf(self) -> dict:
        n_docs = len(self._doc_tokens)
        df = Counter()
        for toks in self._doc_tokens.values():
            for term in set(toks):
                df[term] += 1
        return {
            term: math.log((1 + n_docs) / (1 + count)) + 1.0
            for term, count in df.items()
        }

    def _tfidf_vector(self, tokens: list) -> dict:
        tf = Counter(tokens)
        vec = {}
        for term, count in tf.items():
            idf = self._idf.get(term, 0.0)
            if idf > 0:
                vec[term] = count * idf
        return vec

    @staticmethod
    def _cosine(v1: dict, v2: dict) -> float:
        if not v1 or not v2:
            return 0.0
        shared = set(v1) & set(v2)
        dot = sum(v1[t] * v2[t] for t in shared)
        norm1 = math.sqrt(sum(x * x for x in v1.values()))
        norm2 = math.sqrt(sum(x * x for x in v2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def search(self, query: str, top_k: int = 3, version: str = None) -> list:
        q_vec = self._tfidf_vector(_tokenize(query))
        scored = []
        for cid in self.chunk_ids:
            if version and self.chunks[cid]["version"] != version:
                continue
            score = self._cosine(q_vec, self._doc_vectors[cid])
            if score > 0:
                scored.append((cid, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
