/// <reference types="vitest" />
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { SearchInput } from '../components/SearchInput';

describe('SearchInput Component', () => {
  it('renders placeholder text', () => {
    render(<SearchInput onSearch={vi.fn()} loading={false} />);
    expect(screen.getByPlaceholderText(/What's happening/i)).toBeInTheDocument();
  });

  it('calls onSearch when Ctrl+Enter pressed', () => {
    const onSearch = vi.fn();
    render(<SearchInput onSearch={onSearch} loading={false} />);
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'test query' } });
    fireEvent.keyDown(input, { key: 'Enter', ctrlKey: true });
    expect(onSearch).toHaveBeenCalledWith('test query');
  });

  it('disables input when loading', () => {
    render(<SearchInput onSearch={vi.fn()} loading={true} />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('shows character count', () => {
    render(<SearchInput onSearch={vi.fn()} loading={false} />);
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'hello world' } });
    expect(screen.getByText('11/2000')).toBeInTheDocument();
  });
});
