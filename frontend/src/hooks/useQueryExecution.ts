/**
 * Custom hook for query execution
 */

import { useState, useCallback } from 'react';
import { queryApi } from '../services/api';
import { QueryResult, QueryInput } from '../types/query';

interface UseQueryExecutionState {
  loading: boolean;
  error: string | null;
  result: QueryResult | null;
}

interface UseQueryExecutionReturn extends UseQueryExecutionState {
  executeQuery: (databaseName: string, query: QueryInput) => Promise<void>;
  reset: () => void;
}

export const useQueryExecution = (): UseQueryExecutionReturn => {
  const [state, setState] = useState<UseQueryExecutionState>({
    loading: false,
    error: null,
    result: null,
  });

  const executeQuery = useCallback(async (databaseName: string, query: QueryInput) => {
    setState({ loading: true, error: null, result: null });

    try {
      const result = await queryApi.execute(databaseName, query);
      setState({ loading: false, error: null, result });
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error?.message || err.message || 'Query execution failed';
      setState({ loading: false, error: errorMessage, result: null });
    }
  }, []);

  const reset = useCallback(() => {
    setState({ loading: false, error: null, result: null });
  }, []);

  return {
    ...state,
    executeQuery,
    reset,
  };
};
