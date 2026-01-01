# DB Query Tool 使用指南

## 功能概述

這個資料庫查詢工具提供以下核心功能：

### 1. 資料庫連接管理
- ✅ 添加資料庫連接（支持 MySQL, PostgreSQL, SQLite）
- ✅ 查看所有已連接的資料庫
- ✅ 編輯和刪除資料庫連接
- ✅ 查看資料庫 metadata（表、列、數據類型等）

### 2. SQL 查詢執行
- ✅ **手動 SQL 查詢**：在 "Manual SQL" 標籤中輸入和執行 SQL 查詢
- ✅ 支持語法驗證
- ✅ 自動添加 LIMIT 限制（防止返回過多數據）
- ✅ 顯示查詢結果、執行時間、行數
- ✅ 導出結果為 CSV 或 JSON
- ✅ 快捷鍵：`Ctrl+Enter` (或 `Cmd+Enter`) 執行查詢

### 3. 自然語言查詢 (NL2SQL)
- ✅ **自然語言轉 SQL**：在 "Natural Language" 標籤中用中文或英文描述查詢需求
- ✅ 基於 GPT-4 自動生成 SQL 查詢
- ✅ 顯示生成的 SQL 和解釋
- ✅ 一鍵切換到 Manual SQL 標籤執行生成的查詢

### 4. 查詢歷史
- ✅ 保存所有查詢歷史（成功和失敗）
- ✅ 查看執行時間、結果行數
- ✅ 一鍵重用歷史查詢

## 使用步驟

### 第一步：配置 OpenAI API Key

自然語言查詢功能需要 OpenAI API Key：

#### Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

#### Linux/macOS:
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

或者在 `backend/.env` 文件中設置：
```env
OPENAI_API_KEY=sk-your-api-key-here
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=*
```

### 第二步：啟動服務

#### 方式 1：使用腳本（推薦）
```bash
cd scripts
.\start-all.bat
```

#### 方式 2：手動啟動

**後端：**
```bash
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

**前端：**
```bash
cd frontend
npm run dev
```

### 第三步：添加資料庫連接

1. 打開瀏覽器訪問 `http://localhost:5173`
2. 點擊 "ADD DATABASE" 按鈕
3. 輸入資料庫連接資訊：
   - **Name**: 連接名稱（例如：todo）
   - **URL**: 資料庫連接字符串
     - MySQL: `mysql+aiomysql://user:password@localhost:3306/database`
     - PostgreSQL: `postgresql+asyncpg://user:password@localhost:5432/database`
     - SQLite: `sqlite+aiosqlite:///path/to/database.db`
   - **Description**: 可選描述

### 第四步：執行查詢

#### 方式 A：手動 SQL 查詢

1. 在左側選擇資料庫
2. 點擊 "Manual SQL" 標籤
3. 輸入 SQL 查詢，例如：
   ```sql
   SELECT * FROM todo WHERE completed = 0
   ```
4. 點擊 "Execute Query" 或按 `Ctrl+Enter`
5. 查看結果表格

#### 方式 B：自然語言查詢

1. 在左側選擇資料庫
2. 點擊 "Natural Language" 標籤
3. 用中文或英文描述查詢需求，例如：
   - 中文：`查詢所有未完成的 todo`
   - 英文：`Show all incomplete tasks`
   - 中文：`按創建時間倒序查詢最近10條記錄`
4. 點擊 "Generate SQL"
5. 查看生成的 SQL 和解釋
6. 點擊 "Use This SQL" 自動填充到 Manual SQL 標籤
7. 執行查詢查看結果

### 第五步：查看查詢歷史

1. 點擊 "Show History" 按鈕
2. 右側顯示查詢歷史記錄
3. 點擊歷史記錄可重用該 SQL

## API 端點

### 資料庫管理
- `GET /api/v1/dbs` - 列出所有資料庫連接
- `PUT /api/v1/dbs/{name}` - 創建或更新資料庫連接
- `GET /api/v1/dbs/{name}` - 獲取資料庫詳情和 metadata
- `DELETE /api/v1/dbs/{name}` - 刪除資料庫連接
- `POST /api/v1/dbs/{name}/refresh` - 刷新 metadata

### 查詢執行
- `POST /api/v1/dbs/{name}/query` - 執行 SQL 查詢
- `GET /api/v1/dbs/{name}/history` - 獲取查詢歷史
- `POST /api/v1/dbs/{name}/query/natural` - 自然語言轉 SQL

### 健康檢查
- `GET /health` - 服務健康狀態

## 功能特性

### SQL 驗證和安全
- ✅ 只允許 SELECT 查詢（防止數據修改）
- ✅ 自動添加 LIMIT 1000（可配置）
- ✅ 防止 SQL 注入
- ✅ 查詢超時保護（默認 30 秒）

### 智能 NL2SQL
- ✅ 支持中英文混合查詢
- ✅ 基於實際資料庫 schema 生成 SQL
- ✅ 包含 SQL 解釋說明
- ✅ 自動驗證生成的 SQL

### 查詢結果
- ✅ 表格展示
- ✅ 顯示列名和數據類型
- ✅ 顯示執行時間和行數
- ✅ 支持分頁
- ✅ 導出為 CSV/JSON

## 常見問題

### Q1: 自然語言查詢報錯 "OpenAI API key not configured"
**A**: 請確保已設置 `OPENAI_API_KEY` 環境變數並重啟後端服務。

### Q2: 資料庫連接失敗
**A**: 請檢查：
- 資料庫服務是否運行
- 連接字符串格式是否正確
- 用戶名密碼是否正確
- 網絡連接是否正常

### Q3: 查詢結果為空
**A**: 檢查：
- SQL 語法是否正確
- 表中是否有數據
- WHERE 條件是否過濾掉了所有數據

### Q4: 自然語言生成的 SQL 不正確
**A**: 可以：
- 使用更具體的描述
- 明確指定表名和列名
- 在 Manual SQL 標籤中手動修改生成的 SQL

## 技術棧

### 後端
- FastAPI - Web 框架
- SQLAlchemy - ORM 和查詢執行
- Alembic - 數據庫遷移
- OpenAI SDK - NL2SQL 功能
- Pydantic - 數據驗證

### 前端
- React + TypeScript
- Ant Design - UI 組件庫
- Vite - 構建工具
- Axios - HTTP 客戶端

## 開發調試

### 查看後端日誌
後端啟動後會在終端顯示詳細日誌，包括：
- API 請求記錄
- SQL 執行日誌
- 錯誤堆棧信息

### 查看前端控制台
在瀏覽器開發者工具中可以看到：
- API 請求和響應
- React 組件狀態
- 錯誤信息

## 授權
MIT License
