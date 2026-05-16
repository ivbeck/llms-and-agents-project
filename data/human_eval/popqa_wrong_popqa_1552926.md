# Human Evaluation Checklist — popqa_1552926

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
| **PopQA** |       ☐        |       ☐        |      ☒       |
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
| question_id | popqa_1552926 |
| LLM-judge correctness | -1 |
| LLM-judge answer_relevance | 1 |
| LLM-judge citation_accuracy | 1.000 |

**Human correctness**: `-1` ☒ &nbsp; `0` ☐ &nbsp; `+1` ☐ &nbsp; — short justification: Agent Claim that Welch is the screenwriter, that is after the gold answer is not correct

**Human answer relevance**: `0` ☐ &nbsp; `1` ☒ &nbsp; — short justification: It is revelant, because agents searched after Nort and South

**Human citation accuracy** — one row per `[Ei]` in the answer:

| cite | claim made in the answer | supports? (0/1) |
| --- | --- | :---: |
| E1 | named the screenwriter for promoting an event | 1 |
| E2 | named teh screenwriter | 1 |
| E3 | |named the screenwriter | 1 |
| **mean** |  | 1 |

- [X] My correctness matches the LLM judge
- [X] My answer relevance matches the LLM judge
- [X] My citation accuracy matches the LLM judge (within ±0.1)

Disagreement notes (if any): _…_

---

## 6. Prediction to rate

```json
{
  "question_id": "popqa_1552926",
  "question": "Who was the screenwriter for North & South?",
  "gold": [
    "Elizabeth Gaskell",
    "Author of Mary Barton,",
    "Elizabeth Cleghorn Gaskell",
    "Elizabeth Cleghorn Stevenson",
    "Mrs. Gaskell, née Stevenson"
  ],
  "dataset": "popqa",
  "setup": "full",
  "latency_seconds": 408.9,
  "answer": "Sandy Welch was the screenwriter for *North & South* [E1][E2][E3].\n\nWhy these sources were relevant:\nAll three sources explicitly identify Sandy Welch as the screenwriter for the BBC drama *North & South*: E1 names her as the screenwriter promoting an anniversary event; E2 directly states that the script was written by her; and E3’s infobox formally credits her as the screenplay writer.",
  "critic": {
    "is_grounded": true,
    "is_relevant": true,
    "needs_revision": false,
    "comment": "All three evidence snippets (E1, E2, E3) explicitly name Sandy Welch as the screenwriter for the BBC's North & South, fully supporting the answer. The answer directly addresses the question."
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
      "url": "http://www.morethanthornton.com/blog/2024/11/1/celebrating-20-years-of-the-bbcs-north-and-south",
      "title": "Celebrating 20 years of the BBC's \"North and South\" — More Than Thornton",
      "text": "his beautiful film production of *North and South* is truly worldwide—and ongoing. After 20 years, it still shines as one of the BBC’s best period dramas. It will surely live on as a well-loved classic for decades to come. *You’re invited to join North and South’s screenwriter, Sandy Welch, for an anniversary event sponsored by Elizabeth Gaskell’s House. Register* [*here*](https://elizabethgaskellhouse.co.uk/events/online-event-happy-birthday-north-and-south-with-sandy-welch/) *for the November 6th event. (Replays will be sent if you can’t make the live session.)*",
      "score_final": 7.923905372619629,
      "selected_reason": "explicitly names Sandy Welch as the screenwriter"
    },
    {
      "evidence_id": "E2",
      "url": "https://rissiwrites.com/2018/11/north-and-south-2004.html",
      "title": "North & South (2004): A Beautiful & Authentic Romance",
      "text": "he light of the next day. It’s about love, happiness and beauty in the smallest of joys. north & south 2004 The script is written by Sandy Welch (BBC’s *Emma*, *Jane Eyre* and *Our Mutual Friend*) and directed by the then newcomer Brian Percival. In addition to the primary cast (who are all magnificent) including Daniela and the near-perfect leading man Richard Armitage; the cast also has Brendan Coyle (*Downton Abbey*), Anna Maxwell-Martin, Sinéad Cusack and Rupert Evans. Everyone is brilliant, and should have a gold star on their chart. They embody their respective roles wonderfully; and as  […truncated…]",
      "score_final": 6.84884786605835,
      "selected_reason": "states the script was written by Sandy Welch"
    },
    {
      "evidence_id": "E3",
      "url": "https://en.wikipedia.org/wiki/North_%26_South_(TV_serial)",
      "title": "North & South (TV serial)",
      "text": "(disambiguation) \"North and South (disambiguation)\"). | _North & South_ | | --- | | [![Image 5](https://upload.wikimedia.org/wikipedia/en/1/19/NorthandsouthDVDcover.png)](https://en.wikipedia.org/wiki/File:NorthandsouthDVDcover.png) British DVD cover | | Genre | [Historical drama](https://en.wikipedia.org/wiki/Historical_drama \"Historical drama\") | | Based on | _[North and South](https://en.wikipedia.org/wiki/North\\_and\\_South\\_(Gaskell\\_novel) \"North and South (Gaskell novel)\")_ by [Elizabeth Gaskell](https://en.wikipedia.org/wiki/Elizabeth_Gaskell \"Elizabeth Gaskell\") | | Screenplay by | [Sa […truncated…]",
      "score_final": 3.2564940452575684,
      "selected_reason": "Wikipedia infobox credits Sandy Welch as screenplay writer"
    }
  ],
  "judge": {
    "correctness": {
      "rationale": "Gold answers name Elizabeth Gaskell (author of the original novel). Candidate instead names Sandy Welch (screenwriter of the 2004 BBC adaptation), a different person and fact.",
      "score": -1
    },
    "answer_relevance": {
      "rationale": "The answer directly names Sandy Welch as the screenwriter for North & South, which matches the question exactly and provides supporting source context without any deviation or evasion.",
      "score": 1
    },
    "citation_accuracy": {
      "checks": [
        {
          "evidence_id": "E1",
          "claim": "Sandy Welch was the screenwriter for North & South",
          "supported": true,
          "rationale": "E1 explicitly refers to 'North and South’s screenwriter, Sandy Welch' in an event invitation."
        },
        {
          "evidence_id": "E2",
          "claim": "Sandy Welch was the screenwriter for North & South",
          "supported": true,
          "rationale": "E2 states 'The script is written by Sandy Welch' in a review of the 2004 North & South adaptation."
        },
        {
          "evidence_id": "E3",
          "claim": "Sandy Welch was the screenwriter for North & South",
          "supported": true,
          "rationale": "E3 Wikipedia infobox lists 'Screenplay by Sandy Welch' for the North & South entry."
        }
      ],
      "accuracy": 1.0,
      "no_citations": false
    }
  },
  "ragas": {
    "faithfulness": 0.2,
    "answer_relevancy": 0.8899006639444615,
    "context_precision": 0.0,
    "context_recall": 0.0
  },
  "scoring": {
    "elapsed_seconds": 51.389
  }
}
```
