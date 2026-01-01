/** SQL Editor component using Monaco Editor. */

import { useRef, useEffect } from 'react';
import Editor, { OnMount } from '@monaco-editor/react';
import { Alert } from 'antd';
import type { editor } from 'monaco-editor';

interface SqlEditorProps {
  value: string;
  onChange: (value: string) => void;
  error?: string | null;
  readOnly?: boolean;
  height?: string;
}

export default function SqlEditor({
  value,
  onChange,
  error,
  readOnly = false,
  height = '300px',
}: SqlEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    // Configure SQL language support
    monaco.languages.registerCompletionItemProvider('sql', {
      provideCompletionItems: (model, position) => {
        // Basic SQL keywords
        const keywords = [
          'SELECT',
          'FROM',
          'WHERE',
          'JOIN',
          'LEFT JOIN',
          'RIGHT JOIN',
          'INNER JOIN',
          'ORDER BY',
          'GROUP BY',
          'HAVING',
          'LIMIT',
          'OFFSET',
          'AS',
          'AND',
          'OR',
          'NOT',
          'IN',
          'LIKE',
          'BETWEEN',
          'IS NULL',
          'IS NOT NULL',
          'COUNT',
          'SUM',
          'AVG',
          'MIN',
          'MAX',
        ];

        const suggestions = keywords.map((keyword) => ({
          label: keyword,
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: keyword,
          range: {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: position.column,
            endColumn: position.column,
          },
        }));

        return { suggestions };
      },
    });

    // Focus editor
    editor.focus();
  };

  const handleChange = (value: string | undefined) => {
    onChange(value || '');
  };

  return (
    <div>
      {error && (
        <Alert
          message="SQL Validation Error"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: '16px' }}
        />
      )}
      <div style={{ border: '1px solid #d9d9d9', borderRadius: '4px', overflow: 'hidden' }}>
        <Editor
          height={height}
          defaultLanguage="sql"
          value={value}
          onChange={handleChange}
          onMount={handleEditorDidMount}
          options={{
            readOnly,
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            wordWrap: 'on',
            suggest: {
              showKeywords: true,
            },
          }}
          theme="vs"
        />
      </div>
    </div>
  );
}
