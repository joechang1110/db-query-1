# Windows 啟動腳本

這個目錄包含用於啟動和停止 Database Query Tool 服務的 Windows 批處理腳本。

## 腳本列表

### 1. `start-backend.bat`
啟動後端 FastAPI 服務器。

**功能：**
- 檢查虛擬環境是否存在
- 如果資料庫不存在，自動運行遷移
- 啟動 uvicorn 開發服務器
- 在 http://localhost:8000 運行

**使用方法：**
```batch
scripts\start-backend.bat
```

### 2. `start-frontend.bat`
啟動前端 React 開發服務器。

**功能：**
- 檢查依賴是否已安裝
- 啟動 Vite 開發服務器
- 在 http://localhost:5173 運行

**使用方法：**
```batch
scripts\start-frontend.bat
```

### 3. `start-all.bat`
同時啟動後端和前端服務器。

**功能：**
- 在兩個獨立的命令窗口啟動後端和前端
- 自動等待後端啟動後再啟動前端
- 顯示服務器 URL 信息

**使用方法：**
```batch
scripts\start-all.bat
```

### 4. `stop-all.bat`
停止所有運行的服務器。

**功能：**
- 停止端口 8000 上的後端服務器
- 停止端口 5173 上的前端服務器
- 清理相關進程

**使用方法：**
```batch
scripts\stop-all.bat
```

## 快速開始

### 方法 1：使用腳本（推薦）

```batch
# 1. 安裝依賴（首次運行）
cd w2\db_query_1
make install

# 2. 啟動所有服務
scripts\start-all.bat
```

### 方法 2：分別啟動

```batch
# 終端 1 - 啟動後端
scripts\start-backend.bat

# 終端 2 - 啟動前端
scripts\start-frontend.bat
```

## 注意事項

1. **首次運行前**：
   - 確保已安裝依賴：`make install`
   - 確保已運行遷移：`make migrate`

2. **環境變數**：
   - 確保設置了 `OPENAI_API_KEY` 環境變數（用於自然語言查詢功能）
   - 可以在系統環境變數中設置，或在啟動腳本中臨時設置

3. **端口衝突**：
   - 如果端口 8000 或 5173 已被佔用，腳本會失敗
   - 使用 `stop-all.bat` 停止現有服務，或手動更改端口

4. **停止服務**：
   - 在服務器窗口中按 `Ctrl+C`
   - 或使用 `stop-all.bat` 腳本

## 故障排除

### 錯誤：虛擬環境未找到
```batch
# 解決方案：安裝後端依賴
cd backend
uv venv
uv pip install -e ".[dev]"
```

### 錯誤：依賴未安裝
```batch
# 解決方案：安裝前端依賴
cd frontend
npm install
```

### 錯誤：端口已被佔用
```batch
# 解決方案：停止現有服務
scripts\stop-all.bat
```

### 錯誤：資料庫未初始化
```batch
# 解決方案：運行遷移
cd backend
.venv\Scripts\python.exe -m alembic upgrade head
```

## 自定義配置

如果需要修改端口或其他配置，可以編輯腳本文件：

- **後端端口**：編輯 `start-backend.bat`，修改 `--port 8000`
- **前端端口**：編輯 `frontend/vite.config.ts` 或設置環境變數

## 與 Makefile 的關係

這些腳本提供了 Windows 原生的啟動方式，與 Makefile 的命令功能相同：

| Makefile 命令 | 對應腳本 |
|-------------|---------|
| `make dev-backend` | `scripts\start-backend.bat` |
| `make dev-frontend` | `scripts\start-frontend.bat` |
| `make dev` | `scripts\start-all.bat` |
| `make stop` | `scripts\stop-all.bat` |

選擇使用 Makefile 或批處理腳本都可以，取決於你的偏好。

