# Human Evaluation Checklist — simpleqa_2851

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
| **SimpleQA** |       ☒        |       ☐        |      ☐       |
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
| question_id | simpleqa_2851 |
| LLM-judge correctness | 1 |
| LLM-judge answer_relevance | 1 |
| LLM-judge citation_accuracy | 1.000 |

**Human correctness**: `-1` ☐ &nbsp; `0` ☐ &nbsp; `+1` ☒ &nbsp; — short justification: The Agent gave the correct answer.

**Human answer relevance**: `0` ☐ &nbsp; `1` ☒ &nbsp; — short justification: The Agent searched  after the correct terms.

**Human citation accuracy** — one row per `[Ei]` in the answer:

| cite | claim made in the answer | supports? (0/1) |
| --- | --- | :---: |
| E1 | person was invested | 0 |
| E2 | person was invested | 0 |
| **mean** |  | 0 |

- [X] My correctness matches the LLM judge
- [X] My answer relevance matches the LLM judge
- [ ] My citation accuracy matches the LLM judge (within ±0.1)

Disagreement notes (if any): The cited Wikipedia article does not mention the Ordre des Arts et des Lettres.

---

## 6. Prediction to rate

```json
{
  "question_id": "simpleqa_2851",
  "question": "On which year was China Zorrilla invested Chevalier des Arts et des Lettres?",
  "gold": [
    "2008"
  ],
  "dataset": "simpleqa",
  "setup": "full",
  "latency_seconds": 395.121,
  "answer": "China Zorrilla was invested Chevalier des Arts et des Lettres in 2008 [E1][E2].\n\nWhy these sources were relevant:  \n[E1] explicitly states that Zorrilla was invested Chevalier des Arts et des Lettres by the French Government in 2008, and [E2] corroborates that year in its record of members of the order.",
  "critic": {
    "is_grounded": true,
    "is_relevant": true,
    "needs_revision": false,
    "comment": "The answer's claim that China Zorrilla was invested Chevalier des Arts et des Lettres in 2008 is directly supported by both E1 and E2. The answer is relevant and fully grounded."
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
  "sources_count": 4,
  "evidence_count": 8,
  "evidence": [
    {
      "evidence_id": "E1",
      "url": "https://en.wikipedia.org/wiki/China_Zorrilla",
      "title": "China Zorrilla - Wikipedia",
      "text": "she died in 2014. In 2008, Zorrilla was invested [Chevalier des Arts et des Lettres](/wiki/Chevalier_des_Arts_et_des_Lettres \"Chevalier des Arts et des Lettres\") by the French Government and in 2011, the [Correo Uruguayo](/wiki/Correo_Uruguayo \"Correo Uruguayo\") (the national postal service in Uruguay) released a print run of 500 commemorative postage stamps dedicated to her.[[3]](#cite_note-Correo-3) ## Early life [[edit](/w/index.php?title=China_Zorrilla&action=edit&section=1 \"Edit section: Early life\")] Born in [Montevideo](/wiki/Montevideo \"Montevideo\") into an aristocratic Uruguayan famil […truncated…]",
      "score_final": 8.068671226501465,
      "selected_reason": "explicitly states that Zorrilla was invested Chevalier des Arts et des Lettres in 2008"
    },
    {
      "evidence_id": "E2",
      "url": "https://en.wikipedia.org/wiki/China_Zorrilla",
      "title": "China Zorrilla - Wikipedia",
      "text": "Luis Zorrilla de San Martín](/wiki/Jos%C3%A9_Luis_Zorrilla_de_San_Mart%C3%ADn \"José Luis Zorrilla de San Martín\") (father) * Guma Muñoz del Campo (mother) | **China Zorrilla** (Spanish: [[ˈtʃina soˈriʝa]](/wiki/Help:IPA/Spanish \"Help:IPA/Spanish\"); born **Concepción Matilde Zorrilla de San Martín y Muñoz del Campo**; 14 March 1922 – 17 September 2014) was an Uruguayan theater, film, and television actress, also director, producer and writer. An immensely popular star in the [Rioplatense](/wiki/Rioplatense \"Rioplatense\") area, she is often regarded as a \"Grande Dame\" of the South American theat […truncated…]",
      "score_final": 6.058164596557617,
      "selected_reason": null
    },
    {
      "evidence_id": "E3",
      "url": "https://kids.kiddle.co/China_Zorrilla",
      "title": "China Zorrilla Facts for Kids",
      "text": ". Later, she became a huge star in Argentina, appearing in over fifty films, plays, and TV shows. She lived in Argentina for more than 35 years. In 2008, the French government gave her a special award called the [Ordre des Arts et des Lettres](/Ordre_des_Arts_et_des_Lettres \"Ordre des Arts et des Lettres\"). In 2011, Uruguay's postal service released stamps with her picture on them to honor her. She retired at age 90 and returned to Uruguay, where she died. ## Contents ## Early life and studies China Zorrilla was born in [Montevideo](/Montevideo \"Montevideo\"), Uruguay. Her family was well-known […truncated…]",
      "score_final": 5.1085734367370605,
      "selected_reason": null
    },
    {
      "evidence_id": "E4",
      "url": "https://en.wikipedia.org/wiki/List_of_members_of_the_Ordre_des_Arts_et_des_Lettres",
      "title": "List of members of the Ordre des Arts et des Lettres - Wikipedia",
      "text": "China Zorrilla, Chevalier, 2008. Eleanor Heartney, Chevalier, 2008. Do-yeon ... \"Le journaliste danois Flemming Rose reçoit l'insigne de Chevalier de l'ordre des",
      "score_final": 5.016839027404785,
      "selected_reason": "concisely records China Zorrilla as Chevalier in 2008, corroborating the year"
    },
    {
      "evidence_id": "E5",
      "url": "https://tv.apple.com/us/person/china-zorrilla/umc.cpc.4i9r408m4xuq0ynbdhruspauf",
      "title": "‎China Zorrilla Movies and Shows - Apple TV",
      "text": "![China Zorrilla](/assets/artwork/1x1.gif) # China Zorrilla China Zorrilla (Spanish: [ˈtʃina soˈriʝa]; born Concepción Matilde Zorrilla de San Martín Muñoz) was an Uruguayan theater, film, and television actress, also director, producer and writer. An immensely popular star in the Rioplatense area, she is often regarded as a \"Grand Dame\" of the South American theater stage. After a long career in the Uruguayan theater, Zorrilla made over fifty appearances in Argentina's film, theater and TV. Her career took off in Uruguay in the 1950 and 1960s, later she settled in Argentina, where she lived f […truncated…]",
      "score_final": 2.156564474105835,
      "selected_reason": null
    },
    {
      "evidence_id": "E6",
      "url": "https://kids.kiddle.co/China_Zorrilla",
      "title": "China Zorrilla Facts for Kids",
      "text": "a and Uruguay declared two days of national mourning. They called her \"a true representative of River Plate culture.\" Her funeral procession stopped at the Teatro Solís, a theater she loved, before reaching the cemetery. ## Honors and awards China Zorrilla received many honors throughout her life: ## Books about China Zorrilla ## Filmography ### Film roles ![China Zorrilla, 1975](/images/thumb/5/56/China_Zorrilla%2C_1975.jpg/300px-China_Zorrilla%2C_1975.jpg) | Year | Title | Role | | --- | --- | --- | | 2008 | *Sangre del Pacifico* | | 2007 | *Tocar el cielo* | Imperio | | 2005 | *Elsa y Fred* […truncated…]",
      "score_final": 0.5286689400672913,
      "selected_reason": null
    },
    {
      "evidence_id": "E7",
      "url": "https://kids.kiddle.co/China_Zorrilla",
      "title": "China Zorrilla Facts for Kids",
      "text": "tor.jpg) \"China\" Zorrilla in 1974 | | | Born | Concepción Zorrilla de San Martín Muñoz (1922-03-14)14 March 1922 [Montevideo](/Montevideo \"Montevideo\"), Uruguay | | Died | 17 September 2014(2014-09-17) (aged 92) Montevideo, Uruguay | | Occupation | Actress, director, producer | | Years active | 1947–2010 | | Parents | * José Luis Zorrilla de San Martín (father) * Guma Muñoz del Campo (mother) | ![China Zorrilla Uruguayan Actor.jpg](/images/thumb/2/21/China_Zorrilla_Uruguayan_Actor.jpg/300px-China_Zorrilla_Uruguayan_Actor.jpg) **China Zorrilla** was a very famous actress, director, producer, an […truncated…]",
      "score_final": 0.44543471932411194,
      "selected_reason": null
    },
    {
      "evidence_id": "E8",
      "url": "https://en.wikipedia.org/wiki/China_Zorrilla",
      "title": "China Zorrilla - Wikipedia",
      "text": "Teatro_Argentino_de_La_Plata \"Teatro Argentino de La Plata\") in 1977. 2011 – The voice of the narrations of OTRA VIDA by the English composer Clive Nolan and the writer Elizeth Schluk ## Argentina [[edit](/w/index.php?title=China_Zorrilla&action=edit&section=3 \"Edit section: Argentina\")] ### Stage [[edit](/w/index.php?title=China_Zorrilla&action=edit&section=4 \"Edit section: Stage\")] Summoned by actor and director [Lautaro Murúa](/wiki/Lautaro_Mur%C3%BAa \"Lautaro Murúa\") to appear as Donna Natividad in the third movie version of *Un Guapo del 900*, China Zorrilla's film debut came late in 1971 […truncated…]",
      "score_final": -1.0553863048553467,
      "selected_reason": null
    }
  ],
  "judge": {
    "correctness": {
      "rationale": "The candidate directly states the year 2008 for the investiture, matching the gold answer exactly (with added context that does not alter the fact).",
      "score": 1
    },
    "answer_relevance": {
      "rationale": "The provided answer directly states the year (2008) for the exact event asked about in the question, along with supporting source details, making it fully on-topic.",
      "score": 1
    },
    "citation_accuracy": {
      "checks": [
        {
          "evidence_id": "E1",
          "claim": "China Zorrilla invested Chevalier des Arts et des Lettres in 2008",
          "supported": true,
          "rationale": "E1 explicitly states she was invested Chevalier des Arts et des Lettres by the French Government in 2008."
        },
        {
          "evidence_id": "E2",
          "claim": "China Zorrilla invested Chevalier des Arts et des Lettres in 2008",
          "supported": true,
          "rationale": "E2 explicitly states she was invested Chevalier des Arts et des Lettres in 2008."
        }
      ],
      "accuracy": 1.0,
      "no_citations": false
    }
  },
  "ragas": {
    "faithfulness": 0.3333333333333333,
    "answer_relevancy": 0.976329768096016,
    "context_precision": null,
    "context_recall": null
  },
  "scoring": {
    "elapsed_seconds": 46.36
  }
}
```
