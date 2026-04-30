from collections import Counter, defaultdict
from itertools import combinations


def candidate_total(scores, rubric):
    return round(
        sum(scores[dimension.name] * dimension.weight for dimension in rubric.dimensions),
        3,
    )


def computed_preference(totals, tie_threshold=0.0):
    margin = totals["A"] - totals["B"]
    if abs(margin) <= tie_threshold:
        return "tie"
    return "A" if margin > 0 else "B"


def evaluate_example(example, rubric, tie_threshold=0.0):
    totals = {
        "A": candidate_total(example.scores["A"], rubric),
        "B": candidate_total(example.scores["B"], rubric),
    }
    computed = computed_preference(totals, tie_threshold=tie_threshold)
    annotation_summary = summarize_example_annotations(example)
    return {
        "id": example.sample_id,
        "domain": example.domain,
        "totals": totals,
        "margin": round(totals["A"] - totals["B"], 3),
        "computed_preference": computed,
        "human_preference": example.preferred,
        "agreement": computed == example.preferred,
        "annotation_summary": annotation_summary,
        "failure_tags": list(example.failure_tags),
        "notes": example.notes,
    }


def summarize(examples, rubric, tie_threshold=0.0):
    evaluated = [evaluate_example(example, rubric, tie_threshold) for example in examples]
    wins = Counter(result["human_preference"] for result in evaluated)
    computed_wins = Counter(result["computed_preference"] for result in evaluated)
    failure_counts = Counter(tag for example in examples for tag in example.failure_tags)
    domain_counts = Counter(example.domain for example in examples)
    domain_agreement = defaultdict(lambda: {"agree": 0, "total": 0})

    dimension_sums = {
        candidate: {dimension.name: 0 for dimension in rubric.dimensions}
        for candidate in ("A", "B")
    }

    for example, result in zip(examples, evaluated):
        domain_agreement[example.domain]["total"] += 1
        if result["agreement"]:
            domain_agreement[example.domain]["agree"] += 1

        for candidate in ("A", "B"):
            for dimension in rubric.dimensions:
                dimension_sums[candidate][dimension.name] += example.scores[candidate][dimension.name]

    count = len(examples) or 1
    averages = {
        candidate: {
            dimension: round(total / count, 2)
            for dimension, total in dimensions.items()
        }
        for candidate, dimensions in dimension_sums.items()
    }

    agreement_count = sum(1 for result in evaluated if result["agreement"])
    domain_summary = {
        domain: {
            "samples": domain_counts[domain],
            "agreement_rate": round(
                domain_agreement[domain]["agree"] / domain_agreement[domain]["total"],
                3,
            ),
        }
        for domain in sorted(domain_counts)
    }

    return {
        "rubric": rubric.name,
        "sample_count": len(examples),
        "human_preference_wins": {key: wins.get(key, 0) for key in ("A", "B", "tie")},
        "computed_preference_wins": {key: computed_wins.get(key, 0) for key in ("A", "B", "tie")},
        "agreement_rate": round(agreement_count / count, 3),
        "average_scores": averages,
        "failure_counts": dict(sorted(failure_counts.items())),
        "domain_summary": domain_summary,
        "multi_annotator": summarize_annotator_agreement(examples),
        "evaluated": evaluated,
    }


def summarize_example_annotations(example):
    annotations = list(example.annotations)
    preference_counts = Counter(annotation.preferred for annotation in annotations)
    pair_count = 0
    agreeing_pairs = 0

    for first, second in combinations(annotations, 2):
        pair_count += 1
        if first.preferred == second.preferred:
            agreeing_pairs += 1

    agreement_rate = round(agreeing_pairs / pair_count, 3) if pair_count else None
    majority_preference = _majority_preference(preference_counts)

    return {
        "annotation_count": len(annotations),
        "preference_counts": {key: preference_counts.get(key, 0) for key in ("A", "B", "tie")},
        "majority_preference": majority_preference,
        "agreement_rate": agreement_rate,
        "disagreement": agreement_rate is not None and agreement_rate < 1,
        "annotations": [
            {
                "annotator": annotation.annotator,
                "preferred": annotation.preferred,
                "failure_tags": list(annotation.failure_tags),
                "confidence": annotation.confidence,
                "notes": annotation.notes,
            }
            for annotation in annotations
        ],
    }


def summarize_annotator_agreement(examples):
    annotated_examples = [example for example in examples if example.annotations]
    pair_counts = defaultdict(lambda: {"compared": 0, "agreements": 0})
    annotator_preference_counts = defaultdict(Counter)
    total_pairs = 0
    agreeing_pairs = 0
    disagreement_cases = []

    for example in annotated_examples:
        summary = summarize_example_annotations(example)
        if summary["disagreement"]:
            disagreement_cases.append(
                {
                    "id": example.sample_id,
                    "domain": example.domain,
                    "preference_counts": summary["preference_counts"],
                    "majority_preference": summary["majority_preference"],
                    "agreement_rate": summary["agreement_rate"],
                }
            )

        for annotation in example.annotations:
            annotator_preference_counts[annotation.annotator][annotation.preferred] += 1

        for first, second in combinations(example.annotations, 2):
            pair_key = " vs ".join(sorted([first.annotator, second.annotator]))
            pair_counts[pair_key]["compared"] += 1
            total_pairs += 1
            if first.preferred == second.preferred:
                pair_counts[pair_key]["agreements"] += 1
                agreeing_pairs += 1

    return {
        "samples_with_annotations": len(annotated_examples),
        "total_annotations": sum(len(example.annotations) for example in annotated_examples),
        "average_annotations_per_sample": round(
            sum(len(example.annotations) for example in annotated_examples)
            / len(annotated_examples),
            3,
        )
        if annotated_examples
        else 0,
        "overall_pairwise_agreement": round(agreeing_pairs / total_pairs, 3)
        if total_pairs
        else None,
        "disagreement_case_count": len(disagreement_cases),
        "annotator_preference_counts": {
            annotator: {key: counts.get(key, 0) for key in ("A", "B", "tie")}
            for annotator, counts in sorted(annotator_preference_counts.items())
        },
        "annotator_pair_agreement": {
            pair: {
                "compared": counts["compared"],
                "agreements": counts["agreements"],
                "agreement_rate": round(counts["agreements"] / counts["compared"], 3)
                if counts["compared"]
                else None,
            }
            for pair, counts in sorted(pair_counts.items())
        },
        "disagreement_cases": disagreement_cases,
    }


def _majority_preference(preference_counts):
    if not preference_counts:
        return None
    ordered = preference_counts.most_common()
    if len(ordered) > 1 and ordered[0][1] == ordered[1][1]:
        return "tie"
    return ordered[0][0]
