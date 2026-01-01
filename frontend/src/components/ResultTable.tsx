/** Query result table component. */

import { Table, Typography, Space, Tag } from 'antd';
import { QueryResult } from '../types/query';
import type { ColumnsType } from 'antd/es/table';

const { Text } = Typography;

interface ResultTableProps {
  result: QueryResult;
}

export default function ResultTable({ result }: ResultTableProps) {
  // Build table columns from query result
  const columns: ColumnsType<Record<string, any>> = result.columns.map((col) => ({
    title: col.name,
    dataIndex: col.name,
    key: col.name,
    ellipsis: true,
    render: (value: any) => {
      // Handle null values
      if (value === null || value === undefined) {
        return <Text type="secondary">NULL</Text>;
      }

      // Handle boolean values
      if (typeof value === 'boolean') {
        return value ? 'true' : 'false';
      }

      // Handle objects/arrays (JSON)
      if (typeof value === 'object') {
        return <Text code>{JSON.stringify(value)}</Text>;
      }

      // Default: convert to string
      return String(value);
    },
  }));

  // Add row key for Ant Design table
  const dataSource = result.rows.map((row, index) => ({
    ...row,
    _key: index,
  }));

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%', marginBottom: '16px' }}>
        <Space>
          <Tag color="blue">{result.rowCount} rows</Tag>
          <Tag color="green">{result.executionTimeMs}ms</Tag>
          {result.sql !== result.rows.length && (
            <Text type="secondary" style={{ fontSize: '12px' }}>
              SQL: {result.sql}
            </Text>
          )}
        </Space>
      </Space>

      <Table
        columns={columns}
        dataSource={dataSource}
        rowKey="_key"
        size="small"
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} rows`,
          pageSizeOptions: ['10', '20', '50', '100'],
        }}
        scroll={{ x: 'max-content', y: 500 }}
        bordered
      />
    </div>
  );
}
