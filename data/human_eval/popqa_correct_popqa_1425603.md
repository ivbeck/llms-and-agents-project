# Human Evaluation Checklist — popqa_1425603

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
| **SimpleQA** |       ☐        |       ☐        |      ☐       |
| **PopQA** |       ☒        |       ☐        |      ☐       |
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
| dataset | popqa |
| question_id | popqa_1425603 |
| LLM-judge correctness | 1 |
| LLM-judge answer_relevance | 1 |
| LLM-judge citation_accuracy | 1.000 |

**Human correctness**: `-1` ☐ &nbsp; `0` ☐ &nbsp; `+1` ☒ &nbsp; — short justification: The Answer matches the Groundtruth.

**Human answer relevance**: `0` ☐ &nbsp; `1` ☒ &nbsp; — short justification: It directly responds to the question

**Human citation accuracy** — one row per `[Ei]` in the answer:

| cite | claim made in the answer | supports? (0/1) |
| --- | --- | :---: |
| E1 | Alfred the Great was the father of Edward the Elder | 1 |
| E2 | Alfred the Great was the father of Edward the Elder | 1 ||
| **mean** |  | 1 |

- [X] My correctness matches the LLM judge
- [X] My answer relevance matches the LLM judge
- [X] My citation accuracy matches the LLM judge (within ±0.1)

Disagreement notes (if any): _…_

---

## 6. Prediction to rate

```json
{
  "question_id": "popqa_1425603",
  "question": "Who is the father of Edward the Elder?",
  "gold": [
    "Alfred the Great",
    "King of Wessex Aelfred",
    "King of England Alfred",
    "Alfred the Wise",
    "King of England Aelfred",
    "King of England Alfred the Great",
    "Alfred the Great of Wessex",
    "Alfred",
    "Alfred King",
    "King Alfred",
    "Alfred den Store"
  ],
  "dataset": "popqa",
  "setup": "full",
  "latency_seconds": 279.285,
  "answer": "Alfred the Great was the father of Edward the Elder [E1][E2].\n\nWhy these sources were relevant:\n[E1] explicitly states that Edward the Elder became king upon the death of his father, Alfred the Great, and its title identifies Edward as Alfred’s son. [E2] explicitly describes Edward the Elder as the eldest son of Alfred the Great.",
  "critic": {
    "is_grounded": true,
    "is_relevant": true,
    "needs_revision": false,
    "comment": "Both E1 and E2 explicitly state that Alfred the Great was Edward the Elder's father, fully supporting the answer to the question."
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
  "sources_count": 3,
  "evidence_count": 3,
  "evidence": [
    {
      "evidence_id": "E1",
      "url": "https://www.facebook.com/bernard.cornwell/posts/edward-the-elder-as-he-is-now-known-died-in-july-924-he-had-reigned-for-twenty-f/1208872913939753/",
      "title": "Edward the Elder, as he is now known, died in July 924 ... - Facebook",
      "text": "During the reign of his father Alfred the Great, Edward the Elder took an active role in campaigns against the Vikings. On the great Alfred's",
      "score_final": 7.584539890289307,
      "selected_reason": "Explicitly identifies Alfred the Great as Edward the Elder's father"
    },
    {
      "evidence_id": "E2",
      "url": "https://reginajeffers.blog/2012/02/16/alfred-the-greats-son-edward-the-elder/",
      "title": "Alfred the Great’s Son, Edward the Elder | Every Woman Dreams…",
      "text": "![](https://reginajeffers.blog/wp-content/uploads/2018/04/cropped-chatsworth_house_2-jpg.jpg) ## [Alfred the Great’s Son, Edward the Elder](https://reginajeffers.blog/2012/02/16/alfred-the-greats-son-edward-the-elder/) [![](https://reginajeffers.blog/wp-content/uploads/2012/02/edward_the_elder.jpg?w=640 \"Edward_the_Elder\")](https://reginajeffers.blog/wp-content/uploads/2012/02/edward_the_elder.jpg) Edward the Elder Edward the Elder (Old English: Ēadweard se Ieldra; c. 874–877 – 17 July 924) became king in 899 upon the death of his father, Alfred the Great. His court was at Winchester, previous […truncated…]",
      "score_final": 5.882426738739014,
      "selected_reason": "States Edward became king upon the death of his father, Alfred the Great"
    },
    {
      "evidence_id": "E3",
      "url": "https://www.historic-uk.com/HistoryUK/HistoryofEngland/Edward-The-Elder/",
      "title": "Edward The Elder - Historic UK",
      "text": "com/wp-content/uploads/2022/03/edward-elder-177x300.jpg) ![](https://www.historic-uk.com/wp-content/uploads/2022/03/edward-elder-177x300.jpg) Born to King Alfred the Great and his wife Ealhswith of Mercia, he was referred to as the “Elder”, not because he was the eldest son, but rather used by historians to differentiate between the latter [King Edward the Martyr](https://www.historic-uk.com/HistoryUK/HistoryofEngland/Edward-The-Martyr/). As a young boy he was said to have been tutored in Alfred’s court alongside his sister Aelfthryth in literature and prose but also guided in behaviour, duty  […truncated…]",
      "score_final": 3.079357385635376,
      "selected_reason": "Explicitly states Edward was born to King Alfred the Great, directly confirming paternity"
    }
  ],
  "judge": {
    "correctness": {
      "rationale": "The candidate directly states that Alfred the Great was the father of Edward the Elder, matching the gold answers in meaning (including all listed aliases and paraphrases of Alfred).",
      "score": 1
    },
    "answer_relevance": {
      "rationale": "The answer directly states that Alfred the Great is the father of Edward the Elder, which matches the question exactly and provides supporting source context.",
      "score": 1
    },
    "citation_accuracy": {
      "checks": [
        {
          "evidence_id": "E1",
          "claim": "Alfred the Great was the father of Edward the Elder",
          "supported": true,
          "rationale": "The text directly refers to 'his father Alfred the Great' in the context of Edward the Elder."
        },
        {
          "evidence_id": "E2",
          "claim": "Alfred the Great was the father of Edward the Elder",
          "supported": true,
          "rationale": "The text states Edward became king 'upon the death of his father, Alfred the Great'."
        }
      ],
      "accuracy": 1.0,
      "no_citations": false
    }
  },
  "ragas": {
    "faithfulness": 0.75,
    "answer_relevancy": 0.9860323166701195,
    "context_precision": 0.9999999999666667,
    "context_recall": 1.0
  },
  "scoring": {
    "elapsed_seconds": 53.492
  }
}
```
