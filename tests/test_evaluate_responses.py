import tempfile
import unittest
from pathlib import Path

from eval_lab.cli import main
from eval_lab.dataset import load_jsonl, validate_dataset
from eval_lab.rubric import load_rubric
from eval_lab.scoring import candidate_total, evaluate_example, summarize


ROOT = Path(__file__).resolve().parents[1]
RUBRIC_PATH = ROOT / "configs" / "rlhf_rubric.json"
DATA_PATH = ROOT / "data" / "examples.jsonl"


class EvaluateResponsesTest(unittest.TestCase):
    def setUp(self):
        self.rubric = load_rubric(RUBRIC_PATH)
        self.examples = load_jsonl(DATA_PATH)

    def test_dataset_passes_validation(self):
        self.assertEqual(validate_dataset(self.examples, self.rubric), [])

    def test_candidate_total_uses_configured_weights(self):
        scores = {
            "correctness": 5,
            "instruction_following": 5,
            "reasoning_quality": 4,
            "communication": 4,
            "safety": 5,
        }
        self.assertEqual(candidate_total(scores, self.rubric), 4.65)

    def test_evaluate_example_prefers_higher_weighted_total(self):
        result = evaluate_example(self.examples[0], self.rubric)
        self.assertEqual(result["computed_preference"], "A")
        self.assertTrue(result["agreement"])

    def test_summary_tracks_agreement_and_failure_tags(self):
        summary = summarize(self.examples, self.rubric)
        self.assertEqual(summary["sample_count"], 3)
        self.assertEqual(summary["agreement_rate"], 1.0)
        self.assertEqual(summary["failure_counts"]["missed_constraint"], 2)

    def test_cli_writes_markdown_and_json_reports(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            markdown = Path(tmp_dir) / "report.md"
            json_report = Path(tmp_dir) / "report.json"
            exit_code = main(
                [
                    "--rubric",
                    str(RUBRIC_PATH),
                    "report",
                    str(DATA_PATH),
                    "--markdown",
                    str(markdown),
                    "--json",
                    str(json_report),
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertIn("Domain Breakdown", markdown.read_text(encoding="utf-8"))
            self.assertIn("agreement_rate", json_report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

