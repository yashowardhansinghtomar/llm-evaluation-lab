import json


def render_json(summary):
    return json.dumps(summary, indent=2, sort_keys=True) + "\n"


def render_markdown(summary, rubric):
    dimensions = rubric.dimension_names
    lines = [
        "# LLM Evaluation Report",
        "",
        f"Rubric: `{summary['rubric']}`",
        f"Samples: `{summary['sample_count']}`",
        f"Computed vs human preference agreement: `{summary['agreement_rate']}`",
        "",
        "## Preference Summary",
        "",
        "| Preference | Human labels | Computed labels |",
        "| --- | ---: | ---: |",
    ]
    for preference in ("A", "B", "tie"):
        lines.append(
            f"| {preference} | {summary['human_preference_wins'][preference]} | "
            f"{summary['computed_preference_wins'][preference]} |"
        )

    lines.extend(["", "## Average Scores", ""])
    lines.append("| Candidate | " + " | ".join(dimensions) + " |")
    lines.append("| --- | " + " | ".join(["---:"] * len(dimensions)) + " |")
    for candidate, scores in summary["average_scores"].items():
        values = " | ".join(str(scores[dimension]) for dimension in dimensions)
        lines.append(f"| {candidate} | {values} |")

    lines.extend(["", "## Domain Breakdown", "", "| Domain | Samples | Agreement rate |"])
    lines.append("| --- | ---: | ---: |")
    for domain, data in summary["domain_summary"].items():
        lines.append(f"| {domain} | {data['samples']} | {data['agreement_rate']} |")

    multi = summary.get("multi_annotator", {})
    lines.extend(
        [
            "",
            "## Multi-Annotator Agreement",
            "",
            f"Samples with annotations: `{multi.get('samples_with_annotations', 0)}`",
            f"Total annotations: `{multi.get('total_annotations', 0)}`",
            f"Average annotations per sample: `{multi.get('average_annotations_per_sample', 0)}`",
            f"Overall pairwise agreement: `{multi.get('overall_pairwise_agreement')}`",
            f"Disagreement cases: `{multi.get('disagreement_case_count', 0)}`",
            "",
            "### Annotator Pair Agreement",
            "",
        ]
    )
    pair_agreement = multi.get("annotator_pair_agreement", {})
    if pair_agreement:
        lines.extend(["| Annotator Pair | Compared | Agreements | Agreement Rate |", "| --- | ---: | ---: | ---: |"])
        for pair, data in pair_agreement.items():
            lines.append(
                f"| {pair} | {data['compared']} | {data['agreements']} | {data['agreement_rate']} |"
            )
    else:
        lines.append("No annotator pairs available.")

    lines.extend(["", "### Disagreement Cases", ""])
    disagreement_cases = multi.get("disagreement_cases", [])
    if disagreement_cases:
        lines.extend(["| Sample | Domain | Majority | Agreement Rate | Preference Counts |", "| --- | --- | --- | ---: | --- |"])
        for case in disagreement_cases:
            counts = case["preference_counts"]
            count_text = f"A={counts['A']}, B={counts['B']}, tie={counts['tie']}"
            lines.append(
                f"| {case['id']} | {case['domain']} | {case['majority_preference']} | "
                f"{case['agreement_rate']} | {count_text} |"
            )
    else:
        lines.append("No disagreement cases.")

    lines.extend(["", "## Failure Tags", "", "| Tag | Count |"])
    lines.append("| --- | ---: |")
    if summary["failure_counts"]:
        for tag, count in summary["failure_counts"].items():
            lines.append(f"| {tag} | {count} |")
    else:
        lines.append("| none | 0 |")

    lines.extend(["", "## Sample Decisions", ""])
    for result in summary["evaluated"]:
        tags = ", ".join(result["failure_tags"]) or "none"
        lines.extend(
            [
                f"### {result['id']} ({result['domain']})",
                "",
                f"- Weighted total A: {result['totals']['A']}",
                f"- Weighted total B: {result['totals']['B']}",
                f"- Margin A-B: {result['margin']}",
                f"- Human preference: {result['human_preference']}",
                f"- Computed preference: {result['computed_preference']}",
                f"- Agreement: {result['agreement']}",
                f"- Annotators: {result['annotation_summary']['annotation_count']}",
                f"- Annotation majority: {result['annotation_summary']['majority_preference']}",
                f"- Annotation agreement rate: {result['annotation_summary']['agreement_rate']}",
                f"- Failure tags: {tags}",
                f"- Notes: {result['notes']}",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"
