/** Metadata tree view component. */

import { Collapse } from "antd";
import { TableMetadata, DatabaseMetadataResponse } from "../types/metadata";
import type { CollapseProps } from "antd/es/collapse";

interface MetadataTreeProps {
  metadata: DatabaseMetadataResponse | null;
}

export default function MetadataTree({ metadata }: MetadataTreeProps) {
  if (!metadata || !metadata.tables || metadata.tables.length === 0) {
    return <div style={{ color: '#999', fontSize: '12px' }}>No tables found</div>;
  }

  const panels: CollapseProps["items"] = metadata.tables.map((item) => ({
    key: item.name,
    label: (
      <div>
        <strong>{item.name}</strong>
        {item.type === "table" && item.rowCount !== undefined && (
          <span style={{ marginLeft: "8px", color: "#666" }}>
            ({item.rowCount} rows)
          </span>
        )}
      </div>
    ),
    children: (
      <div>
        <div style={{ marginBottom: "8px" }}>
          <strong>Schema:</strong> {item.schemaName}
        </div>
        <div>
          <strong>Columns:</strong>
          <table style={{ width: "100%", marginTop: "8px" }}>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Nullable</th>
                <th>Primary Key</th>
                <th>Default</th>
              </tr>
            </thead>
            <tbody>
              {item.columns.map((col) => (
                <tr key={col.name}>
                  <td>
                    <strong>{col.name}</strong>
                  </td>
                  <td>{col.dataType}</td>
                  <td>{col.nullable ? "Yes" : "No"}</td>
                  <td>{col.primaryKey ? "✓" : ""}</td>
                  <td style={{ fontFamily: "monospace", fontSize: "12px" }}>
                    {col.defaultValue || "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    ),
  }));

  return <Collapse items={panels} />;
}

