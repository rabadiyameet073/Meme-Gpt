/// <reference types="vitest" />
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useMemeSearch } from '../hooks/useMemeSearch';

describe('useMemeSearch Hook', () => {
  it('starts with empty results', () => {
    const { result } = renderHook(() => useMemeSearch());
    expect(result.current.results).toEqual([]);
    expect(result.current.loading).toBe(false);
  });

  it('sets loading state during search', async () => {
    const { result } = renderHook(() => useMemeSearch());
    let p: Promise<void> | undefined;
    act(() => {
      p = result.current.search('test') as any;
    });
    expect(result.current.loading).toBe(true);
    await act(async () => {
      await p;
    });
  });
});
