# Human Evaluation Checklist — triviaqa_bt_1978

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
| **TriviaQA** |       ☐        |       ☒        |      ☐       |

## 4. Rating procedure

- [X] Read the **question** in §6 carefully — what is it actually asking for?
- [X] Read the **gold answer(s)** — these are the accepted answers including aliases.
- [X] Read the **candidate answer** — do not look at the judge's verdict yet.
- [X] Decide your own **correctness** score (`-1` / `0` / `+1`).
- [X] Decide your own **answer relevance** score (`0` / `1`).
- [X] For each `[Ei]` citation in the answer:
    - [x] Find evidence `Ei` in the `evidence` list.
    - [X] Decide whether that piece of evidence really supports the cited claim (`0` / `1`).
- [X] Compute the **citation accuracy** as the mean of those 0/1 decisions.
- [X] Compare each of your three scores against the LLM judge's scores in the JSON.

## 5. Your ratings

| field | value |
| --- | --- |
| dataset | triviaqa |
| question_id | triviaqa_bt_1978 |
| LLM-judge correctness | 0 |
| LLM-judge answer_relevance | 1 |
| LLM-judge citation_accuracy | 0.500 |

**Human correctness**: `-1` ☐ &nbsp; `0` ☒ &nbsp; `+1` ☐ &nbsp; — short justification:  The candidate couldn't answer.


**Human answer relevance**: `0` ☐ &nbsp; `1` ☒ &nbsp; — short justification: The candidate searched for the Birmingham canals. This was relevant to the question, even though he could not answer it.
**Human citation accuracy** — one row per `[Ei]` in the answer:

| cite | claim made in the answer | supports? (0/1) |
| --- | --- | :---: |
| E1 | claims that Birmingham has less canals then venice  | 1|
| E2 | claims that Birmingham has more canaals in miles  then venice with 100 miles  | 1 |
| **mean** |  | 1 |

- [X] My correctness matches the LLM judge
- [X] My answer relevance matches the LLM judge
- [ ] My citation accuracy matches the LLM judge (within ±0.1)

Disagreement notes (if any): The judge said that one claim cannot be proven by one source. This is incorrect.

---

## 6. Prediction to rate

```json
{
  "question_id": "triviaqa_bt_1978",
  "question": "Which English city has the most canals",
  "gold": [
    "Birmingham",
    "County Borough of Birmingham",
    "Birmingham overspill",
    "Metropolitan Borough of Birmingham",
    "B'Ham",
    "Great Barr Primary School",
    "City of Birmingham",
    "City of a thousand and one trades",
    "Birmingham, UK",
    "Birminghamian",
    "Birmingham (borough)",
    "City of a thousand trades",
    "Nelson Mandela Primary School",
    "Crime and policing in Birmingham",
    "Birmingham, United Kingdom",
    "The weather in Birmingham",
    "Bournville Junior School",
    "Birmingham Corporation",
    "Birmingham Heritage Festival",
    "Bimringham",
    "Birmingham artistic figures",
    "Beormingham",
    "Birmingham, West Midlands",
    "England Birmingham",
    "Birmingham, England",
    "UN/LOCODE:GBBHM"
  ],
  "dataset": "triviaqa",
  "setup": "full",
  "latency_seconds": 278.322,
  "answer": "The evidence does not explicitly identify which English city has the most canals. It notes that Birmingham has more canals than Venice by total navigable length, with the Birmingham Canal Navigations extending to just over 100 miles [E1][E2]. However, the evidence does not compare Birmingham against other English cities to confirm it has the most. It also clarifies that Birmingham has only six individual canals, and that the “more canals than Venice” claim refers to total waterway mileage rather than the number of separate canals [E2].\n\n**Why these sources were relevant**\nThese sources were relevant because they discuss Birmingham’s extensive canal network and its well-known claim of having more canals than Venice [E1][E2]. They provide specific mileage figures and clarify that such comparisons are based on total navigable waterway length rather than the count of individual canals [E2]. Nevertheless, they only compare Birmingham to non-English cities (Venice and Amsterdam), not to other English cities, so they do not fully answer the question.",
  "critic": {
    "is_grounded": true,
    "is_relevant": true,
    "needs_revision": false,
    "comment": "The answer correctly reflects the evidence: it notes Birmingham's extensive canal mileage and the 'more than Venice' claim, accurately cites the ~100 miles figure and the six-canal count from the sources, and properly identifies that the evidence does not compare Birmingham against other English cities to confirm it has the most."
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
  "evidence_count": 3,
  "evidence": [
    {
      "evidence_id": "E1",
      "url": "https://apetcher.wordpress.com/2015/07/25/birmingham-more-canals-than-venice/",
      "title": "Birmingham – More Canals than Venice | Have Bag, Will Travel",
      "text": "dam and just twenty five in Venice. But thinking in terms of the number of canals, it is wrong; Birmingham only really has six canals whereas Amsterdam has 165 and Venice has 177. I am just saying. After walking around the Civic Centre we made our way now to Brindleyplace which is at the heart of the canal infrastructure of the city and which has been regenerated and thoroughly reinvented as a tourist attraction. By the 1970s Birmingham’s canals were in a serious state of disrepair, crumbling away, dirty and smelly and lined by derelict warehouses and the City Council even considered a proposa […truncated…]",
      "score_final": 3.8264613151550293,
      "selected_reason": "clarifies Birmingham has only 6 individual canals versus Venice's 177, distinguishing canal count from total waterway length"
    },
    {
      "evidence_id": "E2",
      "url": "https://canalrivertrust.org.uk/news-and-views/features/fascinating-facts-about-canals-and-rivers",
      "title": "Fascinating Facts about Rivers and Canals | Canal & River Trust",
      "text": "in canals? Our charity cares for 2,000 miles of canals, which create a unique natural corridor across the UK and provide homes for a variety of wonderful wildlife. From dozens of fish species swimming in the depths, to water voles burrowing into canal banks and kingfishers soaring above, you can read more about waterway wildlife in [our spotter's guide](/things-to-do/canal-and-river-wildlife/a-spotters-guide-to-waterway-wildlife). ## Did you know? * Britain's longest river is the [River Severn](/canals-and-rivers/river-severn) at 220 miles. In comparison, the **world's longest river** is the N […truncated…]",
      "score_final": 3.0213112831115723,
      "selected_reason": "authoritative source stating Birmingham Canal Navigations extend over 100 miles, directly supporting Birmingham's claim to exceed Venice by mileage"
    },
    {
      "evidence_id": "E3",
      "url": "https://apetcher.wordpress.com/2015/07/25/birmingham-more-canals-than-venice/",
      "title": "Birmingham – More Canals than Venice | Have Bag, Will Travel",
      "text": "e Canals than Venice Posted on [July 25, 2015](https://apetcher.wordpress.com/2015/07/25/birmingham-more-canals-than-venice/ \"4:10 am\") | [26 Comments](https://apetcher.wordpress.com/2015/07/25/birmingham-more-canals-than-venice/#comments) When visiting Birmingham it is almost inevitable to come across the proud boast that the city has *‘More Canals than Venice’.*Birmingham has been called the ‘*Venice of the North’* but this isn’t a title that it holds uniquely because it has also been applied to [Saint Petersburg](https://anotherbagmoretravel.wordpress.com/2014/07/05/russia-sightseeing-tour- […truncated…]",
      "score_final": 2.833216667175293,
      "selected_reason": "explains Birmingham's 'more canals than Venice' claim is based on navigable waterway length (100+ miles vs ~25 in Venice) and notes Manchester as another major English canal city"
    }
  ],
  "judge": {
    "correctness": {
      "rationale": "The candidate explicitly refuses to identify any city as having the most canals and hedges that the sources do not confirm Birmingham (or any other city), providing no factual answer to the question.",
      "score": 0
    },
    "answer_relevance": {
      "rationale": "The answer directly engages the question by referencing Birmingham's canal mileage, clarifying the 'more than Venice' claim, and noting the absence of comparisons to other English cities, keeping the focus squarely on identifying the city with the most canals.",
      "score": 1
    },
    "citation_accuracy": {
      "checks": [
        {
          "evidence_id": "E1",
          "claim": "Birmingham has more canals than Venice by total navigable length (~100 miles)",
          "supported": false,
          "rationale": "E1 mentions only that Birmingham has six canals and contrasts the number (not length) with Venice/Amsterdam; it contains no mileage figure or length-based comparison."
        },
        {
          "evidence_id": "E2",
          "claim": "Birmingham has more canals than Venice by total navigable length (~100 miles) and the claim refers to mileage not number of canals",
          "supported": true,
          "rationale": "E2 explicitly states the Birmingham Canal Navigations extend to just over 100 miles and notes the common 'more canals than Venice' claim is based on that length metric."
        }
      ],
      "accuracy": 0.5,
      "no_citations": false
    }
  },
  "ragas": {
    "faithfulness": 1.0,
    "answer_relevancy": 0.0,
    "context_precision": 0.9999999999666667,
    "context_recall": 1.0
  },
  "scoring": {
    "elapsed_seconds": 66.746
  }
}
```
