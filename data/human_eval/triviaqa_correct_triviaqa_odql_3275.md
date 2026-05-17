# Human Evaluation Checklist — triviaqa_odql_3275

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
| **PopQA** |       ☐        |       ☐        |      ☐       |
| **TriviaQA** |       ☒        |       ☐        |      ☐       |

## 4. Rating procedure

- [X] Read the **question** in §6 carefully — what is it actually asking for?
- [x] Read the **gold answer(s)** — these are the accepted answers including aliases.
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
| dataset | triviaqa |
| question_id | triviaqa_odql_3275 |
| LLM-judge correctness | 1 |
| LLM-judge answer_relevance | 1 |
| LLM-judge citation_accuracy | 0.667 |

**Human correctness**: `-1` ☐ &nbsp; `0` ☐ &nbsp; `+1` ☒ &nbsp; — short justification: The candidate answered the right question.

**Human answer relevance**: `0` ☐ &nbsp; `1` ☒ &nbsp; — short justification: It is relevant because of the right answer.

**Human citation accuracy** — one row per `[Ei]` in the answer:

| cite | claim made in the answer | supports? (0/1) |
| --- | --- | :---: |
| E1 | Burgess Meredith portrayed the Penguin | 1 |
| E2 | Burgess Meredith portrayed the Penguin  | 1 |
| E3 | Burgess Meredith portrayed the Penguin in the serie and in a spin-off film | 1|
| E4 | no claim and source | 0|
| **mean** |  | 0.75|

- [X] My correctness matches the LLM judge
- [X] My answer relevance matches the LLM judge
- [X] My citation accuracy matches the LLM judge (within ±0.1)

Disagreement notes (if any): The judge claims that the spin-offs are not mentioned. However, the movie is listed in his actor list.


---

## 6. Prediction to rate

```json
{
  "question_id": "triviaqa_odql_3275",
  "question": "Who played the part of 'The Penguin' in the TV series 'Batman'?",
  "gold": [
    "BURGESS MEREDITH",
    "Oliver Meredith",
    "Oliver Burgess Meredith"
  ],
  "dataset": "triviaqa",
  "setup": "full",
  "latency_seconds": 142.853,
  "answer": "Burgess Meredith played the Penguin in the 1966 *Batman* TV series [E1][E2][E3][E4]. He portrayed the character in nineteen episodes of the series [E1] and also appeared in the 1966 spinoff film [E2].\n\nWhy these sources were relevant:\nThese sources explicitly identify Burgess Meredith as the actor who portrayed the Penguin in the 1966 *Batman* television series and document his appearances across multiple episodes and the related feature film.",
  "critic": {
    "is_grounded": true,
    "is_relevant": true,
    "needs_revision": false,
    "comment": "All factual claims—that Burgess Meredith played the Penguin in the 1966 Batman TV series, that he appeared in nineteen episodes, and that he appeared in the 1966 spinoff film—are directly supported by evidence E1, E2, E3, and E4. The answer directly addresses the question asked."
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
      "url": "https://www.facebook.com/metvnetwork/posts/burgess-meredith-loved-his-time-as-the-penguin-watch-batman-66-tonight-at-1030p-/1360553702768044/",
      "title": "Burgess Meredith loved his time as the Penguin! Watch Batman '66 ...",
      "text": "Burgess Meredith's iconic portrayal of the Penguin in the 1966 Batman TV series ... Burgess Meredith portrayed the Penguin in nineteen episodes of",
      "score_final": 8.599355697631836,
      "selected_reason": "directly states Burgess Meredith portrayed the Penguin in the 1966 Batman TV series"
    },
    {
      "evidence_id": "E2",
      "url": "https://www.imdb.com/name/nm0580565/",
      "title": "Burgess Meredith(1907-1997) - IMDb",
      "text": "His character, the Penguin, was so popular as a villain on the television series Batman (1966), the producers always had a Penguin script ready in case Meredith",
      "score_final": 5.890868186950684,
      "selected_reason": "identifies Burgess Meredith as the actor who played the Penguin in the 1966 television series"
    },
    {
      "evidence_id": "E3",
      "url": "https://batman.fandom.com/wiki/Burgess_Meredith",
      "title": "Burgess Meredith | Batman Wiki - Fandom",
      "text": "Burgess Meredith portrayed the Penguin in William Dozier's ABC television series, as well as the 1966 spinoff film. Meredith's portrayal of the Penguin tied",
      "score_final": 5.802414417266846,
      "selected_reason": "confirms Burgess Meredith portrayed the Penguin in the ABC television series and spinoff film"
    }
  ],
  "judge": {
    "correctness": {
      "rationale": "Candidate directly states Burgess Meredith played the Penguin (matching gold exactly, with added details irrelevant to correctness). No refusal, contradiction, or mismatch.",
      "score": 1
    },
    "answer_relevance": {
      "rationale": "The answer directly names Burgess Meredith as the actor who played The Penguin in the 1966 Batman TV series, matching the question exactly with no evasion or off-topic content.",
      "score": 1
    },
    "citation_accuracy": {
      "checks": [
        {
          "evidence_id": "E4",
          "claim": "",
          "supported": false,
          "rationale": "Cited evidence id is not present in the retrieved evidence pool."
        },
        {
          "evidence_id": "E1",
          "claim": "Burgess Meredith played the Penguin in the 1966 Batman TV series",
          "supported": true,
          "rationale": "E1 directly states Burgess Meredith's portrayal of the Penguin in the 1966 Batman TV series."
        },
        {
          "evidence_id": "E1",
          "claim": "He portrayed the character in nineteen episodes of the series",
          "supported": true,
          "rationale": "E1 explicitly notes that Burgess Meredith portrayed the Penguin in nineteen episodes."
        },
        {
          "evidence_id": "E2",
          "claim": "Burgess Meredith played the Penguin in the 1966 Batman TV series",
          "supported": true,
          "rationale": "E2 refers to his character the Penguin on the Batman (1966) television series, confirming the role."
        },
        {
          "evidence_id": "E2",
          "claim": "also appeared in the 1966 spinoff film",
          "supported": false,
          "rationale": "E2 makes no mention of the 1966 spinoff film or Meredith's appearance in it."
        },
        {
          "evidence_id": "E3",
          "claim": "Burgess Meredith played the Penguin in the 1966 Batman TV series",
          "supported": true,
          "rationale": "E3 states that Burgess Meredith portrayed the Penguin in the ABC television series Batman."
        }
      ],
      "accuracy": 0.6666666666666666,
      "no_citations": false
    }
  },
  "ragas": {
    "faithfulness": 1.0,
    "answer_relevancy": 0.9242346331568204,
    "context_precision": 0.9999999999666667,
    "context_recall": 1.0
  },
  "scoring": {
    "elapsed_seconds": 66.109
  }
}
```
