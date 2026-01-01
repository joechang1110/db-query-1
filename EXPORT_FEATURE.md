# 数据导出功能使用指南

## 功能概述

本项目新增了强大的数据导出功能，允许用户将查询结果导出为多种格式（CSV、JSON），并提供了多种便捷的导出方式。

## 主要功能

### 1. 支持的导出格式

- **CSV格式** - 适合在Excel、Google Sheets等工具中使用
- **JSON格式** - 适合程序化处理和API集成

### 2. 三种导出方式

#### 方式一：结果表格中的导出按钮

在查询执行完成后，结果表格右上角会显示"Export Data"按钮：

1. 点击"Export Data"按钮
2. 从下拉菜单中选择导出格式：
   - Export as CSV
   - Export as JSON
3. 文件将自动下载到本地

#### 方式二：查询后自动提示

每次查询成功执行后，系统会自动弹出通知提示：

1. 通知显示查询结果的行数
2. 提供两个快捷按钮：
   - "Export CSV" - 一键导出为CSV格式
   - "Export JSON" - 一键导出为JSON格式
3. 点击任一按钮即可直接导出，无需额外操作

#### 方式三：一键查询并导出

在SQL编辑器区域，除了常规的"Execute Query"按钮外，还提供了"Execute & Export"下拉按钮：

1. 点击"Execute & Export"按钮
2. 选择导出格式：
   - Execute & Export CSV
   - Execute & Export JSON
3. 系统将自动执行查询并在完成后立即导出结果

这种方式特别适合需要频繁导出数据的场景。

## 技术实现

### 后端架构

#### 导出服务 (`backend/app/services/export.py`)

- `ExportService` 类提供统一的导出接口
- 支持CSV和JSON两种格式
- 自动处理特殊数据类型（日期、Decimal、JSON对象等）
- 提供数据序列化功能

#### API端点 (`/api/v1/dbs/{name}/export`)

```http
POST /api/v1/dbs/{name}/export
Content-Type: application/json

{
  "columns": [
    {"name": "id", "dataType": "integer"},
    {"name": "name", "dataType": "text"}
  ],
  "rows": [
    {"id": 1, "name": "张三"},
    {"id": 2, "name": "李四"}
  ],
  "format": "csv",  // 或 "json"
  "filename": "my_export.csv"  // 可选
}
```

**响应格式：**

```json
{
  "data": "id,name\n1,张三\n2,李四\n",
  "format": "csv",
  "filename": "query_result_20260101_123456.csv"
}
```

### 前端实现

#### ResultTable组件更新

- 添加了Export按钮和格式选择下拉菜单
- 监听自定义导出事件以支持通知触发的导出
- 使用Blob API创建下载链接

#### 查询执行页面增强

- 集成了自动提示通知
- 添加了"Execute & Export"功能
- 通过自定义事件实现组件间通信

## 使用示例

### 示例1：导出用户数据

```sql
SELECT id, name, email, created_at
FROM users
WHERE status = 'active'
LIMIT 100;
```

执行后点击"Export as CSV"，将得到：

```csv
id,name,email,created_at
1,张三,zhangsan@example.com,2024-01-01T10:00:00
2,李四,lisi@example.com,2024-01-02T11:30:00
...
```

### 示例2：导出统计数据为JSON

```sql
SELECT category, COUNT(*) as count, AVG(price) as avg_price
FROM products
GROUP BY category;
```

导出JSON格式将包含完整的元数据：

```json
{
  "columns": [
    {"name": "category", "dataType": "text"},
    {"name": "count", "dataType": "integer"},
    {"name": "avg_price", "dataType": "numeric"}
  ],
  "rows": [
    {"category": "Electronics", "count": "150", "avg_price": "299.99"},
    {"category": "Books", "count": "300", "avg_price": "19.99"}
  ],
  "rowCount": 2,
  "exportedAt": "2026-01-01T12:34:56.789012"
}
```

## 特殊数据类型处理

导出服务会自动处理以下特殊数据类型：

| 数据类型 | 处理方式 | 示例 |
|---------|---------|------|
| `null/undefined` | 导出为空值 | `NULL` 或 `null` |
| `datetime` | ISO 8601格式 | `2024-01-01T10:00:00` |
| `Decimal` | 转换为浮点数 | `123.45` |
| `JSON对象/数组` | JSON字符串化 | `"{\"key\":\"value\"}"` |
| `boolean` | 字符串 | `true` / `false` |

## 文件命名规则

如果没有指定文件名，系统会自动生成带时间戳的文件名：

```
query_result_YYYYMMDD_HHMMSS.csv
query_result_YYYYMMDD_HHMMSS.json
```

例如：
- `query_result_20260101_123456.csv`
- `query_result_20260101_123456.json`

## API测试

使用curl测试导出API：

```bash
# 测试CSV导出
curl -X POST "http://localhost:8000/api/v1/dbs/my_database/export" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": [{"name": "id", "dataType": "integer"}],
    "rows": [{"id": 1}, {"id": 2}],
    "format": "csv"
  }'

# 测试JSON导出
curl -X POST "http://localhost:8000/api/v1/dbs/my_database/export" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": [{"name": "id", "dataType": "integer"}],
    "rows": [{"id": 1}, {"id": 2}],
    "format": "json"
  }'
```

## 注意事项

1. **大数据集导出**：对于大量数据，建议使用LIMIT限制结果集大小
2. **中文编码**：CSV文件默认使用UTF-8编码，在Excel中打开可能需要手动指定编码
3. **浏览器限制**：非常大的导出文件可能受到浏览器内存限制
4. **文件格式选择**：
   - CSV适合表格数据和数据分析
   - JSON适合API集成和程序化处理

## 故障排除

### 导出失败

如果导出失败，请检查：
1. 查询是否成功执行
2. 浏览器控制台是否有错误信息
3. 网络连接是否正常
4. 后端服务是否正常运行

### 文件无法下载

1. 检查浏览器的下载权限设置
2. 确认没有被弹窗拦截器阻止
3. 尝试更换浏览器

## 未来改进计划

- [ ] 支持更多导出格式（Excel、XML等）
- [ ] 添加自定义导出选项（字段选择、排序等）
- [ ] 支持大数据集的流式导出
- [ ] 添加导出任务队列和后台处理
- [ ] 提供导出历史记录

## 相关文件

### 后端文件
- `backend/app/services/export.py` - 导出服务实现
- `backend/app/api/v1/queries.py` - 导出API端点

### 前端文件
- `frontend/src/components/ResultTable.tsx` - 结果表格和导出按钮
- `frontend/src/pages/queries/execute.tsx` - 查询执行页面
- `frontend/src/services/api.ts` - API调用
- `frontend/src/types/query.ts` - 类型定义

## 反馈与支持

如果您在使用导出功能时遇到任何问题或有改进建议，欢迎通过以下方式联系我们：

- 提交GitHub Issue
- 发送邮件至项目维护者

---

*最后更新：2026-01-01*
