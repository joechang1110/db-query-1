/** Database list page. */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Table, Button, Space, Tag, message } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { databaseApi } from "../../services/api";
import { DatabaseConnection, ConnectionStatus } from "../../types/database";
import type { ColumnsType } from "antd/es/table";

export default function DatabaseListPage() {
  const navigate = useNavigate();
  const [databases, setDatabases] = useState<DatabaseConnection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDatabases();
  }, []);

  const loadDatabases = async () => {
    try {
      setLoading(true);
      const data = await databaseApi.list();
      setDatabases(data);
    } catch (error) {
      message.error("Failed to load databases");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (name: string) => {
    try {
      await databaseApi.delete(name);
      message.success("Database deleted successfully");
      loadDatabases();
    } catch (error) {
      message.error("Failed to delete database");
      console.error(error);
    }
  };

  const columns: ColumnsType<DatabaseConnection> = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      render: (name: string, record: DatabaseConnection) => (
        <a onClick={() => navigate(`/databases/${name}`)}>{name}</a>
      ),
    },
    {
      title: "Type",
      dataIndex: "databaseType",
      key: "databaseType",
      render: (type: string) => <Tag>{type.toUpperCase()}</Tag>,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status: ConnectionStatus) => {
        const colorMap: Record<ConnectionStatus, string> = {
          active: "green",
          inactive: "default",
          error: "red",
        };
        return <Tag color={colorMap[status]}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: "Description",
      dataIndex: "description",
      key: "description",
    },
    {
      title: "Last Connected",
      dataIndex: "lastConnectedAt",
      key: "lastConnectedAt",
      render: (date: string) => (date ? new Date(date).toLocaleString() : "-"),
    },
    {
      title: "Actions",
      key: "actions",
      render: (_: unknown, record: DatabaseConnection) => (
        <Space>
          <Button size="small" onClick={() => navigate(`/databases/${record.name}`)}>
            View
          </Button>
          <Button size="small" onClick={() => navigate(`/databases/${record.name}/edit`)}>
            Edit
          </Button>
          <Button
            size="small"
            danger
            onClick={() => handleDelete(record.name)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: "24px" }}>
      <div style={{ marginBottom: "16px", display: "flex", justifyContent: "space-between" }}>
        <h1>Database Connections</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate("/databases/new")}
        >
          Add Database
        </Button>
      </div>
      <Table
        columns={columns}
        dataSource={databases}
        loading={loading}
        rowKey="name"
      />
    </div>
  );
}

