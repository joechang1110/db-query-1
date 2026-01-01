"""
数据导出服务模块
支持将查询结果导出为多种格式（CSV、JSON等）
"""

import csv
import json
from datetime import datetime, date
from decimal import Decimal
from io import StringIO
from typing import Any, Dict, List, Optional
from enum import Enum


class ExportFormat(str, Enum):
    """支持的导出格式"""
    CSV = "csv"
    JSON = "json"


class ExportService:
    """数据导出服务"""

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """
        序列化值，处理特殊类型

        Args:
            value: 要序列化的值

        Returns:
            序列化后的值
        """
        if value is None:
            return None
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        else:
            return str(value)

    @staticmethod
    def export_to_csv(
        columns: List[Dict[str, Any]],
        rows: List[Dict[str, Any]],
        include_headers: bool = True
    ) -> str:
        """
        将查询结果导出为CSV格式

        Args:
            columns: 列定义列表，格式：[{"name": "id", "dataType": "integer"}, ...]
            rows: 数据行列表，格式：[{"id": 1, "name": "Alice"}, ...]
            include_headers: 是否包含表头

        Returns:
            CSV格式的字符串
        """
        if not rows:
            return ""

        # 提取列名
        column_names = [col["name"] for col in columns]

        # 创建StringIO对象
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=column_names,
            extrasaction='ignore'
        )

        # 写入表头
        if include_headers:
            writer.writeheader()

        # 写入数据行（序列化特殊类型）
        for row in rows:
            serialized_row = {
                key: ExportService._serialize_value(value)
                for key, value in row.items()
                if key in column_names
            }
            writer.writerow(serialized_row)

        return output.getvalue()

    @staticmethod
    def export_to_json(
        columns: List[Dict[str, Any]],
        rows: List[Dict[str, Any]],
        pretty_print: bool = True
    ) -> str:
        """
        将查询结果导出为JSON格式

        Args:
            columns: 列定义列表
            rows: 数据行列表
            pretty_print: 是否格式化输出

        Returns:
            JSON格式的字符串
        """
        # 序列化数据
        serialized_rows = []
        for row in rows:
            serialized_row = {
                key: ExportService._serialize_value(value)
                for key, value in row.items()
            }
            serialized_rows.append(serialized_row)

        # 构建导出对象
        export_data = {
            "columns": columns,
            "rows": serialized_rows,
            "rowCount": len(rows),
            "exportedAt": datetime.now().isoformat()
        }

        # 转换为JSON
        if pretty_print:
            return json.dumps(export_data, ensure_ascii=False, indent=2)
        else:
            return json.dumps(export_data, ensure_ascii=False)

    @staticmethod
    def export_data(
        columns: List[Dict[str, Any]],
        rows: List[Dict[str, Any]],
        format: ExportFormat,
        **options
    ) -> str:
        """
        统一的导出接口

        Args:
            columns: 列定义列表
            rows: 数据行列表
            format: 导出格式
            **options: 格式特定的选项

        Returns:
            导出的字符串数据
        """
        if format == ExportFormat.CSV:
            return ExportService.export_to_csv(
                columns,
                rows,
                include_headers=options.get("include_headers", True)
            )
        elif format == ExportFormat.JSON:
            return ExportService.export_to_json(
                columns,
                rows,
                pretty_print=options.get("pretty_print", True)
            )
        else:
            raise ValueError(f"Unsupported export format: {format}")


# 导出服务实例
export_service = ExportService()
