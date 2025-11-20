import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useRevenueTrendsQuery } from '@/hooks/useAnalytics';
import analyticsAPI from '@/services/api';

// Mock the API
vi.mock('@/services/api', () => ({
  default: {
    getRevenueTrends: vi.fn(),
  },
}));

describe('useAnalytics hooks', () => {
  const createWrapper = () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
    return ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };

  it('fetches revenue trends data', async () => {
    const mockData = {
      data: [
        { period: '2024-01', revenue: 1000, period_type: 'monthly' },
      ],
      metadata: { count: 1 },
    };

    vi.mocked(analyticsAPI.getRevenueTrends).mockResolvedValue(mockData);

    const { result } = renderHook(
      () => useRevenueTrendsQuery('monthly'),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
  });
});

