"""Evaluation CLI Script from 10_Testing/Testing_Strategy.md and AI_Evaluation.md."""

import argparse
import json
import logging
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.ai_evaluation_service import run_offline_search_evaluation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("memegpt.eval")


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate MemeGPT Search Quality")
    parser.add_argument("--test-file", type=str, default=None, help="Path to labeled test queries JSON")
    parser.add_argument("--k", nargs="+", type=int, default=[3, 5, 10], help="K cutoffs for precision/recall")
    parser.add_argument("--output", type=str, default=None, help="Output JSON report file")
    parser.add_argument("--live", action="store_true", help="Use live match_memes engine")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger.info(f"Running evaluation with k={args.k} (live_matcher={args.live})...")
    results = run_offline_search_evaluation(
        test_cases_file=args.test_file,
        use_live_matcher=args.live,
    )

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved evaluation report to {args.output}")

    summary = results["summary"]
    print("\n=======================================================")
    print("           MemeGPT AI Search Quality Evaluation        ")
    print("=======================================================")
    print(f"Total Test Cases Evaluated : {results['total_test_cases']}")
    print("-------------------------------------------------------")
    print(f"Precision@5   : {summary['precision_at_5']:.2%}  (Target >70%) -> {'[PASS]' if summary['precision_at_5_meets_target'] else '[FAIL]'}")
    print(f"Recall@10     : {summary['recall_at_10']:.2%}  (Target >85%) -> {'[PASS]' if summary['recall_at_10_meets_target'] else '[FAIL]'}")
    print(f"MRR           : {summary['mrr']:.2%}  (Target >80%) -> {'[PASS]' if summary['mrr_meets_target'] else '[FAIL]'}")
    print(f"NDCG@5        : {summary['ndcg_at_5']:.2%}  (Target >75%) -> {'[PASS]' if summary['ndcg_at_5_meets_target'] else '[FAIL]'}")
    print("=======================================================\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
