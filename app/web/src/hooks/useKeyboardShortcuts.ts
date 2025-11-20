import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface Shortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  action: () => void;
  description: string;
}

export function useKeyboardShortcuts(shortcuts: Shortcut[]) {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore if typing in input, textarea, or contenteditable
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      shortcuts.forEach((shortcut) => {
        const ctrlMatch = shortcut.ctrl ? event.ctrlKey || event.metaKey : !event.ctrlKey && !event.metaKey;
        const shiftMatch = shortcut.shift ? event.shiftKey : !event.shiftKey;
        const altMatch = shortcut.alt ? event.altKey : !event.altKey;
        const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase();

        if (ctrlMatch && shiftMatch && altMatch && keyMatch) {
          event.preventDefault();
          shortcut.action();
        }
      });
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts, navigate]);
}

// Predefined shortcuts for common navigation
export function useAppKeyboardShortcuts() {
  const navigate = useNavigate();

  useKeyboardShortcuts([
    {
      key: '1',
      ctrl: true,
      action: () => navigate('/overview'),
      description: 'Go to Overview',
    },
    {
      key: '2',
      ctrl: true,
      action: () => navigate('/revenue'),
      description: 'Go to Revenue',
    },
    {
      key: '3',
      ctrl: true,
      action: () => navigate('/customers'),
      description: 'Go to Customers',
    },
    {
      key: '4',
      ctrl: true,
      action: () => navigate('/jobs'),
      description: 'Go to Jobs',
    },
    {
      key: '5',
      ctrl: true,
      action: () => navigate('/sales-performance'),
      description: 'Go to Sales Performance',
    },
    {
      key: '/',
      ctrl: true,
      action: () => {
        const searchInput = document.querySelector('input[placeholder*="Search"]') as HTMLInputElement;
        if (searchInput) {
          searchInput.focus();
        }
      },
      description: 'Focus search',
    },
    {
      key: '?',
      action: () => {
        // Show keyboard shortcuts help modal
        console.log('Keyboard shortcuts help');
      },
      description: 'Show keyboard shortcuts',
    },
  ]);
}

