/** Query history panel component. */

import { useEffect, useState } from 'react';
import { List, Typography, Tag, Space, Card, Empty, Spin, message } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { queryApi } from '../services/api';
import { QueryHistoryEntry } from '../types/query';

const { Text, Paragraph } = Typography;

interface QueryHistoryProps {
  databaseName: string;
  onSelectQuery: (sql: string) => void;
  refreshTrigger?: number; // Use this to trigger refresh from parent
}

export default function QueryHistory({
  databaseName,
  onSelectQuery,
  refreshTrigger = 0,
}: QueryHistoryProps) {
  const [history, setHistory] = useState<QueryHistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      if (!databaseName) return;

      setLoading(true);
      try {
        const data = await queryApi.getHistory(databaseName);
        setHistory(data);
      } catch (error: any) {
        message.error(
          error.response?.data?.error?.message || 'Failed to load query history'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [databaseName, refreshTrigger]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (loading) {
    return (
      <Card>
        <Spin tip="Loading history..." />
      </Card>
    );
  }

  if (history.length === 0) {
    return (
      <Card>
        <Empty description="No query history yet" />
      </Card>
    );
  }

  return (
    <Card title="Query History" size="small">
      <List
        dataSource={history}
        renderItem={(item) => (
          <List.Item
            key={item.id}
            style={{ cursor: 'pointer' }}
            onClick={() => onSelectQuery(item.sqlText)}
          >
            <List.Item.Meta
              avatar={
                item.success ? (
                  <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '20px' }} />
                ) : (
                  <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: '20px' }} />
                )
              }
              title={
                <Paragraph
                  ellipsis={{ rows: 2 }}
                  style={{ marginBottom: 0 }}
                  code
                >
                  {item.sqlText}
                </Paragraph>
              }
              description={
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  <Space size="small" wrap>
                    <Tag icon={<ClockCircleOutlined />} color="default">
                      {formatDate(item.executedAt)}
                    </Tag>
                    {item.executionTimeMs !== null && (
                      <Tag color="green">{item.executionTimeMs}ms</Tag>
                    )}
                    {item.rowCount !== null && (
                      <Tag color="blue">{item.rowCount} rows</Tag>
                    )}
                    <Tag color={item.querySource === 'manual' ? 'default' : 'purple'}>
                      {item.querySource === 'manual' ? 'Manual' : 'NL Generated'}
                    </Tag>
                  </Space>
                  {item.errorMessage && (
                    <Text type="danger" style={{ fontSize: '12px' }}>
                      Error: {item.errorMessage}
                    </Text>
                  )}
                </Space>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );
}
