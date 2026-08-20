"""Offline AI Search Quality Evaluation CLI Script for MemeGPT.
Specification: 10_Testing/AI_Evaluation.md
"""

import sys
import logging

from app.services.ai_evaluation_service import (
    run_offline_search_evaluation,
    get_evaluation_metrics_catalog,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("memegpt.eval.search")


def main() -> int:
    """Execute evaluation against ground-truth dataset and display report."""
    logger.info("Starting offline search quality evaluation on benchmark dataset...")
    results = run_offline_search_evaluation()
    summary = results["summary"]

    print("\n=======================================================")
    print("           MemeGPT AI Search Quality Evaluation        ")
    print("=======================================================")
    print(f"Total Test Cases Evaluated : {results['total_test_cases']}")
    print("-------------------------------------------------------")
    print(f"Precision@5   : {summary['precision_at_5']:.2%}  (Target >70%) -> {'PASS ✅' if summary['precision_at_5_meets_target'] else 'FAIL ❌'}")
    print(f"Recall@10     : {summary['recall_at_10']:.2%}  (Target >85%) -> {'PASS ✅' if summary['recall_at_10_meets_target'] else 'FAIL ❌'}")
    print(f"MRR           : {summary['mrr']:.2%}  (Target >80%) -> {'PASS ✅' if summary['mrr_meets_target'] else 'FAIL ❌'}")
    print(f"NDCG@5        : {summary['ndcg_at_5']:.2%}  (Target >75%) -> {'PASS ✅' if summary['ndcg_at_5_meets_target'] else 'FAIL ❌'}")
    print("=======================================================\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
