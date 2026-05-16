# Human Evaluation Checklist — popqa_2542979

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
| **PopQA** |       ☐        |       ☒        |      ☐       |
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
| question_id | popqa_2542979 |
| LLM-judge correctness | 0 |
| LLM-judge answer_relevance | 1 |
| LLM-judge citation_accuracy | 0.667 |

**Human correctness**: `-1` ☐ &nbsp; `0` ☒ &nbsp; `+1` ☐ &nbsp; — short justification: It is rejected because it serached after another authors

**Human answer relevance**: `0` ☐ &nbsp; `1` ☒ &nbsp; — short justification: It revelant, beacuse it searched after the same title

**Human citation accuracy** — one row per `[Ei]` in the answer:

| cite | claim made in the answer | supports? (0/1) |
| --- | --- | :---: |
| E1 | indentified an Author named November | 1 |
| E2 | indentified Colleen Hoover as the author of the novel November 9 | 1 |
| E3 | indentified Josephine Winslow Johnson as the author of Now in November | 1 |
| **mean** |  | 1 |,

- [X] My correctness matches the LLM judge
- [X] My answer relevance matches the LLM judge
- [ ] My citation accuracy matches the LLM judge (within ±0.1)

Disagreement notes (if any): 
The citation score from the judge is wrong. In one source, he claimed this was incorrect, but it was actually correct.


---

## 6. Prediction to rate

```json
{
  "question_id": "popqa_2542979",
  "question": "Who is the author of November?",
  "gold": [
    "Gustave Flaubert",
    "Flaubert"
  ],
  "dataset": "popqa",
  "setup": "full",
  "latency_seconds": 1735.15,
  "answer": "The evidence is incomplete regarding the author of a work titled exactly “November.” The evidence does identify November J. Brown as an author and coach named November [E1], Colleen Hoover as the author of the novel *November 9* [E2], and Josephine Winslow Johnson as the author of *Now in November* [E3].\n\n**Why these sources were relevant:**\nE1 was selected because it identifies November J. Brown as an author/coach named November. E2 was selected because it identifies Colleen Hoover as the author of the novel *November 9*. E3 was selected because it identifies Josephine Winslow Johnson as the author of *Now in November*. Each source connects an author to the name “November,” though none establish the author of a work titled exactly “November.”",
  "critic": {
    "is_grounded": true,
    "is_relevant": true,
    "needs_revision": false,
    "comment": "All factual claims are supported by the evidence, and the answer correctly notes that none of the sources establish the author of a work titled exactly 'November'."
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
      "url": "https://www.writesofnovember.com/",
      "title": "November J. Brown",
      "text": "social media shoutouts, and more! [Learn more!](/free-resources) [Learn more!](/free-resources) * ## “Following November’s advice has allowed me to make major strides in my own publishing journey (even as a mama to 5 busy kids!) and I will be releasing my debut novel soon, thanks to her encouragement and words of wisdom!” - Olivia M. (@oliviamccarthyauthor) * ## “November has given me the tools, the confidence, and the push I've needed to continue writing. She’s made me feel like I can actually finish a book after all.” - Zoe S. (@zoesallbooked) * ## “Every author needs a cheerleader and mento […truncated…]",
      "score_final": 2.922879695892334,
      "selected_reason": "directly profiles author November J. Brown, who is identified as an author/writing coach named November"
    },
    {
      "evidence_id": "E2",
      "url": "https://www.alwayswithabook.com/2021/11/review-november-9-by-colleen-hoover.html",
      "title": "Review: November 9 by Colleen Hoover - Always With a Book",
      "text": "[Always With a Book](https://www.alwayswithabook.com/ \"Always With a Book\") [k2reader](https://www.alwayswithabook.com/author/k2reader \"Posts by k2reader\") # Review: November 9 by Colleen Hoover **Publisher:** Atria Books **Published:** November 10, 2015 **Source:** ARC Paperback via Publisher ### **Summary:** Beloved #1 *New York Times* bestselling author Colleen Hoover returns with an unforgettable love story between a writer and his unexpected muse. Fallon meets Ben, an aspiring novelist, the day before her scheduled cross-country move. Their untimely attraction leads them to spend Fallon’s […truncated…]",
      "score_final": 1.8718891143798828,
      "selected_reason": "directly states Colleen Hoover is the author of the novel 'November 9', the closest book title match to 'November'"
    },
    {
      "evidence_id": "E3",
      "url": "https://www.ashleyhajimirsadeghi.com/blog/now-in-november-josephine-johnson",
      "title": "Review, Summary, Analysis: Now in November by Josephine Winslow Johnson — Ashley Hajimirsadeghi",
      "text": "ut something besides a pulp?” — Josephine Winslow Johnson * * * ![Image 1](https://images.squarespace-cdn.com/content/v1/5ea1f794501b7153b29e7cd7/43d32fbb-2048-4c01-b66b-bfd80f6a7ccf/267115.jpg) _Now in November_ by Josephine Winslow Johnson (1934). I don’t know when I first heard about this novel, but I’m pretty sure I saw it on one of my recommendation sites. I find out about books through a strange, slightly eclectic mixture of websites, so I’m confident this is where I found out about this one. The premise of _Now in November_ isn’t what sold me about; it was the author herself. In 1935, t […truncated…]",
      "score_final": 1.1459457874298096,
      "selected_reason": "directly states Josephine Winslow Johnson is the author of 'Now in November', another close book title match"
    }
  ],
  "judge": {
    "correctness": {
      "rationale": "The candidate explicitly states that evidence is incomplete for any work titled exactly 'November' and offers no author identification at all, instead listing unrelated titles/authors; this is a hedged non-answer rather than a factual claim (correct or incorrect).",
      "score": 0
    },
    "answer_relevance": {
      "rationale": "The provided answer directly engages the query by examining possible authors linked to titles containing 'November' and stating that no exact match exists, which constitutes an on-topic attempt to identify the author.",
      "score": 1
    },
    "citation_accuracy": {
      "checks": [
        {
          "evidence_id": "E1",
          "claim": "identifies November J. Brown as an author/coach named November",
          "supported": false,
          "rationale": "Evidence refers to a publishing coach/mentor named November and her advice to authors but never mentions the surname Brown or states that November herself is an author."
        },
        {
          "evidence_id": "E2",
          "claim": "identifies Colleen Hoover as the author of the novel November 9",
          "supported": true,
          "rationale": "Evidence explicitly titles the review 'November 9 by Colleen Hoover' and describes her as the bestselling author of that novel."
        },
        {
          "evidence_id": "E3",
          "claim": "identifies Josephine Winslow Johnson as the author of Now in November",
          "supported": true,
          "rationale": "Evidence directly states '_Now in November_ by Josephine Winslow Johnson (1934)' and discusses her as the book's author and Pulitzer winner."
        }
      ],
      "accuracy": 0.6666666666666666,
      "no_citations": false
    }
  },
  "ragas": {
    "faithfulness": 0.4444444444444444,
    "answer_relevancy": 0.9368955215904395,
    "context_precision": 0.0,
    "context_recall": 0.0
  },
  "scoring": {
    "elapsed_seconds": 64.427
  }
}
```
