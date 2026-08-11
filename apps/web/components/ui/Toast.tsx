import React from 'react';

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info';
  onClose?: () => void;
}

export const Toast: React.FC<ToastProps> = ({ message, type = 'success', onClose }) => {
  return (
    <div className="fixed bottom-4 right-4 z-50 flex items-center gap-2 rounded-lg bg-neutral-900 border border-neutral-700 px-4 py-3 text-sm text-neutral-100 shadow-xl animate-fade-in">
      <span className={type === 'success' ? 'text-emerald-400' : 'text-rose-400'}>
        {type === 'success' ? '✓' : '✕'}
      </span>
      <span>{message}</span>
      {onClose && (
        <button onClick={onClose} className="ml-2 text-neutral-500 hover:text-neutral-300">
          ×
        </button>
      )}
    </div>
  );
};
