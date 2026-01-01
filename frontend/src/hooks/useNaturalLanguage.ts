/**
 * Custom hook for natural language to SQL generation
 */

import { useState, useCallback } from 'react';
import { queryApi } from '../services/api';
import { NaturalLanguageInput, NaturalLanguageResult } from '../types/query';

interface UseNaturalLanguageState {
  loading: boolean;
  error: string | null;
  result: NaturalLanguageResult | null;
}

interface UseNaturalLanguageReturn extends UseNaturalLanguageState {
  generateSql: (databaseName: string, input: NaturalLanguageInput) => Promise<void>;
  reset: () => void;
}

export const useNaturalLanguage = (): UseNaturalLanguageReturn => {
  const [state, setState] = useState<UseNaturalLanguageState>({
    loading: false,
    error: null,
    result: null,
  });

  const generateSql = useCallback(async (databaseName: string, input: NaturalLanguageInput) => {
    setState({ loading: true, error: null, result: null });

    try {
      const result = await queryApi.generateFromNaturalLanguage(databaseName, input);
      setState({ loading: false, error: null, result });
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error?.message || err.message || 'Failed to generate SQL';
      setState({ loading: false, error: errorMessage, result: null });
    }
  }, []);

  const reset = useCallback(() => {
    setState({ loading: false, error: null, result: null });
  }, []);

  return {
    ...state,
    generateSql,
    reset,
  };
};
