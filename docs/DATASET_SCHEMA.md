# Dataset Schema

Evaluation datasets are stored as JSONL: one JSON object per line.

## Required Fields

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Stable sample identifier |
| `prompt` | string | User prompt or task instruction |
| `scores` | object | Candidate scores keyed by `A` and `B` |
| `preferred` | string | Human preference: `A`, `B`, or `tie` |

## Recommended Fields

| Field | Type | Description |
| --- | --- | --- |
| `domain` | string | Task domain such as `python`, `data_science`, `safety` |
| `response_a` | string | Candidate A answer |
| `response_b` | string | Candidate B answer |
| `failure_tags` | array | Failure-mode labels from the rubric config |
| `notes` | string | Human evaluator rationale |
| `annotations` | array | Optional per-annotator labels for agreement tracking |

## Response Format Options

Short format:

```json
{
  "response_a": "Candidate A answer",
  "response_b": "Candidate B answer"
}
```

Structured format:

```json
{
  "responses": {
    "A": "Candidate A answer",
    "B": "Candidate B answer"
  }
}
```

## Score Format

Each candidate must have every rubric dimension:

```json
{
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
  }
}
```

The allowed score range and dimension names come from `configs/rlhf_rubric.json`.

## Annotation Format

Use `annotations` when multiple reviewers label the same example:

```json
{
  "annotations": [
    {
      "annotator": "reviewer_1",
      "preferred": "A",
      "confidence": 0.92,
      "failure_tags": ["missed_constraint"],
      "notes": "A follows the requested audience and example framing."
    },
    {
      "annotator": "reviewer_2",
      "preferred": "B",
      "confidence": 0.58,
      "failure_tags": ["poor_structure"],
      "notes": "B is shorter, but the judgment should be reviewed."
    }
  ]
}
```

Annotation-level fields:

| Field | Required | Description |
| --- | --- | --- |
| `annotator` | yes | Stable reviewer identifier |
| `preferred` | yes | Annotator preference: `A`, `B`, or `tie` |
| `confidence` | no | Reviewer confidence from `0` to `1` |
| `failure_tags` | no | Failure tags assigned by this annotator |
| `notes` | no | Annotator rationale |
| `scores` | no | Optional candidate scores using the same score format |

See [ANNOTATOR_AGREEMENT.md](ANNOTATOR_AGREEMENT.md) for agreement metrics.

## Validation

Run:

```bash
PYTHONPATH=src python -m eval_lab.cli --rubric configs/rlhf_rubric.json validate data/examples.jsonl
```

Validation checks:

- Duplicate sample IDs
- Missing candidate responses
- Missing dimension scores
- Scores outside the rubric range
- Invalid preference labels
- Unknown failure tags
- Invalid annotation preference labels
- Duplicate annotator IDs within a sample
- Annotation confidence values outside `0` to `1`
