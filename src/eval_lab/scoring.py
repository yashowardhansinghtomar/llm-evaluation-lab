from collections import Counter, defaultdict


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
    return {
        "id": example.sample_id,
        "domain": example.domain,
        "totals": totals,
        "margin": round(totals["A"] - totals["B"], 3),
        "computed_preference": computed,
        "human_preference": example.preferred,
        "agreement": computed == example.preferred,
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
        "evaluated": evaluated,
    }

