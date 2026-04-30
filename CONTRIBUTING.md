# Contributing

This project is intentionally small and dependency-light. Contributions should keep the evaluation workflow easy to inspect.

## Local Setup

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

## Before Opening A PR

- Run the unit tests.
- Validate `data/examples.jsonl`.
- Regenerate the sample report if scoring or reporting changed.
- Keep new dependencies out unless they clearly improve the evaluation workflow.
- Add or update tests for scoring, validation, or report behavior.

## Good Contributions

- New evaluation failure tags with examples.
- Better dataset validation errors.
- Additional report breakdowns.
- More representative sample eval cases.
- Documentation that explains evaluator decisions more clearly.

## Style

- Prefer standard-library Python.
- Keep functions small and directly testable.
- Use explicit names for scoring and rubric concepts.
- Avoid hidden network calls or API-key requirements.
