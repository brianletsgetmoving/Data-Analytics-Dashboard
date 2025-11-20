import { create } from 'zustand';
import { FilterParams } from '@/shared/types';

interface FilterStore {
  filters: FilterParams;
  setFilters: (filters: Partial<FilterParams>) => void;
  clearFilters: () => void;
}

export const useFilterStore = create<FilterStore>((set) => ({
  filters: {},
  setFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),
  clearFilters: () => set({ filters: {} }),
}));

