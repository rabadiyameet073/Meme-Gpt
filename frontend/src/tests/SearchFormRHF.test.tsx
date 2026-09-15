import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SearchFormRHF } from '../components/SearchFormRHF';

describe('React Hook Form: SearchFormRHF (Guide 10)', () => {
  it('renders textarea, format dropdown, and submit button', () => {
    render(<SearchFormRHF onSubmit={vi.fn()} />);

    expect(screen.getByPlaceholderText(/Describe a situation/i)).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
    expect(screen.getByText('0/2000')).toBeInTheDocument();
  });

  it('validates required input when submitted empty', async () => {
    const handleSubmit = vi.fn();
    render(<SearchFormRHF onSubmit={handleSubmit} />);

    const button = screen.getByRole('button', { name: /search/i });
    await userEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Tell us what you are looking for')).toBeInTheDocument();
    });
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('validates minLength rule (< 2 characters)', async () => {
    const handleSubmit = vi.fn();
    render(<SearchFormRHF onSubmit={handleSubmit} />);

    const textarea = screen.getByPlaceholderText(/Describe a situation/i);
    await userEvent.type(textarea, 'a');

    const button = screen.getByRole('button', { name: /search/i });
    await userEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('At least 2 characters')).toBeInTheDocument();
    });
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('submits valid form data with user input and selected format', async () => {
    const handleSubmit = vi.fn();
    render(<SearchFormRHF onSubmit={handleSubmit} />);

    const textarea = screen.getByPlaceholderText(/Describe a situation/i);
    await userEvent.type(textarea, 'friday deploy panic');

    const select = screen.getByRole('combobox');
    await userEvent.selectOptions(select, 'image');

    const button = screen.getByRole('button', { name: /search/i });
    await userEvent.click(button);

    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalled();
      expect(handleSubmit.mock.calls[0][0]).toEqual({
        query: 'friday deploy panic',
        format: 'image',
      });
    });
  });
});
