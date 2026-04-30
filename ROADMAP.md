# Roadmap

This roadmap shows how the project can mature from a focused demo into a more production-like evaluation tool.

## Done

- JSONL pairwise evaluation dataset.
- Weighted rubric config.
- Dataset validation.
- Computed preference checks.
- Optional multi-annotator labels.
- Pairwise annotator agreement metrics.
- Disagreement-case reporting.
- Failure tag counts.
- Markdown and JSON reports.
- Unit-tested CLI.

## Next Improvements

1. Add more diverse sample cases across code, reasoning, safety, and factual QA.
2. Add CSV export for spreadsheet review.
3. Add report sections for disagreement patterns by rubric dimension.
4. Add reviewer calibration examples by domain.
5. Add review-queue export for low-agreement samples.

## Production Direction

- Store evaluator decisions with reviewer metadata.
- Support versioned rubric configs.
- Track model/version fields per candidate response.
- Add review queues for low-confidence or disagreement cases.
- Add dashboards for weekly quality trends.

## Non-Goals

- Calling live LLM APIs by default.
- Replacing human evaluators.
- Treating one numeric score as the full evaluation story.
