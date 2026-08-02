# MemeGPT — Frontend Tests

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Test Stack

| Tool | Purpose |
|---|---|
| **vitest** | Test runner (fast, Vite-native) |
| **React Testing Library** | Component rendering + assertions |
| **jsdom** | Browser environment simulation |
| **MSW** | API mocking (Mock Service Worker) |

---

## Running Tests

```bash
npm run test           # Run all tests
npm run test:watch     # Watch mode
npm run test:coverage  # With coverage report
```

---

## Test Examples

### Component Tests

```typescript
// SearchInput.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { SearchInput } from '../components/SearchInput';

test('renders placeholder text', () => {
  render(<SearchInput onSearch={vi.fn()} loading={false} />);
  expect(screen.getByPlaceholderText(/What's happening/i)).toBeInTheDocument();
});

test('calls onSearch when Ctrl+Enter pressed', () => {
  const onSearch = vi.fn();
  render(<SearchInput onSearch={onSearch} loading={false} />);
  const input = screen.getByRole('textbox');
  fireEvent.change(input, { target: { value: 'test query' } });
  fireEvent.keyDown(input, { key: 'Enter', ctrlKey: true });
  expect(onSearch).toHaveBeenCalledWith('test query');
});

test('disables input when loading', () => {
  render(<SearchInput onSearch={vi.fn()} loading={true} />);
  expect(screen.getByRole('textbox')).toBeDisabled();
});

test('shows character count', () => {
  render(<SearchInput onSearch={vi.fn()} loading={false} />);
  const input = screen.getByRole('textbox');
  fireEvent.change(input, { target: { value: 'hello world' } });
  expect(screen.getByText('11/2000')).toBeInTheDocument();
});
```

### Hook Tests

```typescript
// useMemeSearch.test.ts
import { renderHook, act } from '@testing-library/react';
import { useMemeSearch } from '../hooks/useMemeSearch';

test('starts with empty results', () => {
  const { result } = renderHook(() => useMemeSearch());
  expect(result.current.results).toEqual([]);
  expect(result.current.loading).toBe(false);
});

test('sets loading state during search', async () => {
  const { result } = renderHook(() => useMemeSearch());
  act(() => { result.current.search('test'); });
  expect(result.current.loading).toBe(true);
});
```

---

## Coverage Target: >70%

| Component | Target |
|---|---|
| SearchInput | >90% |
| MemeCard | >85% |
| ResultsGrid | >80% |
| Custom hooks | >85% |
| API client | >75% |

---

> **Related Documents:**
> - [Testing_Strategy.md](./Testing_Strategy.md) · [04_Frontend/Components.md](../04_Frontend/Components.md)
