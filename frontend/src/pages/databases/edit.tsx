/** Database edit page - redirects to create with name param. */

import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Spin, message } from "antd";
import { databaseApi } from "../../services/api";
import DatabaseCreatePage from "./create";

export default function DatabaseEditPage() {
  const { name } = useParams<{ name: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (name) {
      loadDatabase();
    }
  }, [name]);

  const loadDatabase = async () => {
    try {
      await databaseApi.get(name!);
      // The create page will handle loading the data
      setLoading(false);
    } catch (error) {
      message.error("Failed to load database");
      navigate("/databases");
    }
  };

  if (loading) {
    return (
      <div style={{ padding: "24px", textAlign: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  return <DatabaseCreatePage />;
}

