"""Backend evaluation script per 10_Testing/AI_Evaluation.md."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.ai_evaluation_service import (
    load_test_cases,
    evaluate_search as eval_search_fn,
)

TEST_CASES = load_test_cases()


def evaluate_search():
    """Execute search quality evaluation and print P@5 and MRR."""
    return eval_search_fn()


if __name__ == "__main__":
    evaluate_search()
