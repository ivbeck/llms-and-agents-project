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
7. Evidence sufficiency agent
8. HyDE (Hypothetical Document Embeddings)

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

If you are new to Python projects, follow these steps exactly.

### 1) Create and activate a virtual environment

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell [enjoy the pain :)]

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If activation worked, your shell prompt usually starts with `(.venv)`.

### 2) Install the project (from `pyproject.toml`)

Install runtime dependencies and CLI scripts (`rag-cli`, `rag-tui`, `rag-bench`, `rag-score`):

```bash
pip install -e .
```

If you also want dev tools (pytest/ruff/mypy):

```bash
pip install -e ".[dev]"
```

### 3) Create your local env file

```bash
cp .env.dist .env
```

Windows PowerShell:

```powershell
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
-> adaptive Tavily search depth (`basic` or `advanced`)
-> HyDE pseudo-document generation
-> Tavily searches across iterations
-> chunking
-> Hybrid Retrieval
-> Cross-Encoder Reranking
-> Evidence Filtering Agent
-> Evidence Sufficiency Agent
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
| Evidence Sufficiency | `ENABLE_EVIDENCE_SUFFICIENCY` | `--disable-evidence-sufficiency` | True |
| HyDE | `ENABLE_HYDE` | `--disable-hyde` | True |

`--baseline` turns all add-ons off.

Evidence sufficiency can trigger extra pre-answer web-search retries when the filtered evidence is not enough to answer the question. Limit this loop with `MAX_EVIDENCE_RETRIES` or `--max-evidence-retries` (default: 3).

Query decomposition generates up to `MAX_QUERY_DECOMPOSITION_QUERIES` focused search queries (default: 4). The planner can return fewer queries for simple questions.

The query planner also chooses Tavily `search_depth` (`basic` or `advanced`) for the initial search and critic-driven follow-up searches. Evidence sufficiency retries always use `advanced` search. If planning is disabled or parsing fails, the system falls back to `TAVILY_DEFAULT_SEARCH_DEPTH` (default: `advanced`).

## Suggested Report Metrics

- answer relevance
- context relevance
- groundedness / faithfulness
- latency
- source count
- evidence count
- token and API cost, if provider usage metadata is available

## Data layout

The evaluation pipeline uses the project's `data/` directory as its base path:

```text
data/
  benchmarks/   ← question files from scripts/download_benchmarks.py
  predictions/  ← outputs of run/eval.py
  scores/       ← outputs of run/score.py and run/aggregate.py
```

CLI scripts default to the right subdir for their stage and accept either a
plain filename (resolved against the convention) or an explicit path.

## Benchmarks

Download SimpleQA, PopQA, TriviaQA, and BrowseComp into JSONL files matching
the question-file schema used below:

```bash
python scripts/download_benchmarks.py
python scripts/download_benchmarks.py --datasets browsecomp --sample 50
```

Sources:

- **SimpleQA** — OpenAI public CSV (no auth)
- **PopQA** — HuggingFace `akariasai/PopQA`
- **TriviaQA** — HuggingFace `trivia_qa` (`rc.nocontext` validation split — has gold)
- **BrowseComp** — OpenAI public CSV, XOR-encrypted with per-row canary; the script
  decrypts on download. If OpenAI rotates the URL or scheme, sync the loader
  against `https://github.com/openai/simple-evals/blob/main/browsecomp_eval.py`.

`--sample N` randomly samples N rows per dataset (seeded for reproducibility) — useful
for the BrowseComp subset, since running the full 1.2k questions through a multi-agent
pipeline is expensive.

## Evaluation Quick Start (Required First Steps)

Before running any benchmark/evaluation commands, do this once:

```bash
./scripts/setup_folder_structure.sh
```

This creates the required `data/` folder layout and downloads benchmark files.

Then check available evaluation CLI options:

```bash
rag-bench -h
```

If this command is not found, your environment is usually not active yet. Run:

```bash
source .venv/bin/activate
```

Then try `rag-bench -h` again.

## Scoring (LLM-as-Judge + RAGAS)

Generation and scoring are decoupled. `eval.py` produces `predictions.jsonl`;
`score.py` consumes it and writes `scored.jsonl` with judge and RAGAS metrics.
`aggregate.py` produces a per-setup × dataset summary table.

### Question file format with gold answers

For SimpleQA / PopQA / TriviaQA / BrowseComp, include a `gold` field (string or
list of acceptable answers / aliases) and a `dataset` tag:

```jsonl
{"id": "sq_1", "question": "Who discovered radium?", "gold": ["Marie Curie", "Curie"], "dataset": "simpleqa"}
{"id": "tq_1", "question": "...", "gold": ["..."], "dataset": "triviaqa"}
```

### Run

Bare filenames are resolved under the right `data/` subdir at each stage:

```bash
# reads data/benchmarks/simpleqa.jsonl, writes data/predictions/simpleqa_full.jsonl
python run/eval.py simpleqa.jsonl --setup full

# reads data/predictions/simpleqa_full.jsonl, writes data/scores/simpleqa_full.jsonl
python run/score.py simpleqa_full.jsonl

# reads data/scores/*.jsonl
python run/aggregate.py simpleqa_full.jsonl --csv data/scores/summary.csv
```

You can still pass an explicit relative or absolute path to override the default
location.

Score a subset of metrics or use a different judge model:

```bash
python run/score.py simpleqa_full.jsonl --metrics correctness,faithfulness
python run/score.py simpleqa_full.jsonl --judge-model anthropic/claude-haiku-4-5
```

Score is incremental: re-running with additional metrics only fills in what is
missing per row, so you can extend the metric set without redoing prior work.

### Metrics

LLM-as-judge (rationale-first):

- `correctness` — answer vs gold, scored **-1 wrong, 0 no-answer, 1 correct (paraphrase ok)**
- `answer_relevance` — is the answer on-topic, regardless of correctness (0/1)
- `citation_accuracy` — for each `[Ei]` cite in the answer, does evidence Ei support the claim

RAGAS (per single-turn sample):

- `faithfulness` — answer grounded in retrieved contexts
- `ragas_answer_relevancy` — RAGAS-style answer relevance via embeddings
- `context_precision` — relevant contexts ranked high (needs gold)
- `context_recall` — gold facts present in contexts (needs gold)
### Human Evaluation

In addition to the automated judge pipeline, this repo includes a small manual
audit of the judge outputs in `data/human_eval/`.

- 8 predictions from the `full` setup were sampled across SimpleQA, PopQA, and
  TriviaQA
- the sample is stratified by judge correctness class: correct (`+1`), rejected
  (`0`), and wrong (`-1`)
- each rating sheet contains the original prediction JSON, the LLM-judge scores,
  and a checklist for human ratings

Human raters score the same three judge-facing metrics:

- `correctness` — `-1` wrong, `0` rejected / no-answer, `1` correct
- `answer_relevance` — `0` not on-topic, `1` on-topic
- `citation_accuracy` — mean support rate across cited evidence items

Current alignment summary from `scripts/Human_Eval_Corr.py`:

| Metric | Pearson (r) | MAE | Exact Match % |
|---|---:|---:|---:|
| Correctness | N/A (perfect agreement) | 0.0000 | 100.0 |
| Answer relevance | N/A (zero variance) | 0.0000 | 100.0 |
| Citation accuracy | 0.1651 | 0.3638 | 37.5 |

To reproduce the alignment summary:

```bash
python scripts/Human_Eval_Corr.py
```
The judge model is read from `JUDGE_MODEL` in `.env` (default `openai/gpt-4.1-mini`),
with temperature `JUDGE_TEMPERATURE` (default `0.0`). It is routed through OpenRouter,
so use the `provider/model` form (e.g. `anthropic/claude-haiku-4-5`,
`google/gemini-2.5-flash`). Use a different model than the generator
(`OPENROUTER_MODEL`) to limit self-preference bias. The CLI flag
`--judge-model` overrides the env var per run.
