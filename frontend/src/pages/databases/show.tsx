/** Database detail/metadata page. */

import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, Button, Space, Tag, Spin, message } from "antd";
import { ArrowLeftOutlined, ReloadOutlined } from "@ant-design/icons";
import { databaseApi } from "../../services/api";
import { DatabaseMetadataResponse } from "../../types/metadata";
import MetadataTree from "../../components/MetadataTree";

export default function DatabaseShowPage() {
  const { name } = useParams<{ name: string }>();
  const navigate = useNavigate();
  const [metadata, setMetadata] = useState<DatabaseMetadataResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (name) {
      loadMetadata();
    }
  }, [name]);

  const loadMetadata = async () => {
    if (!name) return;
    try {
      setLoading(true);
      const data = await databaseApi.getMetadata(name);
      setMetadata(data);
    } catch (error) {
      message.error("Failed to load database metadata");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (!name) return;
    try {
      setRefreshing(true);
      const data = await databaseApi.refreshMetadata(name);
      setMetadata(data);
      message.success("Metadata refreshed successfully");
    } catch (error) {
      message.error("Failed to refresh metadata");
      console.error(error);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: "24px", textAlign: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!metadata) {
    return <div>Database not found</div>;
  }

  return (
    <div style={{ padding: "24px" }}>
      <Space style={{ marginBottom: "16px" }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/databases")}>
          Back
        </Button>
        <h1 style={{ margin: 0 }}>{metadata.databaseName}</h1>
        <Tag>{metadata.databaseType.toUpperCase()}</Tag>
        {metadata.isStale && <Tag color="orange">Stale</Tag>}
      </Space>

      <Space style={{ marginBottom: "16px" }}>
        <Button
          icon={<ReloadOutlined />}
          onClick={handleRefresh}
          loading={refreshing}
        >
          Refresh Metadata
        </Button>
      </Space>

      <Card title={`Tables (${metadata.tables.length})`} style={{ marginBottom: "16px" }}>
        <MetadataTree items={metadata.tables} />
      </Card>

      <Card title={`Views (${metadata.views.length})`}>
        <MetadataTree items={metadata.views} />
      </Card>
    </div>
  );
}

