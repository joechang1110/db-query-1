# Database Query Tool - 安裝與啟動指南

## 問題排查：依賴未安裝

如果遇到 `ModuleNotFoundError: No module named 'alembic'` 或類似錯誤，說明依賴未正確安裝。

## 完整安裝步驟

### 1. 安裝依賴

從項目根目錄運行安裝腳本：

```batch
cd w2\db_query_1
scripts\install-dependencies.bat
```

**或者手動安裝：**

```batch
# 1. 進入項目根目錄
cd w2\db_query_1

# 2. 創建虛擬環境（如果不存在）
cd backend
uv venv
cd ..

# 3. 安裝依賴（使用正確的命令）
uv pip install --python backend/.venv/Scripts/python.exe uvicorn[standard] fastapi pydantic pydantic-settings sqlparse openai sqlalchemy sqlmodel asyncpg aiomysql aiosqlite alembic python-multipart
uv pip install --python backend/.venv/Scripts/python.exe pytest pytest-asyncio httpx mypy ruff black

# 4. 驗證安裝
cd backend
.venv\Scripts\python.exe -c "import alembic; print('✓ alembic installed')"
.venv\Scripts\python.exe -c "import uvicorn; print('✓ uvicorn installed')"
.venv\Scripts\python.exe -c "import fastapi; print('✓ fastapi installed')"
```

### 2. 運行資料庫遷移

```batch
cd backend
.venv\Scripts\python.exe run_migrations.py
```

### 3. 啟動服務

```batch
# 啟動後端
scripts\start-backend.bat

# 或啟動所有服務（新視窗）
scripts\start-all.bat
```

## 常見問題

### 問題 1: `No module named 'alembic'`

**原因：** 依賴未安裝或虛擬環境路徑不正確。

**解決方案：**
```batch
cd w2\db_query_1
uv pip install -e ".[dev]"
```

**驗證：**
```batch
cd backend
.venv\Scripts\python.exe -c "import alembic; print('OK')"
```

### 問題 2: `uv pip install` 失敗

**原因：** pyproject.toml 位置錯誤或 uv 版本問題。

**解決方案：**
```batch
# 確保在正確的目錄
cd w2\db_query_1
dir pyproject.toml    # 應該能看到這個檔案

# 更新 uv
pip install --upgrade uv

# 重新安裝
uv pip install -e ".[dev]"
```

### 問題 3: 循環導入錯誤

**原因：** schemas.py 的循環導入問題（已修復）。

**驗證修復：**
```batch
cd backend
.venv\Scripts\python.exe -c "from app.models import BaseSchema; print('OK')"
```

### 問題 4: MySQL 連接失敗

**測試連接：**
```batch
cd backend
.venv\Scripts\python.exe test_mysql_connection.py "mysql://user:pass@localhost:3306/dbname"
```

## 目錄結構

```
w2/db_query_1/                      # 項目根目錄（pyproject.toml 在這裡）
├── backend/
│   ├── .venv/                      # 虛擬環境
│   ├── app/                        # 應用代碼
│   ├── run_migrations.py           # 遷移腳本
│   └── test_mysql_connection.py    # MySQL 測試腳本
├── frontend/
├── scripts/
│   ├── install-dependencies.bat    # 安裝腳本
│   ├── start-backend.bat          # 啟動後端
│   └── start-all.bat              # 啟動所有服務
├── pyproject.toml                  # 依賴配置（重要！）
└── start.bat                       # 快速啟動選單
```

## 重要提示

1. **必須從 `w2/db_query_1/` 目錄運行 `uv pip install`**
   - 這是 `pyproject.toml` 所在的目錄
   - 不要從 `backend/` 目錄運行

2. **虛擬環境在 `backend/.venv/`**
   - 但安裝命令要從項目根目錄運行

3. **啟動腳本會自動檢查依賴**
   - 如果未安裝，會自動安裝
   - 如果失敗，會顯示錯誤訊息

## 完整重裝步驟

如果一切都不工作，完全重新安裝：

```batch
# 1. 刪除舊的虛擬環境
rmdir /s /q w2\db_query_1\backend\.venv

# 2. 重新安裝
cd w2\db_query_1
scripts\install-dependencies.bat

# 3. 運行遷移
cd backend
.venv\Scripts\python.exe run_migrations.py

# 4. 啟動服務
cd ..
scripts\start-backend.bat
```

## 快速啟動

使用快速啟動選單：

```batch
cd w2\db_query_1
start.bat
```

選擇：
- 選項 5: Install Dependencies（安裝依賴）
- 選項 6: Run Database Migrations（運行遷移）
- 選項 3: Start All（啟動所有服務）

