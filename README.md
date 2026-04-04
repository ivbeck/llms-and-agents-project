# Groq + Tavily Multi-Agent RAG QA System (Advanced Toggleable Version)

A complete **web RAG / QA multi-agent system** with a strong baseline and seven optional advanced add-ons.

This version is designed for **architecture comparison experiments**.

## Features

### Baseline
- Groq LLM for generation using `llama-3.3-70b-versatile`
- Tavily web search for live retrieval
- chunking over returned page text
- answer writer + critic

### Optional add-ons (all enabled by default)
1. **Hybrid Retrieval (BM25 + Embeddings)**
2. **Cross-Encoder Reranking**
3. **Query Decomposition (Multi-Hop)**
4. **Iterative Retrieval (ReAct-style search loop)**
5. **Self-RAG / Reflection Loop**
6. **Evidence Filtering Agent**
7. **HyDE (Hypothetical Document Embeddings)**

The key design goal is:
- you can run a **simple baseline**
- or enable/disable each technique individually
- so you can compare architectures for your report

## 1. Project structure

```text
groq_tavily_multiagent_rag_v2/
├── README.md
├── requirements.txt
├── .env.example
├── cli.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── orchestrator.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── answer_writer.py
│   │   ├── critic.py
│   │   ├── evidence_filter.py
│   │   ├── hyde.py
│   │   ├── query_planner.py
│   │   └── researcher.py
│   ├── llm/
│   │   ├── __init__.py
│   │   └── groq_client.py
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── chunking.py
│   │   ├── dense.py
│   │   ├── hybrid.py
│   │   ├── rerank.py
│   │   ├── sparse.py
│   │   └── web_search.py
│   └── utils/
│       ├── __init__.py
│       ├── parsing.py
│       └── text.py
└── tests/
    └── __init__.py
```

## 2. Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Fill in `.env`:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## 3. Important notes

### Local retrieval models
This project uses local Hugging Face models for advanced retrieval:
- embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- cross-encoder reranker: `cross-encoder/ms-marco-MiniLM-L-6-v2`

These will download on first run.

### Why this is useful
This gives you a clean experimental setup:
- Groq for the main generative LLM
- local open-weight retrieval/reranking models
- easy toggles for ablations

## 4. Run the system

### Default run (all advanced features ON)

```bash
python cli.py "What is BM25 and why is it useful in RAG?"
```

### Save full output as JSON

```bash
python cli.py "How does MCP differ from function calling?" --json --save result.json
```

### Run the pure baseline

```bash
python cli.py "What is BM25?" --baseline
```

### Disable specific features

```bash
python cli.py "What is HyDE in RAG?" \
  --disable-hybrid-retrieval \
  --disable-cross-encoder-reranking
```

## 5. Feature toggles

All optional add-ons default to **True**.

| Feature | Env key | CLI disable flag | Default |
|---|---|---|---|
| Hybrid Retrieval | `ENABLE_HYBRID_RETRIEVAL` | `--disable-hybrid-retrieval` | True |
| Cross-Encoder Reranking | `ENABLE_CROSS_ENCODER_RERANKING` | `--disable-cross-encoder-reranking` | True |
| Query Decomposition | `ENABLE_QUERY_DECOMPOSITION` | `--disable-query-decomposition` | True |
| Iterative Retrieval | `ENABLE_ITERATIVE_RETRIEVAL` | `--disable-iterative-retrieval` | True |
| Self-RAG | `ENABLE_SELF_RAG` | `--disable-self-rag` | True |
| Evidence Filtering | `ENABLE_EVIDENCE_FILTERING` | `--disable-evidence-filtering` | True |
| HyDE | `ENABLE_HYDE` | `--disable-hyde` | True |

`--baseline` turns all seven add-ons off in one step.

## 6. How the pipeline works

### Baseline mode
```text
Question
-> Tavily search
-> chunking
-> simple lexical chunk scoring
-> answer writer
-> critic
```

### Full advanced mode
```text
Question
-> Query Decomposition
-> HyDE pseudo-document generation
-> Tavily searches across iterations
-> chunking
-> Hybrid Retrieval (BM25 + embeddings)
-> Cross-Encoder reranking
-> Evidence Filtering Agent
-> Answer Writer
-> Self-RAG Critic Loop
-> Final answer
```

## 7. Recommended experiments for your report

1. **Baseline**
2. **+ Query Decomposition**
3. **+ Hybrid Retrieval**
4. **+ Cross-Encoder Reranking**
5. **+ Evidence Filtering**
6. **+ Self-RAG**
7. **+ Iterative Retrieval**
8. **+ HyDE**
9. **Full system**

Useful metrics:
- answer relevance
- groundedness
- context relevance
- latency
- number of sources
- token / API cost

## 8. CLI examples for ablations

### Only Query Decomposition
```bash
python cli.py "What is BM25?" \
  --disable-hybrid-retrieval \
  --disable-cross-encoder-reranking \
  --disable-iterative-retrieval \
  --disable-self-rag \
  --disable-evidence-filtering \
  --disable-hyde
```

### Only HyDE + Dense/Hybrid Retrieval
```bash
python cli.py "What is BM25?" \
  --disable-cross-encoder-reranking \
  --disable-query-decomposition \
  --disable-iterative-retrieval \
  --disable-self-rag \
  --disable-evidence-filtering
```

### Everything except Self-RAG
```bash
python cli.py "What is BM25?" --disable-self-rag
```

## 9. Suggested next extensions
- trustworthiness ranking by domain class
- timeliness filtering
- citation-at-sentence level
- benchmark runner for HotpotQA / NQ / CRAG-style tasks
- LangSmith logging and trace analysis
