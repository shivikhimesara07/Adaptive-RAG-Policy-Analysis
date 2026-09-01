# Adaptive-Multi-Strategy-RAG-for-Policy-Impact-Analysis

# Policy Impact Simulator

A prototype for analyzing healthcare policy changes and estimating their financial impact using an adaptive retrieval pipeline.

### How it works

* **Simple queries** → TF-IDF vector search
* **Multi-hop queries** → Vector search + knowledge graph
* **Complex queries** → Retrieval + agentic extraction + grounding + impact simulation
* **Grounding critic** → Verifies extracted values and quotes; retries or abstains when needed.
* **Impact simulator** → Estimates the effect of visit-cap, authorization-threshold, and reimbursement-rate changes.

The policy corpus and claims data are **fully synthetic** and contain no PHI.

### Run

```bash
pip install -r requirements.txt
python main.py
```

Gemini is optional here
Set `GEMINI_API_KEY` to enable Gemini-based extraction; otherwise the rule-based fallback is used.

### Benchmark

```bash
python benchmark.py
```

Compares adaptive routing against a pipeline that always runs the most expensive retrieval and synthesis path.
