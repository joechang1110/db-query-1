/** API client and service functions. */

import axios, { AxiosInstance, AxiosError } from "axios";
import { DatabaseConnection, DatabaseConnectionInput } from "../types/database";
import { DatabaseMetadataResponse } from "../types/metadata";
import {
  QueryInput,
  QueryResult,
  QueryHistoryEntry,
  NaturalLanguageInput,
  NaturalLanguageResult,
  ExportInput,
  ExportResult,
} from "../types/query";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

// Create Axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Response interceptors for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.data) {
      const errorData = error.response.data as { error?: { message?: string } };
      if (errorData.error?.message) {
        console.error("API Error:", errorData.error.message);
      }
    }
    return Promise.reject(error);
  }
);

// Database endpoints
export const databaseApi = {
  /** List all database connections */
  list: async (): Promise<DatabaseConnection[]> => {
    const response = await apiClient.get<{ databases: DatabaseConnection[] }>("/dbs");
    return response.data.databases;
  },

  /** Get database connection by name */
  get: async (name: string): Promise<DatabaseConnection> => {
    const response = await apiClient.get<DatabaseConnection>(`/dbs/${name}`);
    return response.data;
  },

  /** Create or update database connection */
  createOrUpdate: async (
    name: string,
    data: DatabaseConnectionInput
  ): Promise<DatabaseConnection> => {
    const response = await apiClient.put<DatabaseConnection>(`/dbs/${name}`, data);
    return response.data;
  },

  /** Delete database connection */
  delete: async (name: string): Promise<void> => {
    await apiClient.delete(`/dbs/${name}`);
  },

  /** Get database metadata */
  getMetadata: async (name: string): Promise<DatabaseMetadataResponse> => {
    const response = await apiClient.get<DatabaseMetadataResponse>(`/dbs/${name}`);
    return response.data;
  },

  /** Refresh database metadata */
  refreshMetadata: async (name: string): Promise<DatabaseMetadataResponse> => {
    const response = await apiClient.post<DatabaseMetadataResponse>(`/dbs/${name}/refresh`);
    return response.data;
  },
};

// Query endpoints
export const queryApi = {
  /** Execute SQL query */
  execute: async (databaseName: string, query: QueryInput): Promise<QueryResult> => {
    const response = await apiClient.post<QueryResult>(`/dbs/${databaseName}/query`, query);
    return response.data;
  },

  /** Get query history for a database */
  getHistory: async (databaseName: string, limit: number = 50): Promise<QueryHistoryEntry[]> => {
    const response = await apiClient.get<QueryHistoryEntry[]>(
      `/dbs/${databaseName}/history`,
      { params: { limit } }
    );
    return response.data;
  },

  /** Generate SQL from natural language */
  generateFromNaturalLanguage: async (
    databaseName: string,
    input: NaturalLanguageInput
  ): Promise<NaturalLanguageResult> => {
    const response = await apiClient.post<NaturalLanguageResult>(
      `/dbs/${databaseName}/query/natural`,
      input
    );
    return response.data;
  },

  /** Export query results to specified format */
  export: async (
    databaseName: string,
    input: ExportInput
  ): Promise<ExportResult> => {
    const response = await apiClient.post<ExportResult>(
      `/dbs/${databaseName}/export`,
      input
    );
    return response.data;
  },
};

export default apiClient;

