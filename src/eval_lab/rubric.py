import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Dimension:
    name: str
    weight: float
    description: str = ""


@dataclass(frozen=True)
class Rubric:
    name: str
    score_min: int
    score_max: int
    dimensions: tuple[Dimension, ...]
    allowed_preferences: tuple[str, ...]
    failure_tags: tuple[str, ...]

    @property
    def dimension_names(self):
        return tuple(dimension.name for dimension in self.dimensions)

    @property
    def weights(self):
        return {dimension.name: dimension.weight for dimension in self.dimensions}


def load_rubric(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    dimensions = tuple(
        Dimension(
            name=name,
            weight=float(config["weight"]),
            description=config.get("description", ""),
        )
        for name, config in raw["dimensions"].items()
    )
    rubric = Rubric(
        name=raw["name"],
        score_min=int(raw.get("score_min", 1)),
        score_max=int(raw.get("score_max", 5)),
        dimensions=dimensions,
        allowed_preferences=tuple(raw.get("allowed_preferences", ("A", "B", "tie"))),
        failure_tags=tuple(raw.get("failure_tags", ())),
    )
    validate_rubric(rubric)
    return rubric


def validate_rubric(rubric):
    if rubric.score_min >= rubric.score_max:
        raise ValueError("rubric score_min must be smaller than score_max")

    total_weight = round(sum(dimension.weight for dimension in rubric.dimensions), 8)
    if total_weight != 1:
        raise ValueError(f"rubric weights must sum to 1.0; got {total_weight}")

    if set(rubric.allowed_preferences) != {"A", "B", "tie"}:
        raise ValueError("allowed_preferences must contain A, B, and tie")

