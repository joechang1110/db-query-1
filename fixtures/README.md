# REST Client API Tests

這個目錄包含使用 VS Code REST Client 擴展測試 API 的文件。

## 安裝 REST Client 擴展

1. 打開 VS Code
2. 安裝擴展：**REST Client** (humao.rest-client)
3. 擴展市場：https://marketplace.visualstudio.com/items?itemName=humao.rest-client

## 使用方法

1. **啟動後端服務器**：
   ```bash
   make dev-backend
   # 或
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **打開測試文件**：
   - 在 VS Code 中打開 `fixtures/test.rest`

3. **配置變數**：
   - 在文件頂部更新以下變數以匹配你的環境：
     ```
     @postgresUrl = postgresql://user:pass@localhost:5432/dbname
     @mysqlUrl = mysql://user:pass@localhost:3306/dbname
     @sqliteUrl = sqlite:///./path/to/database.db
     ```

4. **執行請求**：
   - 點擊請求上方的 "Send Request" 按鈕
   - 或使用快捷鍵：`Ctrl+Alt+R` (Windows/Linux) 或 `Cmd+Alt+R` (Mac)

## 測試端點列表

### 資料庫連接管理
- ✅ `GET /dbs` - 列出所有資料庫連接
- ✅ `PUT /dbs/{name}` - 創建或更新資料庫連接
- ✅ `GET /dbs/{name}` - 獲取資料庫元數據
- ✅ `DELETE /dbs/{name}` - 刪除資料庫連接
- ✅ `POST /dbs/{name}/refresh` - 刷新元數據

### 查詢執行（Phase 4 - 可能尚未實現）
- ⏳ `POST /dbs/{name}/query` - 執行 SQL 查詢
- ⏳ `GET /dbs/{name}/history` - 獲取查詢歷史

### 自然語言查詢（Phase 5 - 可能尚未實現）
- ⏳ `POST /dbs/{name}/query/natural` - 從自然語言生成 SQL

## 測試場景

文件包含以下測試場景：

1. **基本操作**：創建、讀取、更新、刪除資料庫連接
2. **元數據查詢**：獲取和刷新資料庫元數據
3. **錯誤處理**：測試無效輸入和錯誤情況
4. **多資料庫類型**：PostgreSQL、MySQL、SQLite 測試
5. **查詢執行**：SQL 查詢和自然語言查詢（如果已實現）

## 注意事項

- 確保後端服務器正在運行（`http://localhost:8000`）
- 某些端點可能尚未實現，取決於當前的開發階段
- 自然語言查詢需要設置 `OPENAI_API_KEY` 環境變數
- 資料庫連接會保存在 `backend/db/db_query.db`

## 故障排除

### 連接錯誤
- 檢查後端服務器是否運行：`make health`
- 檢查端口 8000 是否被佔用

### 資料庫連接失敗
- 確認資料庫 URL 格式正確
- 確認資料庫服務正在運行
- 檢查用戶名和密碼是否正確

### REST Client 無法發送請求
- 確認已安裝 REST Client 擴展
- 檢查文件語法是否正確（`.rest` 擴展名）
- 重啟 VS Code

