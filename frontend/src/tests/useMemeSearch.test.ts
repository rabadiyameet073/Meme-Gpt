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
    act(() => {
      result.current.search('test');
    });
    expect(result.current.loading).toBe(true);
  });
});
