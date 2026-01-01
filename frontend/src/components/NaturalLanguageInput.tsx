/** Natural language input component. */

import { useState } from 'react';
import { Input, Button, Card, Space, Alert, Typography, Spin } from 'antd';
import { ThunderboltOutlined, ClearOutlined } from '@ant-design/icons';
import { useNaturalLanguage } from '../hooks/useNaturalLanguage';

const { TextArea } = Input;
const { Text, Paragraph } = Typography;

interface NaturalLanguageInputProps {
  databaseName: string;
  onSqlGenerated: (sql: string) => void;
}

export default function NaturalLanguageInput({
  databaseName,
  onSqlGenerated,
}: NaturalLanguageInputProps) {
  const [prompt, setPrompt] = useState('');
  const { loading, error, result, generateSql, reset } = useNaturalLanguage();

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      return;
    }

    await generateSql(databaseName, { prompt: prompt.trim() });
  };

  const handleUseGenerated = () => {
    if (result?.sql) {
      onSqlGenerated(result.sql);
      handleClear();
    }
  };

  const handleClear = () => {
    setPrompt('');
    reset();
  };

  return (
    <Card
      title="Natural Language to SQL"
      extra={
        <Text type="secondary" style={{ fontSize: '12px' }}>
          Powered by GPT-4
        </Text>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <div>
          <TextArea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your query in natural language (English or Chinese)&#10;&#10;Examples:&#10;- Show all active users&#10;- 查询最近30天的订单总额&#10;- Get top 10 customers by revenue"
            autoSize={{ minRows: 4, maxRows: 8 }}
            disabled={loading}
          />
          <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
            Tip: Be specific about what data you want to retrieve
          </div>
        </div>

        <Space>
          <Button
            type="primary"
            icon={<ThunderboltOutlined />}
            onClick={handleGenerate}
            loading={loading}
            disabled={!prompt.trim() || !databaseName}
          >
            Generate SQL
          </Button>
          <Button icon={<ClearOutlined />} onClick={handleClear} disabled={loading}>
            Clear
          </Button>
        </Space>

        {loading && (
          <div style={{ textAlign: 'center', padding: '24px' }}>
            <Spin tip="Generating SQL query..." />
          </div>
        )}

        {error && !loading && (
          <Alert
            message="Generation Failed"
            description={error}
            type="error"
            showIcon
            closable
            onClose={reset}
          />
        )}

        {result && !loading && (
          <Card
            type="inner"
            title="Generated SQL"
            size="small"
            extra={
              <Button type="link" onClick={handleUseGenerated}>
                Use This SQL
              </Button>
            }
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>Query:</Text>
                <Paragraph
                  code
                  copyable
                  style={{
                    marginTop: '8px',
                    padding: '12px',
                    background: '#f5f5f5',
                    borderRadius: '4px',
                  }}
                >
                  {result.sql}
                </Paragraph>
              </div>

              {result.explanation && (
                <div>
                  <Text strong>Explanation:</Text>
                  <Paragraph style={{ marginTop: '8px', marginBottom: 0 }}>
                    {result.explanation}
                  </Paragraph>
                </div>
              )}
            </Space>
          </Card>
        )}
      </Space>
    </Card>
  );
}
