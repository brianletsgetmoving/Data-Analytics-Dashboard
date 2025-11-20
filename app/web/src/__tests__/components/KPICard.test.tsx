import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KPICard } from '@/components/ui/KPICard';

describe('KPICard', () => {
  it('renders label and value', () => {
    render(<KPICard label="Test KPI" value="100" />);
    expect(screen.getByText('Test KPI')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('displays trend indicator when change is provided', () => {
    render(<KPICard label="Revenue" value="$1,000" change={5.2} trend="up" />);
    expect(screen.getByText('5.2%')).toBeInTheDocument();
  });

  it('shows status badge when provided', () => {
    render(<KPICard label="New Feature" value="50" statusBadge="new" />);
    expect(screen.getByText('NEW')).toBeInTheDocument();
  });
});

