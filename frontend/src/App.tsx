/** Main application component. */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ConfigProvider } from "antd";
import DatabaseListPage from "./pages/databases/list";
import DatabaseCreatePage from "./pages/databases/create";
import DatabaseShowPage from "./pages/databases/show";
import DatabaseEditPage from "./pages/databases/edit";
import QueryExecutePage from "./pages/queries/execute";

function App() {
  return (
    <ConfigProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<QueryExecutePage />} />
          <Route path="/databases" element={<DatabaseListPage />} />
          <Route path="/databases/new" element={<DatabaseCreatePage />} />
          <Route path="/databases/:name" element={<DatabaseShowPage />} />
          <Route path="/databases/:name/edit" element={<DatabaseEditPage />} />
          <Route path="/query" element={<QueryExecutePage />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;

