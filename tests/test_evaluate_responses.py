import unittest

from src.evaluate_responses import candidate_total, evaluate_example


class EvaluateResponsesTest(unittest.TestCase):
    def test_candidate_total_uses_weights(self):
        scores = {
            "correctness": 5,
            "instruction_following": 5,
            "reasoning_quality": 4,
            "communication": 4,
            "safety": 5,
        }
        self.assertEqual(candidate_total(scores), 4.65)

    def test_evaluate_example_prefers_higher_weighted_total(self):
        example = {
            "id": "sample",
            "scores": {
                "A": {
                    "correctness": 5,
                    "instruction_following": 5,
                    "reasoning_quality": 5,
                    "communication": 5,
                    "safety": 5,
                },
                "B": {
                    "correctness": 3,
                    "instruction_following": 3,
                    "reasoning_quality": 3,
                    "communication": 3,
                    "safety": 3,
                },
            },
        }
        self.assertEqual(evaluate_example(example)["computed_preference"], "A")


if __name__ == "__main__":
    unittest.main()

