## constitution
這是針對 ./db_query 項目的：
後端使用 Ergonomic Python 風格來編寫代碼，前端使用 TypeScript
前後端都要有嚴格的型別標註
使用 pydantic 來定義數據模型
所有後端生成的 JSON 數據，使用 camelCase 格式
不需要 authentication，任何用戶都可以使用

## 基本思路
這是一個資料庫查詢工具，使用者可以新增一個 db url，系統會連接到資料庫，取得資料庫的 metadata，接著將資料庫中的 table 與 view 資訊顯示出來。
之後使用者可以：
自行輸入 SQL 查詢
或透過自然語言產生 SQL 查詢


## 基本想法

資料庫連線字串與資料庫的 metadata 都會存儲到 SQLite 資料庫 中。我們可以根據 Postgres 的功能來查詢系統中的表與視圖資訊，然後使用 LLM 將這些資訊轉換成 JSON 格式，再存入 SQLite，這些資訊之後可以重複使用。
當使用者使用 LLM 產生 SQL 查詢 時，會把系統中表與視圖的資訊作為 context 傳遞給 LLM，讓 LLM 根據這些資訊來生成 SQL。
任何輸入的 SQL 語句都必須先經過 sqlparser 解析，確保語法正確，且只允許包含 SELECT 語句。若語法錯誤，需回傳錯誤訊息。
若查詢未包含 LIMIT 子句，系統會自動加入 LIMIT 1000。
輸出格式為 JSON，前端再將其組織為表格並顯示。

後端使用：Python（uv） / FastAPI / sqlglot / OpenAI SDK 實作
前端使用：React / Refine 5 / Tailwind CSS / Ant Design 實作，
SQL Editor 使用 Monaco Editor 來實作