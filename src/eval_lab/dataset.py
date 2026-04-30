import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvaluationExample:
    sample_id: str
    domain: str
    prompt: str
    responses: dict
    scores: dict
    preferred: str
    failure_tags: tuple[str, ...]
    notes: str


def load_jsonl(path):
    examples = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
            examples.append(parse_example(raw, line_number))
    return examples


def parse_example(raw, line_number=None):
    sample_id = raw.get("id")
    if not sample_id:
        location = f" on line {line_number}" if line_number else ""
        raise ValueError(f"example{location} is missing id")

    responses = raw.get("responses")
    if responses is None:
        responses = {
            "A": raw.get("response_a", ""),
            "B": raw.get("response_b", ""),
        }

    return EvaluationExample(
        sample_id=sample_id,
        domain=raw.get("domain", "unknown"),
        prompt=raw.get("prompt", ""),
        responses=responses,
        scores=raw.get("scores", {}),
        preferred=raw.get("preferred", "tie"),
        failure_tags=tuple(raw.get("failure_tags", ())),
        notes=raw.get("notes", ""),
    )


def validate_example(example, rubric):
    errors = []

    for candidate in ("A", "B"):
        if not example.responses.get(candidate):
            errors.append(f"{example.sample_id}: missing response {candidate}")
        if candidate not in example.scores:
            errors.append(f"{example.sample_id}: missing scores for candidate {candidate}")
            continue

        for dimension in rubric.dimension_names:
            value = example.scores[candidate].get(dimension)
            if not isinstance(value, int):
                errors.append(f"{example.sample_id}: {candidate}.{dimension} must be an integer")
            elif value < rubric.score_min or value > rubric.score_max:
                errors.append(
                    f"{example.sample_id}: {candidate}.{dimension} must be between "
                    f"{rubric.score_min} and {rubric.score_max}"
                )

    if example.preferred not in rubric.allowed_preferences:
        errors.append(f"{example.sample_id}: preferred must be one of {rubric.allowed_preferences}")

    unknown_tags = sorted(set(example.failure_tags) - set(rubric.failure_tags))
    if unknown_tags:
        errors.append(f"{example.sample_id}: unknown failure tags: {', '.join(unknown_tags)}")

    return errors


def validate_dataset(examples, rubric):
    errors = []
    seen_ids = set()
    for example in examples:
        if example.sample_id in seen_ids:
            errors.append(f"{example.sample_id}: duplicate id")
        seen_ids.add(example.sample_id)
        errors.extend(validate_example(example, rubric))
    return errors

