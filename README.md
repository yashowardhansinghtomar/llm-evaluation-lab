# LLM Evaluation Lab

A small, config-driven workbench for human-in-the-loop LLM response evaluation.

This project models the core pieces used in RLHF and LLM quality workflows: rubric design, pairwise response comparison, dataset validation, failure-mode tagging, computed preference checks, and report generation.

## Why This Exists

LLM evaluation is not just asking which answer sounds better. Good evaluation needs:

- Clear task instructions
- A repeatable rubric
- Side-by-side response comparison
- Human preference labels
- Weighted scoring by quality dimension
- Failure-mode tags that can improve prompts, model behavior, and datasets
- Reports that expose disagreement and weak spots

## Features

- JSON rubric config with weighted dimensions
- JSONL evaluation dataset format
- Dataset validation before scoring
- Pairwise scoring for candidate `A` and candidate `B`
- Computed-vs-human preference agreement
- Domain-level breakdowns
- Failure-tag counts
- Markdown and JSON report output
- Unit tests for scoring, validation, and CLI behavior

## Project Structure

```text
.
|-- configs/
|   `-- rlhf_rubric.json
|-- data/
|   `-- examples.jsonl
|-- docs/
|   `-- DATASET_SCHEMA.md
|-- reports/
|   |-- sample_report.json
|   `-- sample_report.md
|-- rubrics/
|   `-- rlhf_response_rubric.md
|-- src/
|   |-- eval_lab/
|   |   |-- cli.py
|   |   |-- dataset.py
|   |   |-- reporting.py
|   |   |-- rubric.py
|   |   `-- scoring.py
|   `-- evaluate_responses.py
|-- tests/
|   `-- test_evaluate_responses.py
|-- LICENSE
|-- pyproject.toml
|-- README.md
`-- requirements.txt
```

## Dataset Format

Each JSONL row contains one pairwise evaluation example:

```json
{
  "id": "python-001",
  "domain": "python",
  "prompt": "Write a Python function...",
  "response_a": "candidate answer A",
  "response_b": "candidate answer B",
  "scores": {
    "A": {
      "correctness": 5,
      "instruction_following": 5,
      "reasoning_quality": 4,
      "communication": 4,
      "safety": 5
    },
    "B": {
      "correctness": 2,
      "instruction_following": 2,
      "reasoning_quality": 1,
      "communication": 3,
      "safety": 4
    }
  },
  "preferred": "A",
  "failure_tags": ["code_bug", "missed_constraint"],
  "notes": "Response B fails on duplicate values."
}
```

See [docs/DATASET_SCHEMA.md](docs/DATASET_SCHEMA.md) for the full schema and validation rules.

## Quick Start

This project uses only the Python standard library.

Validate the dataset:

```bash
PYTHONPATH=src python -m eval_lab.cli --rubric configs/rlhf_rubric.json validate data/examples.jsonl
```

Generate reports:

```bash
PYTHONPATH=src python -m eval_lab.cli --rubric configs/rlhf_rubric.json report data/examples.jsonl --markdown reports/sample_report.md --json reports/sample_report.json
```

Compatibility wrapper:

```bash
PYTHONPATH=src python src/evaluate_responses.py --rubric configs/rlhf_rubric.json report data/examples.jsonl
```

Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

Install as a local CLI:

```bash
pip install -e .
llm-eval-lab --rubric configs/rlhf_rubric.json validate data/examples.jsonl
```

## What The Report Shows

- Human preference distribution
- Computed preference distribution
- Computed-vs-human agreement rate
- Average candidate scores by dimension
- Domain-level agreement
- Failure-tag counts
- Per-sample margins and notes

See:

- [reports/sample_report.md](reports/sample_report.md)
- [reports/sample_report.json](reports/sample_report.json)

## Use Cases

- RLHF response comparison practice
- Prompt regression testing
- Human evaluator training
- Private eval set reporting
- Failure-mode analysis for LLM apps
- Lightweight model-output QA before building a larger evaluation pipeline

## Notes

The sample data is synthetic and intentionally small. It demonstrates evaluation structure, not model benchmark performance.
