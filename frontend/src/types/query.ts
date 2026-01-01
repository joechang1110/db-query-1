/**
 * Query-related TypeScript types
 */

export type QuerySource = 'manual' | 'natural_language';

export interface QueryInput {
  sql: string;
}

export interface QueryColumn {
  name: string;
  dataType: string;
}

export interface QueryResult {
  columns: QueryColumn[];
  rows: Record<string, any>[];
  rowCount: number;
  executionTimeMs: number;
  sql: string;
}

export interface QueryHistoryEntry {
  id: number;
  databaseName: string;
  sqlText: string;
  executedAt: string;
  executionTimeMs: number | null;
  rowCount: number | null;
  success: boolean;
  errorMessage: string | null;
  querySource: QuerySource;
}

export interface NaturalLanguageInput {
  prompt: string;
}

export interface NaturalLanguageResult {
  sql: string;
  explanation: string;
}
