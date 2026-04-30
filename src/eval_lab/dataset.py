import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Annotation:
    annotator: str
    preferred: str
    scores: dict = field(default_factory=dict)
    failure_tags: tuple[str, ...] = ()
    notes: str = ""
    confidence: float | None = None


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
    annotations: tuple[Annotation, ...] = ()


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
        annotations=tuple(parse_annotation(annotation) for annotation in raw.get("annotations", ())),
    )


def parse_annotation(raw):
    return Annotation(
        annotator=raw.get("annotator", ""),
        preferred=raw.get("preferred", "tie"),
        scores=raw.get("scores", {}),
        failure_tags=tuple(raw.get("failure_tags", ())),
        notes=raw.get("notes", ""),
        confidence=raw.get("confidence"),
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

    seen_annotators = set()
    for index, annotation in enumerate(example.annotations, start=1):
        prefix = f"{example.sample_id}: annotations[{index}]"
        if not annotation.annotator:
            errors.append(f"{prefix}: annotator is required")
        elif annotation.annotator in seen_annotators:
            errors.append(f"{prefix}: duplicate annotator {annotation.annotator}")
        seen_annotators.add(annotation.annotator)

        if annotation.preferred not in rubric.allowed_preferences:
            errors.append(f"{prefix}: preferred must be one of {rubric.allowed_preferences}")

        if annotation.confidence is not None:
            if not isinstance(annotation.confidence, (int, float)):
                errors.append(f"{prefix}: confidence must be numeric")
            elif annotation.confidence < 0 or annotation.confidence > 1:
                errors.append(f"{prefix}: confidence must be between 0 and 1")

        unknown_annotation_tags = sorted(set(annotation.failure_tags) - set(rubric.failure_tags))
        if unknown_annotation_tags:
            errors.append(
                f"{prefix}: unknown failure tags: {', '.join(unknown_annotation_tags)}"
            )

        if annotation.scores:
            for candidate in ("A", "B"):
                if candidate not in annotation.scores:
                    errors.append(f"{prefix}: missing scores for candidate {candidate}")
                    continue
                for dimension in rubric.dimension_names:
                    value = annotation.scores[candidate].get(dimension)
                    if not isinstance(value, int):
                        errors.append(f"{prefix}: {candidate}.{dimension} must be an integer")
                    elif value < rubric.score_min or value > rubric.score_max:
                        errors.append(
                            f"{prefix}: {candidate}.{dimension} must be between "
                            f"{rubric.score_min} and {rubric.score_max}"
                        )

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
