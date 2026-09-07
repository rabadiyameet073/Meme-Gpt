import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { SearchInput } from '../components/SearchInput';

describe('SearchInput Component', () => {
  it('renders input field with placeholder', () => {
    const onSearch = vi.fn();
    render(<SearchInput onSearch={onSearch} loading={false} placeholder="Describe a feeling..." />);
    
    const input = screen.getByPlaceholderText(/describe a feeling/i);
    expect(input).toBeInTheDocument();
  });

  it('triggers search callback when submit button is clicked', () => {
    const onSearch = vi.fn();
    render(<SearchInput onSearch={onSearch} loading={false} placeholder="Describe a feeling..." />);
    
    const input = screen.getByPlaceholderText(/describe a feeling/i);
    fireEvent.change(input, { target: { value: 'when tests pass first try' } });
    
    const submitBtn = screen.getByRole('button', { name: /search/i });
    fireEvent.click(submitBtn);
    
    expect(onSearch).toHaveBeenCalledWith('when tests pass first try');
  });

  it('disables input when loading state is true', () => {
    render(<SearchInput onSearch={vi.fn()} loading={true} placeholder="Describe a feeling..." />);
    const input = screen.getByPlaceholderText(/describe a feeling/i);
    expect(input).toBeDisabled();
  });
});
