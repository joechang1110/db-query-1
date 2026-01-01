/** Database metadata types. */

import { DatabaseType } from "./database";

export interface ColumnMetadata {
  name: string;
  dataType: string;
  nullable: boolean;
  primaryKey: boolean;
  unique?: boolean;
  defaultValue?: string;
  comment?: string;
}

export interface TableMetadata {
  name: string;
  type: "table" | "view";
  schemaName: string;
  columns: ColumnMetadata[];
  rowCount?: number;
}

export interface DatabaseMetadataResponse {
  databaseName: string;
  databaseType: DatabaseType;
  tables: TableMetadata[];
  views: TableMetadata[];
  fetchedAt: string;
  isStale: boolean;
}

