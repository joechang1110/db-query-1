/** Database connection types. */

export enum DatabaseType {
  POSTGRESQL = "postgresql",
  MYSQL = "mysql",
  SQLITE = "sqlite",
}

export enum ConnectionStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  ERROR = "error",
}

export interface DatabaseConnection {
  name: string;
  url: string;
  databaseType: DatabaseType;
  description?: string;
  createdAt: string;
  updatedAt: string;
  lastConnectedAt?: string;
  status: ConnectionStatus;
}

export interface DatabaseConnectionInput {
  url: string;
  description?: string;
}

