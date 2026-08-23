"""Performance Tests Management Service for MemeGPT.
Specification: 10_Testing/Performance_Tests.md
"""

import logging
import time
from typing import Any, Dict, List

from app.rule_engine import run_rule_engine, detect_emotion
from app.semantic_search import embed_text
from app.services.smart_search_service import calculate_smart_search_composite_score

logger = logging.getLogger("memegpt.services.performance_tests")

COMPONENT_BENCHMARKS = [
    {
        "component": "MiniLM embedding",
        "target_latency": "<100ms",
        "target_ms": 100,
        "test_method": "Direct model.encode() / embed_text()",
    },
    {
        "component": "Emotion detection",
        "target_latency": "<150ms",
        "target_ms": 150,
        "test_method": "Direct pipeline() / detect_emotion()",
    },
    {
        "component": "Groq API call",
        "target_latency": "<500ms",
        "target_ms": 500,
        "test_method": "httpx.post() timing",
    },
    {
        "component": "Qdrant search",
        "target_latency": "<100ms",
        "target_ms": 100,
        "test_method": "client.search() timing",
    },
    {
        "component": "Re-ranking",
        "target_latency": "<20ms",
        "target_ms": 20,
        "test_method": "Pure Python timing",
    },
    {
        "component": "Redis GET",
        "target_latency": "<10ms",
        "target_ms": 10,
        "test_method": "cache.get() timing",
    },
    {
        "component": "Full pipeline",
        "target_latency": "<1.5s",
        "target_ms": 1500,
        "test_method": "End-to-end timing",
    },
]

PERFORMANCE_SUITE_COMMANDS = [
    {"command": "pytest tests/test_performance.py -v --tb=short", "description": "Run performance test suite with concise tracebacks"},
    {"command": "pytest tests/test_performance.py -v --durations=10", "description": "Run performance test suite with top 10 slowest test timings"},
]


def get_component_benchmarks() -> Dict[str, Any]:
    """Return the 7 component latency SLA benchmarks."""
    return {
        "total_components": len(COMPONENT_BENCHMARKS),
        "benchmarks": COMPONENT_BENCHMARKS,
    }


def get_performance_suite_commands() -> List[Dict[str, str]]:
    """Return standard performance test execution commands."""
    return PERFORMANCE_SUITE_COMMANDS


def benchmark_system_components() -> Dict[str, Any]:
    """Run live micro-benchmarks on in-process components and measure elapsed milliseconds."""
    results = {}

    # 1. MiniLM / Text Embedding
    t0 = time.perf_counter()
    embed_text("test sentence for performance benchmark")
    embed_ms = round((time.perf_counter() - t0) * 1000, 2)
    results["embedding_ms"] = {"observed": embed_ms, "target": "<100ms", "passed": embed_ms < 100.0}

    # 2. Emotion Detection
    t0 = time.perf_counter()
    detect_emotion("I am feeling great today")
    emo_ms = round((time.perf_counter() - t0) * 1000, 2)
    results["emotion_detection_ms"] = {"observed": emo_ms, "target": "<150ms", "passed": emo_ms < 150.0}

    # 3. Rule Engine
    t0 = time.perf_counter()
    run_rule_engine("Monday morning work panic")
    rule_ms = round((time.perf_counter() - t0) * 1000, 2)
    results["rule_engine_ms"] = {"observed": rule_ms, "target": "<20ms", "passed": rule_ms < 20.0}

    # 4. Re-ranking Composite Scoring (batch of 20 items)
    t0 = time.perf_counter()
    for _ in range(20):
        calculate_smart_search_composite_score(0.85, True, False, 0.7, True)
    rerank_ms = round((time.perf_counter() - t0) * 1000, 2)
    results["rerank_batch_ms"] = {"observed": rerank_ms, "target": "<20ms", "passed": rerank_ms < 20.0}

    all_passed = all(v["passed"] for v in results.values())
    return {
        "status": "PASS" if all_passed else "WARNING",
        "benchmarks": results,
    }
