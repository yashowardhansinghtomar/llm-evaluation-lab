import argparse
from pathlib import Path

from eval_lab.dataset import load_jsonl, validate_dataset
from eval_lab.reporting import render_json, render_markdown
from eval_lab.rubric import load_rubric
from eval_lab.scoring import summarize


def command_validate(args):
    rubric = load_rubric(args.rubric)
    examples = load_jsonl(args.input)
    errors = validate_dataset(examples, rubric)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {len(examples)} examples passed validation")
    return 0


def command_report(args):
    rubric = load_rubric(args.rubric)
    examples = load_jsonl(args.input)
    errors = validate_dataset(examples, rubric)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    summary = summarize(examples, rubric, tie_threshold=args.tie_threshold)

    if args.markdown:
        markdown_path = Path(args.markdown)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_markdown(summary, rubric), encoding="utf-8")

    if args.json:
        json_path = Path(args.json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(render_json(summary), encoding="utf-8")

    if not args.markdown and not args.json:
        print(render_markdown(summary, rubric))

    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Rubric-based pairwise LLM evaluation tools.")
    parser.add_argument(
        "--rubric",
        default="configs/rlhf_rubric.json",
        help="Path to rubric JSON config",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a JSONL evaluation dataset")
    validate.add_argument("input", help="Path to JSONL examples")
    validate.set_defaults(func=command_validate)

    report = subparsers.add_parser("report", help="Generate evaluation reports")
    report.add_argument("input", help="Path to JSONL examples")
    report.add_argument("--markdown", help="Path to write Markdown report")
    report.add_argument("--json", help="Path to write JSON summary")
    report.add_argument(
        "--tie-threshold",
        type=float,
        default=0.0,
        help="Treat weighted-score margins at or below this value as ties",
    )
    report.set_defaults(func=command_report)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

