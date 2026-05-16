# Human Evaluation Checklist — simpleqa_4105

Each rater reads this file, rates the single prediction shown in §6, and writes their decisions inline. Eight such files exist — one per sample. The (TriviaQA, wrong) cell is empty because the full run produced no wrong TriviaQA answer.

---

## 1. LLM-as-judge prompt (for reference)

> You are a grading judge for a question-answering system.
> Compare the candidate answer against the gold answer(s).
> Different formulations of the same fact must count as correct.
> Different facts, contradictions, or hedged non-answers must count as wrong.
> Return JSON only.

## 2. Metrics under evaluation

- **Correctness** — `-1` wrong · `0` rejected / no-answer · `+1` correct (paraphrases of the gold count as correct)
- **Answer relevance** — `0` not on-topic · `1` on-topic, regardless of correctness
- **Citation accuracy** — per `[Ei]` cite in the answer: `1` if that evidence `Ei` actually supports the cited claim, else `0`. The score for the prediction is the arithmetic mean across all citations.

## 3. Sampling design

Eight predictions from the **full** setup were sampled, stratified 3 datasets × 3 correctness classes (minus the empty TriviaQA-wrong cell). The cell marked ☒ below is the one represented by this file.

|              | correct (`+1`) | rejected (`0`) | wrong (`-1`) |
| ------------ | :------------: | :------------: | :----------: |
| **SimpleQA** |       ☐        |       ☒        |      ☐       |
| **PopQA** |       ☐        |       ☐        |      ☐       |
| **TriviaQA** |       ☐        |       ☐        |      ☐       |

## 4. Rating procedure

- [X] Read the **question** in §6 carefully — what is it actually asking for?
- [X] Read the **gold answer(s)** — these are the accepted answers including aliases.
- [X] Read the **candidate answer** — do not look at the judge's verdict yet.
- [X] Decide your own **correctness** score (`-1` / `0` / `+1`).
- [X] Decide your own **answer relevance** score (`0` / `1`).
- [X] For each `[Ei]` citation in the answer:
    - [X] Find evidence `Ei` in the `evidence` list.
    - [X] Decide whether that piece of evidence really supports the cited claim (`0` / `1`).
- [X] Compute the **citation accuracy** as the mean of those 0/1 decisions.
- [X] Compare each of your three scores against the LLM judge's scores in the JSON.

## 5. Your ratings

| field | value |
| --- | --- |
| dataset | simpleqa |
| question_id | simpleqa_4105 |
| LLM-judge correctness | 0 |
| LLM-judge answer_relevance | 1 |
| LLM-judge citation_accuracy | 1.000 |

**Human correctness**: `-1` ☐ &nbsp; `0` ☒ &nbsp; `+1` ☐ &nbsp; — short justification: He gave no answer because he couldn't find the information in the source.

**Human answer relevance**: `0` ☐ &nbsp; `1` ☒ &nbsp; — short justification: The agenda included information about fencing at the 1964 Summer Olympics.

**Human citation accuracy** — one row per `[Ei]` in the answer:

| cite | claim made in the answer | supports? (0/1) |
| --- | --- | :---: |
| E1 | show only the invidiual names, not the country | 0 |
| **mean** |  | 0 |

- [X] My correctness matches the LLM judge
- [X] My answer relevance matches the LLM judge
- [ ] My citation accuracy matches the LLM judge (within ±0.1)

Disagreement notes (if any): The judge claims that the source does not show the name of the country for the silver medallist. This is incorrect.

---

## 6. Prediction to rate

```json
{
  "question_id": "simpleqa_4105",
  "question": "What country won the silver medal in the men's team foil event at the 1964 Summer Olympics?",
  "gold": [
    "Poland"
  ],
  "dataset": "simpleqa",
  "setup": "full",
  "latency_seconds": 482.224,
  "answer": "The provided evidence does not explicitly state which country won the silver medal; the medalists table is cut off after listing the individual silver medalists’ names and before showing the country [E1]. The evidence only shows that the silver medalists were Zbigniew Skrudlik, Witold Woyda, Egon Franke, and Ryszard Parulski [E1].\n\n**Why these sources were relevant**\n- [E1] is the Wikipedia article for the men's team foil event at the 1964 Summer Olympics and includes the medalists table, but the portion containing the country name for the silver medal is truncated in the provided text.",
  "critic": {
    "is_grounded": true,
    "is_relevant": true,
    "needs_revision": false,
    "comment": "The answer correctly notes that the evidence truncates before showing the silver medalist country, and it accurately lists the four named silver medalists that do appear in the source. No unsupported factual claims are made."
  },
  "features": {
    "hybrid_retrieval": true,
    "cross_encoder_reranking": true,
    "query_decomposition": true,
    "iterative_retrieval": true,
    "self_rag": true,
    "evidence_filtering": true,
    "evidence_sufficiency": true,
    "hyde": true
  },
  "sources_count": 1,
  "evidence_count": 1,
  "evidence": [
    {
      "evidence_id": "E1",
      "url": "https://en.wikipedia.org/wiki/Fencing_at_the_1964_Summer_Olympics_%E2%80%93_Men%27s_team_foil",
      "title": "Fencing at the 1964 Summer Olympics – Men's team foil - Wikipedia",
      "text": "![](/static/images/icons/enwiki-25.svg) ![Wikipedia](/static/images/mobile/copyright/wikipedia-wordmark-en-25.svg) ![The Free Encyclopedia](/static/images/mobile/copyright/wikipedia-tagline-en-25.svg) ## Contents # Fencing at the 1964 Summer Olympics – Men's team foil | Men's team foil at the Games of the XVIII Olympiad | | | --- | --- | | Venue | [Waseda Memorial Hall](/wiki/Waseda_University \"Waseda University\") | | Dates | October 15 – 16 | | Competitors | 78 from 16 nations | | Medalists | | | | | | | | | --- | --- | --- | --- | | 1st place, gold medalist(s) | | [Viktor Zhdanovich](/wiki/V […truncated…]",
      "score_final": 4.686723232269287,
      "selected_reason": "only chunk covering the men's team foil event; its medalists table lists the silver-winning squad (Zbigniew Skrudlik, Witold Woyda, Egon Franke, Ryszard Parulski), all representing Poland"
    }
  ],
  "judge": {
    "correctness": {
      "rationale": "The candidate explicitly states that evidence is truncated and insufficient to identify the country, provides no country name or claim, and thus refuses to answer.",
      "score": 0
    },
    "answer_relevance": {
      "rationale": "The answer directly engages the exact query by analyzing the medal table for the 1964 men's team foil event, naming the listed silver medalists, and explaining why the country is missing from the evidence.",
      "score": 1
    },
    "citation_accuracy": {
      "checks": [
        {
          "evidence_id": "E1",
          "claim": "evidence is truncated and does not show the silver-medal country (only the four Polish fencers' names)",
          "supported": true,
          "rationale": "The provided evidence text ends mid-row exactly after the last silver-medalist's name and before any country flag or link, confirming the truncation described."
        }
      ],
      "accuracy": 1.0,
      "no_citations": false
    }
  },
  "ragas": {
    "faithfulness": 0.9,
    "answer_relevancy": 0.0,
    "context_precision": 0.9999999999,
    "context_recall": 0.0
  },
  "scoring": {
    "elapsed_seconds": 75.219
  }
}
```
