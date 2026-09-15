import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

vi.mock('canvas-confetti', () => ({
  default: vi.fn(),
}));

import { MemeCard } from '../components/MemeCard';
import { SearchInput } from '../components/SearchInput';
import { Sidebar } from '../components/Sidebar';
import { PreviewModal } from '../components/PreviewModal';

describe('Accessibility & A11y Standards (Guide 11)', () => {
  const mockMeme = {
    id: 'meme-123',
    name: 'Distracted Boyfriend',
    alt_text: 'Meme titled Distracted Boyfriend expressing distraction and envy',
    category: 'relationships',
    dialogue: 'Look at that new framework',
    explanation: 'Man looking back at another woman while his girlfriend looks disappointed',
    formats: { image: 'https://example.com/boyfriend.jpg' },
  };

  it('MemeCard includes role=article, aria-label, alt text, and keyboard navigation', () => {
    render(<MemeCard meme={mockMeme} />);

    const article = screen.getByRole('article', { name: /Meme: Distracted Boyfriend/i });
    expect(article).toBeInTheDocument();
    expect(article).toHaveAttribute('tabIndex', '0');

    const image = screen.getByRole('img', { name: mockMeme.alt_text });
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('alt', mockMeme.alt_text);

    const copyBtn = screen.getByRole('button', { name: /copy meme image/i });
    expect(copyBtn).toHaveAttribute('aria-label');

    const favBtn = screen.getByRole('button', { name: /save to favorites/i });
    expect(favBtn).toHaveAttribute('aria-pressed', 'false');

    fireEvent.click(favBtn);
    expect(favBtn).toHaveAttribute('aria-pressed', 'true');
  });

  it('SearchInput provides accessible searchbox, label, and screen-reader instructions', () => {
    render(<SearchInput onSearch={vi.fn()} loading={false} />);

    const searchbox = screen.getByRole('searchbox', { name: /Describe a situation to find the perfect meme/i });
    expect(searchbox).toBeInTheDocument();
    expect(searchbox).toHaveAttribute('id', 'meme-search-input');
    expect(searchbox).toHaveAttribute('aria-describedby', 'search-hint');

    const hint = document.getElementById('search-hint');
    expect(hint).toBeInTheDocument();
    expect(hint).toHaveClass('sr-only');
  });

  it('Sidebar navigation uses role=tablist and accessible tabs', () => {
    render(
      <Sidebar
        history={[]}
        onSelectQuery={vi.fn()}
        onClearHistory={vi.fn()}
        onRemoveItem={vi.fn()}
        activeTab="chat"
        onNavigateTab={vi.fn()}
      />
    );

    const tablist = screen.getByRole('tablist', { name: /Sidebar navigation views/i });
    expect(tablist).toBeInTheDocument();

    const activeTab = screen.getByRole('tab', { name: /AI Matcher/i });
    expect(activeTab).toHaveAttribute('aria-selected', 'true');
    expect(activeTab).toHaveAttribute('tabIndex', '0');

    const inactiveTab = screen.getByRole('tab', { name: /Browse Memes/i });
    expect(inactiveTab).toHaveAttribute('aria-selected', 'false');
    expect(inactiveTab).toHaveAttribute('tabIndex', '-1');
  });

  it('PreviewModal implements accessible dialog with aria-modal and close button', () => {
    const handleClose = vi.fn();
    render(
      <PreviewModal
        isOpen={true}
        onClose={handleClose}
        meme={mockMeme}
      />
    );

    const dialog = screen.getByRole('dialog');
    expect(dialog).toBeInTheDocument();
    expect(dialog).toHaveAttribute('aria-modal', 'true');

    const closeBtn = screen.getByRole('button', { name: /close modal/i });
    expect(closeBtn).toBeInTheDocument();

    fireEvent.keyDown(window, { key: 'Escape', code: 'Escape' });
    expect(handleClose).toHaveBeenCalled();
  });
});
