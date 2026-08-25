# StockForge Learning Loop Policy

**Updated:** 25 August 2026  
**Status:** Active operating contract

## 1. Division of responsibility

StockForge is the decision engine for a first-time microstock contributor. The user does not need to choose a niche, buyer segment, prompt, negative prompt, technical format, provider, category, keyword strategy, or finalization path. StockForge must choose those elements from explicit market evidence, buyer-job clarity, production readiness, compliance risk, cost, and prior reviewed outcomes.

The user remains the final human visual reviewer. The user’s useful input is intentionally simple: whether the image is visually good enough, whether the object is clear, whether the image looks useful, and whether the user wants to keep or reject it. The user is not expected to know Adobe policy, engineering terminology, keyword ranking mechanics, or marketplace demand analysis.

StockForge must never convert one attractive image into a claim of market demand, ranking, approval, or sales probability. A market signal, screenshot, catalogue count, expert opinion, internal visual score, submission outcome, and download outcome are different evidence types and must remain separated.

## 2. Generation as an experiment

Every generation is a bounded experiment, not an isolated file creation. Before a provider call, the engine freezes the following context into the execution lineage:

| Field | Required meaning |
|---|---|
| Market hypothesis | What evidence supports testing this niche; uncertainty must be explicit. |
| Buyer job | What the buyer is trying to communicate or accomplish. |
| Product contract | Subject, visual identity, composition, format, and excluded risks. |
| Provider context | Provider, model, version, seed, workflow hash, and execution identity. |
| Technical route | Preview format, final delivery format, technical gates, and export branch. |
| Metadata draft | Title, visual keywords, category candidates, GenAI status, and human-review requirements. |
| Review questions | The exact visual and commercial questions the result must answer. |

A generation may be technically successful and commercially weak. It may also be visually appealing but unsuitable for the selected buyer job. Both outcomes are valuable learning if they are recorded accurately.

## 3. What is learned after generation

After the user reviews a preview, StockForge records an evaluation tied to the immutable execution and artifact IDs. The evaluation covers visual quality, technical quality, buyer fit, metadata accuracy, decision, rejection reasons, and any explicitly known marketplace outcome. The current append-only ledger is `evaluations/generation_evaluations.jsonl`.

The machine may calculate deterministic signals such as decodability, dimensions, RGB/sRGB status, obvious image-quality defects, and local duplicate similarity. It must not pretend that those checks prove semantic correctness, engineering accuracy, legal clearance, buyer purchase intent, or marketplace acceptance. Human review remains required for those questions.

The evaluation command may store detailed scores, but the user does not need to invent them. The agent converts the user’s simple visual feedback plus the deterministic audit into a defensible record and explains the reason for any score or decision. If the evidence is insufficient, the record must say so instead of fabricating precision.

## 4. How prior results affect future decisions

The `portfolio learning-summary` command aggregates reviewed records by lane and buyer job. It produces a transparent recommendation:

| Recommendation | Meaning |
|---|---|
| `INSUFFICIENT_EVIDENCE` | One reviewed result is useful evidence but cannot establish a niche policy. |
| `REFINE_BRIEF` | A repeated weakness indicates that buyer job, composition, metadata, or art direction needs refinement. |
| `PAUSE_AND_RESEARCH` | Repeated rejection and weak buyer fit justify pausing the lane before spending more GPU cost. |
| `KEEP_AND_VALIDATE` | Reviews are strong enough to keep the hypothesis while seeking a materially distinct validation or explicit marketplace outcome. |
| `REVIEW_REQUIRED` | Evidence is mixed or incomplete; do not make a silent production change. |

These recommendations are decision support, not automatic generation permission. A future change to a prompt, niche, format, provider, or volume must cite the records that motivated it, be implemented as a tested change, and pass the relevant gates before another provider call.

The engine must not learn from a seed-only retry, crop-only variant, colour-only variant, duplicate submission, irrelevant keyword, or fabricated marketplace outcome. A new candidate is useful only when its buyer hypothesis or visual product is materially distinct.

## 5. Current rotor-armature learning record

The first successful internal trial produced a review-ready WebP preview, durable execution, artifact, and package. It is not yet a marketplace submission or master JPEG. The visual audit found strong recognizability and silhouette, but only moderate utility for manuals because the image is a polished conceptual object rather than an explanatory diagram. This result supports keeping the technical mechanical component lane as a promising hypothesis while narrowing the primary buyer job toward editorial technology illustration and conceptual electromechanical explainer visuals.

No automatic conclusion has been drawn about sales demand. The next decision should be based on the user’s review of the actual preview and the agent’s documented comparison against the buyer job and market evidence. No additional variant should be generated merely to search for a better-looking image.

## 6. Operational rule

> **StockForge decides what to make; the user judges what is visibly useful; the ledger records why; the next decision cites the record.**

This policy complements the append-only generation evaluation ledger, the evidence-bound niche shortlist, the format gates, and the manual marketplace submission contract.
