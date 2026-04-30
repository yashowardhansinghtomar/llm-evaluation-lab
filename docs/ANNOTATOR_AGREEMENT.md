# Annotator Agreement

The dataset schema supports optional per-sample `annotations` so multiple reviewers can label the same pairwise example.

## Why This Exists

RLHF and LLM evaluation workflows need more than one final label. Teams often need to know:

- whether reviewers agree
- which samples should go to a review queue
- which annotator pairs disagree often
- whether disagreement is about preference, safety, correctness, or prompt constraints

This project keeps that workflow lightweight and inspectable.

## Annotation Shape

```json
{
  "annotator": "reviewer_1",
  "preferred": "A",
  "confidence": 0.92,
  "failure_tags": ["missed_constraint"],
  "notes": "A follows the requested audience and example framing."
}
```

Optional annotation-level `scores` can also be included using the same candidate/dimension structure as top-level `scores`.

## Metrics

The report computes:

- samples with annotations
- total annotations
- average annotations per sample
- overall pairwise agreement
- annotator-pair agreement
- disagreement case count
- per-sample majority preference
- per-sample preference counts

## Disagreement Logic

For each sample, the tool compares every annotator pair:

```text
reviewer_1 vs reviewer_2
reviewer_1 vs reviewer_3
reviewer_2 vs reviewer_3
```

If two annotators selected the same preference, that pair agrees. Otherwise, that pair disagrees.

The sample-level agreement rate is:

```text
agreeing pairs / total annotator pairs
```

## Review Queue Signal

Any sample with agreement below `1.0` is treated as a disagreement case in the report.

Disagreement does not automatically mean the majority label is wrong. It means the sample deserves review because at least one evaluator applied the rubric differently.

## Backward Compatibility

The `annotations` field is optional. Existing datasets with only top-level `preferred`, `scores`, and `failure_tags` still validate and report normally.
