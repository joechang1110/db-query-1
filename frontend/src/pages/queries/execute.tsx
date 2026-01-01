/** Query execution page. */

import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Layout,
  Row,
  Col,
  Card,
  Button,
  Select,
  Space,
  Divider,
  message,
  Spin,
  Tabs,
  Alert,
  Statistic,
  Menu,
} from 'antd';
import type { TabsProps } from 'antd';
import {
  PlayCircleOutlined,
  ClearOutlined,
  HistoryOutlined,
  CodeOutlined,
  ThunderboltOutlined,
  DatabaseOutlined,
  ReloadOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import SqlEditor from '../../components/SqlEditor';
import ResultTable from '../../components/ResultTable';
import QueryHistory from '../../components/QueryHistory';
import NaturalLanguageInput from '../../components/NaturalLanguageInput';
import MetadataTree from '../../components/MetadataTree';
import { useQueryExecution } from '../../hooks/useQueryExecution';
import { databaseApi } from '../../services/api';
import { DatabaseConnection } from '../../types/database';

const { Content, Sider } = Layout;
const { Option } = Select;

export default function QueryExecutePage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [databases, setDatabases] = useState<DatabaseConnection[]>([]);
  const [loadingDatabases, setLoadingDatabases] = useState(true);
  const [selectedDatabase, setSelectedDatabase] = useState<string | undefined>(
    searchParams.get('db') || undefined
  );
  const [sql, setSql] = useState<string>('');
  const [showMetadata, setShowMetadata] = useState(true);
  const [historyRefreshTrigger, setHistoryRefreshTrigger] = useState(0);
  const [activeTab, setActiveTab] = useState<string>('manual');
  const [metadata, setMetadata] = useState<any>(null);
  const [loadingMetadata, setLoadingMetadata] = useState(false);

  const { loading, error, result, executeQuery, reset } = useQueryExecution();

  // Load databases on mount
  useEffect(() => {
    const fetchDatabases = async () => {
      setLoadingDatabases(true);
      try {
        const data = await databaseApi.list();
        setDatabases(data);

        // If no database selected but we have databases, select the first one
        if (!selectedDatabase && data.length > 0) {
          setSelectedDatabase(data[0].name);
        }
      } catch (error: any) {
        message.error(
          error.response?.data?.error?.message || 'Failed to load databases'
        );
      } finally {
        setLoadingDatabases(false);
      }
    };

    fetchDatabases();
  }, []);

  // Update URL when database changes
  useEffect(() => {
    if (selectedDatabase) {
      setSearchParams({ db: selectedDatabase });
      // Load metadata for selected database
      loadMetadata(selectedDatabase);
    }
  }, [selectedDatabase, setSearchParams]);

  const loadMetadata = async (dbName: string) => {
    setLoadingMetadata(true);
    try {
      const data = await databaseApi.getMetadata(dbName);
      setMetadata(data);
    } catch (error: any) {
      console.error('Failed to load metadata:', error);
    } finally {
      setLoadingMetadata(false);
    }
  };

  const handleRefreshMetadata = async () => {
    if (!selectedDatabase) return;
    setLoadingMetadata(true);
    try {
      const data = await databaseApi.refreshMetadata(selectedDatabase);
      setMetadata(data);
      message.success('Metadata refreshed successfully');
    } catch (error: any) {
      message.error('Failed to refresh metadata');
    } finally {
      setLoadingMetadata(false);
    }
  };

  const handleExecute = async () => {
    if (!selectedDatabase) {
      message.warning('Please select a database');
      return;
    }

    if (!sql.trim()) {
      message.warning('Please enter a SQL query');
      return;
    }

    try {
      await executeQuery(selectedDatabase, { sql });
      message.success('Query executed successfully');
      // Trigger history refresh
      setHistoryRefreshTrigger((prev) => prev + 1);
    } catch (err) {
      // Error already handled in hook and displayed in SqlEditor
      console.error('Query execution failed:', err);
    }
  };

  const handleClear = () => {
    setSql('');
    reset();
  };

  const handleSqlGenerated = (generatedSql: string) => {
    setSql(generatedSql);
    setActiveTab('manual'); // Switch to manual tab to show generated SQL
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    // Ctrl/Cmd + Enter to execute
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleExecute();
    }
  };

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown as any);
    return () => {
      window.removeEventListener('keydown', handleKeyDown as any);
    };
  }, [sql, selectedDatabase]);

  if (loadingDatabases) {
    return (
      <Layout style={{ minHeight: '100vh', padding: '24px' }}>
        <Content>
          <Spin tip="Loading databases..." size="large" />
        </Content>
      </Layout>
    );
  }

  if (databases.length === 0) {
    return (
      <Layout style={{ minHeight: '100vh', padding: '24px' }}>
        <Content>
          <Card>
            <div style={{ textAlign: 'center', padding: '48px' }}>
              <p>No databases available. Please add a database connection first.</p>
              <Button type="primary" href="/databases/create">
                Add Database
              </Button>
            </div>
          </Card>
        </Content>
      </Layout>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Left Sidebar */}
      <Sider width={280} style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}>
        <div style={{ padding: '16px' }}>
          {/* Header */}
          <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h3 style={{ margin: 0 }}>
              <DatabaseOutlined /> DB QUERY TOOL
            </h3>
          </div>

          {/* Add Database Button */}
          <Button
            type="primary"
            icon={<PlusOutlined />}
            block
            style={{ marginBottom: '16px' }}
            onClick={() => navigate('/databases/new')}
          >
            ADD DATABASE
          </Button>

          {/* Database Sections */}
          <div style={{ marginBottom: '24px' }}>
            <Card
              size="small"
              title="TODO"
              extra={<Button type="text" size="small" icon={<ReloadOutlined />} />}
              style={{ marginBottom: '8px' }}
            >
              <div style={{ fontSize: '12px', color: '#999' }}>
                Test database for development
              </div>
            </Card>

            <Card
              size="small"
              title="HACKATHON"
              extra={<Button type="text" size="small" icon={<ReloadOutlined />} />}
              style={{ marginBottom: '8px' }}
            >
              <div style={{ fontSize: '12px', color: '#999' }}>
                Project database
              </div>
            </Card>
          </div>

          <Divider style={{ margin: '12px 0' }} />

          {/* Metadata Tree */}
          {selectedDatabase && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontWeight: 'bold' }}>Tables ({metadata?.tables?.length || 0})</span>
                <Button
                  type="text"
                  size="small"
                  icon={<ReloadOutlined />}
                  loading={loadingMetadata}
                  onClick={handleRefreshMetadata}
                />
              </div>
              {metadata && <MetadataTree metadata={metadata} />}
            </div>
          )}
        </div>
      </Sider>

      {/* Main Content */}
      <Layout>
        <Content style={{ background: '#f5f5f5' }}>
          {/* Top Statistics Bar */}
          <div style={{ background: '#fff', padding: '16px 24px', borderBottom: '1px solid #f0f0f0' }}>
            <Row gutter={16}>
              <Col>
                <Statistic title="DATABASES" value={databases.length} />
              </Col>
              <Col>
                <Statistic title="QUERIES" value={result?.rowCount || 0} />
              </Col>
              <Col>
                <Statistic title="RESULTS" value={result ? 8 : 0} />
              </Col>
              <Col>
                <Statistic
                  title="TIME"
                  value={result?.executionTimeMs || 0}
                  suffix="ms"
                  valueStyle={{ color: '#3f8600' }}
                />
              </Col>
            </Row>
          </div>

          {/* Query Editor Area */}
          <div style={{ padding: '24px' }}>
            <Row gutter={[16, 16]}>
              <Col span={24}>
                <Card
                  title={
                    <Space>
                      <span>QUERY EDITOR</span>
                      <Select
                        style={{ width: 200 }}
                        placeholder="Select database"
                        value={selectedDatabase}
                        onChange={setSelectedDatabase}
                        loading={loadingDatabases}
                      >
                        {databases.map((db) => (
                          <Option key={db.name} value={db.name}>
                            {db.name}
                          </Option>
                        ))}
                      </Select>
                    </Space>
                  }
                  extra={
                    <Button type="link" onClick={() => navigate('/databases')}>
                      Manage Databases
                    </Button>
                  }
                >
                  <Tabs
                    activeKey={activeTab}
                    onChange={setActiveTab}
                    items={[
                      {
                        key: 'manual',
                        label: 'MANUAL SQL',
                        children: (
                          <Space direction="vertical" style={{ width: '100%' }} size="large">
                            <div>
                              <SqlEditor
                                value={sql}
                                onChange={setSql}
                                error={error}
                                height="300px"
                              />
                              <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                                Press Ctrl+Enter (Cmd+Enter) to generate
                              </div>
                            </div>

                            <Space>
                              <Button
                                type="primary"
                                icon={<PlayCircleOutlined />}
                                onClick={handleExecute}
                                loading={loading}
                                disabled={!selectedDatabase || !sql.trim()}
                              >
                                Execute Query
                              </Button>
                              <Button icon={<ClearOutlined />} onClick={handleClear}>
                                Clear
                              </Button>
                            </Space>
                          </Space>
                        ),
                      },
                      {
                        key: 'natural',
                        label: 'NATURAL LANGUAGE',
                        children: selectedDatabase ? (
                          <NaturalLanguageInput
                            databaseName={selectedDatabase}
                            onSqlGenerated={handleSqlGenerated}
                          />
                        ) : (
                          <Alert
                            message="Please select a database first"
                            type="info"
                            showIcon
                          />
                        ),
                      },
                    ]}
                  />

                  {loading && (
                    <div style={{ textAlign: 'center', padding: '24px', marginTop: '16px' }}>
                      <Spin tip="Executing query..." />
                    </div>
                  )}

                  {result && !loading && (
                    <>
                      <Divider />
                      <div style={{ marginBottom: '16px' }}>
                        <Space>
                          <span style={{ fontWeight: 'bold' }}>
                            RESULTS - {result.rowCount} ROWS • {result.executionTimeMs}MS
                          </span>
                          <Button size="small">EXPORT CSV</Button>
                          <Button size="small">EXPORT JSON</Button>
                        </Space>
                      </div>
                      <ResultTable result={result} />
                    </>
                  )}
                </Card>
              </Col>
            </Row>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}
