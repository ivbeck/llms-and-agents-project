# OpenRouter + Tavily Multi-Agent RAG QA System

A web-based RAG / QA system for comparing a simple baseline with optional
advanced retrieval and agent-style components.

The project is designed for architecture comparison experiments in a
"Question Answering Agents" university project.

## Features

### Baseline

- OpenRouter LLM for answer generation
- Tavily web search for live retrieval
- chunking over returned web content
- simple lexical chunk scoring
- answer writer + critic

### Optional Add-ons

All optional add-ons are enabled by default:

1. Hybrid retrieval with BM25 + embeddings
2. Cross-encoder reranking
3. Query decomposition
4. Iterative retrieval
5. Self-RAG / reflection loop
6. Evidence filtering agent
7. HyDE (Hypothetical Document Embeddings)

## Project Structure

```text
llms-and-agents-project/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.dist
├── cli.py
├── eval.py
├── src/
│   ├── config.py
│   ├── models.py
│   ├── orchestrator.py
│   ├── agents/
│   │   ├── answer_writer.py
│   │   ├── critic.py
│   │   ├── evidence_filter.py
│   │   ├── hyde.py
│   │   ├── query_planner.py
│   │   └── researcher.py
│   ├── llm/
│   │   └── openrouter_client.py
│   ├── retrieval/
│   │   ├── chunking.py
│   │   ├── dense.py
│   │   ├── hybrid.py
│   │   ├── rerank.py
│   │   ├── sparse.py
│   │   └── web_search.py
│   └── utils/
│       ├── parsing.py
│       └── text.py
└── tests/
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.dist .env
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.dist .env
```

Fill in `.env`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_TEMPERATURE=0.1
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

TAVILY_API_KEY=your_tavily_api_key_here
```

## Local Retrieval Models

The advanced retrieval setup uses local Hugging Face models:

- embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- cross-encoder reranker: `cross-encoder/ms-marco-MiniLM-L-6-v2`

These models download on first use.

## Run the System

Default run:

```bash
python cli.py "What is BM25 and why is it useful in RAG?"
```

Save full output as JSON:

```bash
python cli.py "How does MCP differ from function calling?" --json --save result.json
```

Run the pure baseline:

```bash
python cli.py "What is BM25?" --baseline
```

Disable specific features:

```bash
python cli.py "What is HyDE in RAG?" \
  --disable-hybrid-retrieval \
  --disable-cross-encoder-reranking
```

## Batch Evaluation

Create a JSONL file such as:

```jsonl
{"id": "q1", "question": "What is BM25?"}
{"id": "q2", "question": "How does HyDE improve retrieval?"}
```

Run an evaluation setup:

```bash
python eval.py questions.jsonl --setup baseline --output baseline_results.jsonl
python eval.py questions.jsonl --setup full --output full_results.jsonl
```

The output JSONL includes:

- question id
- setup name
- final answer
- critic result
- feature flags
- latency
- source count
- evidence count
- selected evidence metadata and reasons

## Pipeline

Baseline:

```text
Question
-> Tavily search
-> chunking
-> simple lexical chunk scoring
-> answer writer
-> critic
```

Full setup:

```text
Question
-> Query Decomposition
-> HyDE pseudo-document generation
-> Tavily searches across iterations
-> chunking
-> Hybrid Retrieval
-> Cross-Encoder Reranking
-> Evidence Filtering Agent
-> Answer Writer
-> Self-RAG Critic Loop
-> Final Answer
```

## Feature Toggles

| Feature | Env key | CLI disable flag | Default |
|---|---|---|---|
| Hybrid Retrieval | `ENABLE_HYBRID_RETRIEVAL` | `--disable-hybrid-retrieval` | True |
| Cross-Encoder Reranking | `ENABLE_CROSS_ENCODER_RERANKING` | `--disable-cross-encoder-reranking` | True |
| Query Decomposition | `ENABLE_QUERY_DECOMPOSITION` | `--disable-query-decomposition` | True |
| Iterative Retrieval | `ENABLE_ITERATIVE_RETRIEVAL` | `--disable-iterative-retrieval` | True |
| Self-RAG | `ENABLE_SELF_RAG` | `--disable-self-rag` | True |
| Evidence Filtering | `ENABLE_EVIDENCE_FILTERING` | `--disable-evidence-filtering` | True |
| HyDE | `ENABLE_HYDE` | `--disable-hyde` | True |

`--baseline` turns all seven add-ons off.

## Suggested Report Metrics

- answer relevance
- context relevance
- groundedness / faithfulness
- latency
- source count
- evidence count
- token and API cost, if provider usage metadata is available
