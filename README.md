# LLM Evaluation Lab

Human-in-the-loop evaluation templates and lightweight tooling for comparing LLM responses.

This repository shows the kind of work used in RLHF and LLM quality workflows: prompt design, rubric-based scoring, pairwise response comparison, failure-mode tagging, and evaluation reporting.

## Why This Exists

LLM evaluation is not just asking "which answer sounds better." Good evaluation needs:

- Clear task instructions
- A repeatable rubric
- Side-by-side response comparison
- Ground-truth or reference reasoning when available
- Failure-mode labels that help improve prompts, models, and datasets

This repo keeps those pieces small, inspectable, and easy to adapt.

## What Is Included

```text
.
|-- data/
|   `-- examples.jsonl
|-- reports/
|   `-- sample_report.md
|-- rubrics/
|   `-- rlhf_response_rubric.md
|-- src/
|   `-- evaluate_responses.py
|-- tests/
|   `-- test_evaluate_responses.py
|-- README.md
`-- requirements.txt
```

## Evaluation Dimensions

Each candidate response is scored from 1 to 5 on:

- `correctness`: factual and technical accuracy
- `instruction_following`: how well the answer follows explicit user constraints
- `reasoning_quality`: clarity of reasoning and handling of edge cases
- `communication`: usefulness, concision, and structure
- `safety`: avoids harmful, misleading, or overconfident output

The evaluator then computes weighted totals and a preferred response for each sample.

## Quick Start

This project uses only the Python standard library.

```bash
python src/evaluate_responses.py data/examples.jsonl --output reports/sample_report.md
```

Run tests:

```bash
python -m unittest discover -s tests
```

## Example Output

The generated report includes:

- Overall win rate by candidate
- Average score by rubric dimension
- Per-sample winner
- Failure-mode tags
- Evaluator notes

See [reports/sample_report.md](reports/sample_report.md).

## Use Cases

- RLHF response comparison practice
- Prompt regression testing
- Data quality checks for AI training tasks
- Building a private evaluation set for an LLM app
- Creating review templates for human evaluators

## Notes

The sample data is synthetic and intentionally small. It is meant to demonstrate evaluation structure, not benchmark a real model.

