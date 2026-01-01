/** Query result table component. */

import { useState, useEffect } from 'react';
import { Table, Typography, Space, Tag, Button, Dropdown, message, Modal } from 'antd';
import { DownloadOutlined, ExportOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { QueryResult, ExportFormat } from '../types/query';
import type { ColumnsType } from 'antd/es/table';
import { queryApi } from '../services/api';

const { Text } = Typography;

interface ResultTableProps {
  result: QueryResult;
  databaseName: string;
}

export default function ResultTable({ result, databaseName }: ResultTableProps) {
  const [exportLoading, setExportLoading] = useState(false);

  // Listen for export events from notification
  useEffect(() => {
    const handleExportEvent = (event: any) => {
      const format = event.detail?.format;
      if (format && (format === 'csv' || format === 'json')) {
        handleExport(format);
      }
    };

    window.addEventListener('export-data', handleExportEvent);
    return () => {
      window.removeEventListener('export-data', handleExportEvent);
    };
  }, [result, databaseName]);

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

  // Handle export to specified format
  const handleExport = async (format: ExportFormat) => {
    setExportLoading(true);
    try {
      const exportResult = await queryApi.export(databaseName, {
        columns: result.columns,
        rows: result.rows,
        format,
      });

      // Create blob and download
      const blob = new Blob([exportResult.data], {
        type: format === 'csv' ? 'text/csv' : 'application/json',
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = exportResult.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      message.success(`Successfully exported ${result.rowCount} rows as ${format.toUpperCase()}`);
    } catch (error: any) {
      console.error('Export error:', error);
      message.error(error.response?.data?.error?.message || 'Failed to export data');
    } finally {
      setExportLoading(false);
    }
  };

  // Export menu items
  const exportMenuItems: MenuProps['items'] = [
    {
      key: 'csv',
      label: 'Export as CSV',
      icon: <DownloadOutlined />,
      onClick: () => handleExport('csv'),
    },
    {
      key: 'json',
      label: 'Export as JSON',
      icon: <DownloadOutlined />,
      onClick: () => handleExport('json'),
    },
  ];

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%', marginBottom: '16px' }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <Tag color="blue">{result.rowCount} rows</Tag>
            <Tag color="green">{result.executionTimeMs}ms</Tag>
            {result.sql !== result.rows.length && (
              <Text type="secondary" style={{ fontSize: '12px' }}>
                SQL: {result.sql}
              </Text>
            )}
          </Space>
          <Dropdown menu={{ items: exportMenuItems }} placement="bottomRight">
            <Button
              type="primary"
              icon={<ExportOutlined />}
              loading={exportLoading}
            >
              Export Data
            </Button>
          </Dropdown>
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
