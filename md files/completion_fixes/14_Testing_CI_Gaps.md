# 14 — Testing & CI Pipeline Gaps Guide
> Close testing gaps across Frontend, Mobile, AI Evaluation, and automated latency benchmarking.

---

## Problem Statement

While the backend has 134 test files, the project has notable gaps in:
1. **Frontend Testing**: Vitest and React Testing Library tests for search inputs, meme cards, and theme switching.
2. **Mobile Testing**: Component and hook testing for `apps/mobile/`.
3. **AI Search Evaluation**: Automated computation of Precision@3, NDCG@5, and Mean Reciprocal Rank (MRR) on a standardized query test set.
4. **Latency Benchmarking**: Automated P50/P95 latency thresholds in CI to prevent performance regressions.

---

## Step 1: Frontend Unit & Component Testing (`frontend/`)

### 1.1 Install Testing Dependencies in `frontend/`

```powershell
cd "d:\Meme GPT\frontend"
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

### 1.2 Configure `frontend/vitest.config.ts`

**File:** `frontend/vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/tests/setup.ts'],
  },
});
```

### 1.3 Create `frontend/src/tests/setup.ts`

**File:** `frontend/src/tests/setup.ts`

```typescript
import '@testing-library/jest-dom';

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockImplementation(() => Promise.resolve()),
  },
});

// Mock matchMedia for dark mode
window.matchMedia = vi.fn().mockImplementation((query) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(),
  removeListener: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}));
```

### 1.4 Write Search Component Test: `frontend/src/tests/SearchInput.test.tsx`

**File:** `frontend/src/tests/SearchInput.test.tsx`

```tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import SearchInput from '../components/SearchInput';

describe('SearchInput Component', () => {
  it('renders input field with placeholder', () => {
    const onSearch = vi.fn();
    render(<SearchInput onSearch={onSearch} loading={false} />);
    
    const input = screen.getByPlaceholderText(/describe a feeling/i);
    expect(input).toBeInTheDocument();
  });

  it('triggers search callback when submit button is clicked', () => {
    const onSearch = vi.fn();
    render(<SearchInput onSearch={onSearch} loading={false} />);
    
    const input = screen.getByPlaceholderText(/describe a feeling/i);
    fireEvent.change(input, { target: { value: 'when tests pass first try' } });
    
    const submitBtn = screen.getByRole('button', { name: /search/i });
    fireEvent.click(submitBtn);
    
    expect(onSearch).toHaveBeenCalledWith('when tests pass first try');
  });

  it('disables input when loading state is true', () => {
    render(<SearchInput onSearch={vi.fn()} loading={true} />);
    const input = screen.getByPlaceholderText(/describe a feeling/i);
    expect(input).toBeDisabled();
  });
});
```

---

## Step 2: Automated AI Evaluation Pipeline

### 2.1 Golden Test Dataset (`data/eval/golden_queries.json`)

**File:** `data/eval/golden_queries.json`

```json
[
  {
    "query": "when code works on first try and you don't know why",
    "expected_slugs": ["confused-math-lady", "success-kid", "it-works-why"],
    "intent_emotion": "surprise"
  },
  {
    "query": "boss emails at 11pm on Friday night",
    "expected_slugs": ["this-is-fine", "stressed-michael-scott", "disappointed-face"],
    "intent_emotion": "frustration"
  },
  {
    "query": "staying up until 3am playing video games with friends",
    "expected_slugs": ["me-and-the-boys", "sleepy-squidward", "gamer-rage"],
    "intent_emotion": "joy"
  }
]
```

### 2.2 Evaluation Metric Script (`scripts/evaluate_ai_search.py`)

**File:** `scripts/evaluate_ai_search.py`

```python
"""
MemeGPT AI Recommendation Quality Evaluator
Computes Precision@3, NDCG@5, and Mean Reciprocal Rank (MRR).
"""
import json
import httpx
import math
from pathlib import Path

API_URL = "http://localhost:8000/api/v1/search"
TEST_SET = Path("data/eval/golden_queries.json")

def compute_reciprocal_rank(retrieved_slugs, expected_slugs):
    for rank, slug in enumerate(retrieved_slugs, start=1):
        if slug in expected_slugs:
            return 1.0 / rank
    return 0.0

def compute_precision_at_k(retrieved_slugs, expected_slugs, k=3):
    top_k = retrieved_slugs[:k]
    hits = sum(1 for s in top_k if s in expected_slugs)
    return hits / k

def compute_dcg(retrieved_slugs, expected_slugs, k=5):
    dcg = 0.0
    for i, slug in enumerate(retrieved_slugs[:k]):
        rel = 1.0 if slug in expected_slugs else 0.0
        dcg += (2**rel - 1) / math.log2(i + 2)
    return dcg

def evaluate():
    with open(TEST_SET) as f:
        cases = json.load(f)

    p3_scores, mrr_scores, ndcg_scores = [], [], []

    with httpx.Client(timeout=10.0) as client:
        for case in cases:
            query = case["query"]
            expected = set(case["expected_slugs"])
            resp = client.post(API_URL, json={"query": query, "limit": 5})
            if resp.status_code != 200:
                print(f"Error querying '{query}': {resp.status_code}")
                continue

            results = resp.json().get("memes", [])
            retrieved = [m["slug"] for m in results]

            p3 = compute_precision_at_k(retrieved, expected, k=3)
            mrr = compute_reciprocal_rank(retrieved, expected)
            dcg = compute_dcg(retrieved, expected, k=5)
            # Ideal DCG for 1 hit in top 5
            idcg = (2**1 - 1) / math.log2(2)
            ndcg = min(1.0, dcg / idcg) if idcg > 0 else 0.0

            p3_scores.append(p3)
            mrr_scores.append(mrr)
            ndcg_scores.append(ndcg)

    mean_p3 = sum(p3_scores) / len(p3_scores) if p3_scores else 0.0
    mean_mrr = sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0.0
    mean_ndcg = sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0

    print("=" * 40)
    print("MemeGPT AI Recommendation Quality Benchmark")
    print("=" * 40)
    print(f"Precision@3: {mean_p3:.3f} (Target: > 0.650)")
    print(f"NDCG@5:      {mean_ndcg:.3f} (Target: > 0.700)")
    print(f"MRR:         {mean_mrr:.3f} (Target: > 0.600)")
    print("=" * 40)

    # Return exit code for CI pipeline
    assert mean_p3 >= 0.50, f"Precision@3 {mean_p3} below minimum bar 0.50"

if __name__ == "__main__":
    evaluate()
```

---

## Step 3: Latency Benchmarking Script in CI

**File:** `scripts/benchmark_latency.py`

```python
"""
Automated Latency Benchmark Check
Ensures P50 < 1.5s and P95 < 3.0s under simulated sequential requests.
"""
import time
import httpx
import numpy as np

API_URL = "http://localhost:8000/api/v1/search"
QUERIES = [
    "when code compiles with no warnings",
    "monday morning meeting that could have been an email",
    "me pretending to listen to someone explain crypto",
    "when the food delivery finally arrives",
    "looking at my bank account after the weekend",
]

def benchmark():
    latencies = []
    with httpx.Client(timeout=10.0) as client:
        # Warmup query
        client.post(API_URL, json={"query": "warmup"})

        for q in QUERIES:
            for _ in range(5):
                start = time.perf_counter()
                resp = client.post(API_URL, json={"query": q, "limit": 5})
                elapsed = (time.perf_counter() - start) * 1000
                if resp.status_code == 200:
                    latencies.append(elapsed)

    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)

    print(f"Latency P50: {p50:.1f}ms (Target: < 1500ms)")
    print(f"Latency P95: {p95:.1f}ms (Target: < 3000ms)")

    assert p50 < 1500, f"P50 latency failed: {p50}ms >= 1500ms"
    assert p95 < 3000, f"P95 latency failed: {p95}ms >= 3000ms"
    print("✅ Latency SLA passed successfully.")

if __name__ == "__main__":
    benchmark()
```

---

## Step 4: Verification Checklist

- [ ] Run frontend tests:
  ```powershell
  cd "d:\Meme GPT\frontend"
  npm test
  ```
- [ ] Run AI evaluation benchmark:
  ```powershell
  cd "d:\Meme GPT"
  python scripts/evaluate_ai_search.py
  ```
- [ ] Run latency SLA benchmark:
  ```powershell
  cd "d:\Meme GPT"
  python scripts/benchmark_latency.py
  ```
