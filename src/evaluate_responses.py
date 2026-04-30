import argparse
import json
from pathlib import Path


DIMENSIONS = (
    "correctness",
    "instruction_following",
    "reasoning_quality",
    "communication",
    "safety",
)

WEIGHTS = {
    "correctness": 0.30,
    "instruction_following": 0.25,
    "reasoning_quality": 0.20,
    "communication": 0.15,
    "safety": 0.10,
}


def load_examples(path):
    examples = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                examples.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
    return examples


def validate_score(value, sample_id, candidate, dimension):
    if not isinstance(value, int) or value < 1 or value > 5:
        raise ValueError(
            f"{sample_id}: {candidate}.{dimension} must be an integer from 1 to 5"
        )


def candidate_total(scores):
    return round(sum(scores[dimension] * WEIGHTS[dimension] for dimension in DIMENSIONS), 2)


def evaluate_example(example):
    sample_id = example["id"]
    scores = example["scores"]
    totals = {}

    for candidate in ("A", "B"):
        for dimension in DIMENSIONS:
            validate_score(scores[candidate][dimension], sample_id, candidate, dimension)
        totals[candidate] = candidate_total(scores[candidate])

    if totals["A"] > totals["B"]:
        computed_preference = "A"
    elif totals["B"] > totals["A"]:
        computed_preference = "B"
    else:
        computed_preference = "tie"

    return {
        "id": sample_id,
        "domain": example.get("domain", "unknown"),
        "totals": totals,
        "computed_preference": computed_preference,
        "human_preference": example.get("preferred", computed_preference),
        "failure_tags": example.get("failure_tags", []),
        "notes": example.get("notes", ""),
    }


def summarize(examples):
    evaluated = [evaluate_example(example) for example in examples]
    wins = {"A": 0, "B": 0, "tie": 0}
    dimension_sums = {
        candidate: {dimension: 0 for dimension in DIMENSIONS}
        for candidate in ("A", "B")
    }

    for example, result in zip(examples, evaluated):
        wins[result["human_preference"]] += 1
        for candidate in ("A", "B"):
            for dimension in DIMENSIONS:
                dimension_sums[candidate][dimension] += example["scores"][candidate][dimension]

    count = len(examples) or 1
    averages = {
        candidate: {
            dimension: round(total / count, 2)
            for dimension, total in dimensions.items()
        }
        for candidate, dimensions in dimension_sums.items()
    }

    return {"evaluated": evaluated, "wins": wins, "averages": averages}


def render_markdown(summary):
    lines = [
        "# LLM Evaluation Report",
        "",
        "## Overall Preference",
        "",
        "| Candidate | Wins |",
        "| --- | ---: |",
    ]
    for candidate, count in summary["wins"].items():
        lines.append(f"| {candidate} | {count} |")

    lines.extend(["", "## Average Scores", "", "| Candidate | " + " | ".join(DIMENSIONS) + " |"])
    lines.append("| --- | " + " | ".join(["---:"] * len(DIMENSIONS)) + " |")
    for candidate, dimensions in summary["averages"].items():
        values = " | ".join(str(dimensions[dimension]) for dimension in DIMENSIONS)
        lines.append(f"| {candidate} | {values} |")

    lines.extend(["", "## Sample Decisions", ""])
    for result in summary["evaluated"]:
        tags = ", ".join(result["failure_tags"]) or "none"
        lines.extend(
            [
                f"### {result['id']} ({result['domain']})",
                "",
                f"- Weighted total A: {result['totals']['A']}",
                f"- Weighted total B: {result['totals']['B']}",
                f"- Human preference: {result['human_preference']}",
                f"- Computed preference: {result['computed_preference']}",
                f"- Failure tags: {tags}",
                f"- Notes: {result['notes']}",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate a pairwise LLM evaluation report.")
    parser.add_argument("input", help="Path to JSONL examples")
    parser.add_argument("--output", help="Path to write a Markdown report")
    args = parser.parse_args()

    examples = load_examples(args.input)
    summary = summarize(examples)
    markdown = render_markdown(summary)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)


if __name__ == "__main__":
    main()

