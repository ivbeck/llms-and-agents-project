# Human Evaluation Checklist — simpleqa_2210

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
| **SimpleQA** |       ☐        |       ☐        |      ☒       |
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
| question_id | simpleqa_2210 |
| LLM-judge correctness | -1 |
| LLM-judge answer_relevance | 1 |
| LLM-judge citation_accuracy | 0.000 |

**Human correctness**: `-1` ☒ &nbsp; `0` ☐ &nbsp; `+1` ☐ &nbsp; — short justification: The candidate named the wrong publication. 

**Human answer relevance**: `0` ☐ &nbsp; `1` ☒ &nbsp; — short justification: It searched for the right photograph.

**Human citation accuracy** — one row per `[Ei]` in the answer:

| cite | claim made in the answer | supports? (0/1) |
| --- | --- | :---: |
| E1 | claimed Inkanyiso as onyl work in 2011  | 0 |
| **mean** |  | 0 |

- [X] My correctness matches the LLM judge
- [X] My answer relevance matches the LLM judge
- [X] My citation accuracy matches the LLM judge (within ±0.1)

Disagreement notes (if any): _…_

---

## 6. Prediction to rate

```json
{
  "question_id": "simpleqa_2210",
  "question": "What is the full title of Zanele Muholi's publication from 2011?",
  "gold": [
    "Zanele Muholi: African Women Photographers #1"
  ],
  "dataset": "simpleqa",
  "setup": "full",
  "latency_seconds": 1424.917,
  "answer": "The full title of Zanele Muholi's 2011 publication is **\"Images of Trans Being and Becoming\"** [E1].\n\n**Why these sources were relevant**\nThe evidence explicitly identified the 2011 article by Zanele Muholi, providing its full title and its publication in *Feminist Studies* [E1].",
  "critic": {
    "is_grounded": true,
    "is_relevant": true,
    "needs_revision": false,
    "comment": "The evidence explicitly lists 'Images of Trans Being and Becoming' as Zanele Muholi's 2011 article in Feminist Studies, supporting the answer's claim about the full title."
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
  "sources_count": 2,
  "evidence_count": 2,
  "evidence": [
    {
      "evidence_id": "E1",
      "url": "https://oblogdee.blog/2011/07/06/south-african-lesbian-photographer-activist-zanele-muholis-exhibits-new-portraits/",
      "title": "South African Lesbian Photographer Activist: Zanele Muholi’s Exhibits New Portraits – O-blog-dee-o-blog-da",
      "text": "[Skip to content](#content) # [O-blog-dee-o-blog-da](https://oblogdee.blog/) ## Life goes on…. ### South African Lesbian Photographer Activist: Zanele Muholi’s Exhibits New Portraits Posted on by [Melanie Nathan](https://oblogdee.blog/author/oblogdeeoblogda/) July 06, 2011, by Melanie Nathan, [![](https://oblogdee.blog/wp-content/uploads/2011/07/zanele-exhibition.jpg?w=748 \"zanele exhibition\")](https://oblogdee.blog/wp-content/uploads/2011/07/zanele-exhibition.jpg) Photo by Zanele Muholi Inkanyiso brings together three new bodies of photographic work: new portraits in the ongoing series Faces  […truncated…]",
      "score_final": 4.833574295043945,
      "selected_reason": "Identifies 'Inkanyiso' as the full title of Muholi's 2011 exhibition and associated project, the only 2011 titled work by Muholi described in the candidates."
    },
    {
      "evidence_id": "E2",
      "url": "http://archive.stevenson.info/exhibitions/muholi/index2011.html",
      "title": "STEVENSON | Zanele Muholi",
      "text": "umination' or 'light' in Zulu, and it is Muholi's aim to 'shine a light onto viewers' understanding of gender and sexuality'. She writes: > *Inkanyiso* speaks about the complexities of gender and sexuality terminologies in which lesbianism or gayness (homosexuality) equals sexual orientation, and transgenderism equals gender. *Inkanyiso* presents those who have given of themselves to shed a light on the vast issues that continue to affect sexual minorities, especially black queers. These are people found in spaces that are sometimes disadvantaged. They are the ones who want to but cannot expre […truncated…]",
      "score_final": 1.3556594848632812,
      "selected_reason": "Provides corroborating details about the 2011 Inkanyiso exhibition and associated photographic series from the gallery's 2011 archive."
    }
  ],
  "judge": {
    "correctness": {
      "rationale": "Candidate claims the 2011 title is \"Images of Trans Being and Becoming\", which directly contradicts the gold answer \"Zanele Muholi: African Women Photographers #1\".",
      "score": -1
    },
    "answer_relevance": {
      "rationale": "The provided answer directly states a full title for Zanele Muholi's 2011 publication and explains its source, which matches the question's request for that specific information.",
      "score": 1
    },
    "citation_accuracy": {
      "checks": [
        {
          "evidence_id": "E1",
          "claim": "full title of Zanele Muholi's 2011 publication is \"Images of Trans Being and Becoming\"",
          "supported": false,
          "rationale": "Evidence describes a 2011 exhibition titled Inkanyiso with Transfigures series but contains no mention of that title or any 2011 Feminist Studies publication."
        }
      ],
      "accuracy": 0.0,
      "no_citations": false
    }
  },
  "ragas": {
    "faithfulness": 0.0,
    "answer_relevancy": 0.9851632362279429,
    "context_precision": 0.0,
    "context_recall": 0.0
  },
  "scoring": {
    "elapsed_seconds": 71.259
  }
}
```
