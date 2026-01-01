/** Database create/edit form page. */

import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Form, Input, Button, Space, message } from "antd";
import { databaseApi } from "../../services/api";
import { DatabaseConnectionInput } from "../../types/database";

export default function DatabaseCreatePage() {
  const navigate = useNavigate();
  const { name } = useParams<{ name: string }>();
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const handleSubmit = async (values: DatabaseConnectionInput & { name: string }) => {
    try {
      setLoading(true);
      await databaseApi.createOrUpdate(values.name, {
        url: values.url,
        description: values.description,
      });
      message.success("Database connection saved successfully");
      navigate(`/databases/${values.name}`);
    } catch (error: unknown) {
      const errorMessage =
        (error as { response?: { data?: { error?: { message?: string } } } })?.response?.data
          ?.error?.message || "Failed to save database connection";
      message.error(errorMessage);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "24px", maxWidth: "800px" }}>
      <h1>{name ? "Edit Database" : "Add Database Connection"}</h1>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={name ? { name } : undefined}
      >
        <Form.Item
          label="Name"
          name="name"
          rules={[
            { required: true, message: "Please enter database name" },
            {
              pattern: /^[a-zA-Z0-9-_]+$/,
              message: "Name can only contain letters, numbers, hyphens, and underscores",
            },
          ]}
        >
          <Input disabled={!!name} placeholder="my-database" />
        </Form.Item>
        <Form.Item
          label="Connection URL"
          name="url"
          rules={[
            { required: true, message: "Please enter database URL" },
            {
              pattern: /^(postgresql|mysql|sqlite):\/\/.+/,
              message: "Invalid database URL format",
            },
          ]}
        >
          <Input
            placeholder="postgresql://user:pass@localhost:5432/dbname"
            style={{ fontFamily: "monospace" }}
          />
        </Form.Item>
        <Form.Item label="Description" name="description">
          <Input.TextArea rows={3} placeholder="Optional description" />
        </Form.Item>
        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" loading={loading}>
              Save
            </Button>
            <Button onClick={() => navigate("/databases")}>Cancel</Button>
          </Space>
        </Form.Item>
      </Form>
    </div>
  );
}

