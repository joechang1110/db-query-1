"""
测试导出功能的脚本
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试数据
test_data = {
    "columns": [
        {"name": "id", "dataType": "integer"},
        {"name": "name", "dataType": "text"},
        {"name": "email", "dataType": "text"},
        {"name": "age", "dataType": "integer"}
    ],
    "rows": [
        {"id": 1, "name": "张三", "email": "zhangsan@example.com", "age": 25},
        {"id": 2, "name": "李四", "email": "lisi@example.com", "age": 30},
        {"id": 3, "name": "王五", "email": "wangwu@example.com", "age": 28},
        {"id": 4, "name": "赵六", "email": "zhaoliu@example.com", "age": 35}
    ],
    "format": "csv"
}

print("=" * 80)
print("测试导出API功能")
print("=" * 80)

# 测试CSV导出
print("\n1. 测试CSV导出...")
print("-" * 80)
test_data["format"] = "csv"
try:
    response = requests.post(
        f"{BASE_URL}/dbs/test_db/export",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        print("✓ CSV导出成功!")
        print(f"  - 文件名: {result['filename']}")
        print(f"  - 格式: {result['format']}")
        print(f"  - 数据预览 (前200字符):")
        print("  " + "-" * 76)
        print("  " + result['data'][:200].replace("\n", "\n  "))
        print("  " + "-" * 76)
    else:
        print(f"✗ CSV导出失败: {response.status_code}")
        print(f"  错误信息: {response.text}")
except Exception as e:
    print(f"✗ CSV导出异常: {str(e)}")

# 测试JSON导出
print("\n2. 测试JSON导出...")
print("-" * 80)
test_data["format"] = "json"
try:
    response = requests.post(
        f"{BASE_URL}/dbs/test_db/export",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        print("✓ JSON导出成功!")
        print(f"  - 文件名: {result['filename']}")
        print(f"  - 格式: {result['format']}")
        print(f"  - 数据预览:")
        print("  " + "-" * 76)
        # 解析并格式化JSON
        json_data = json.loads(result['data'])
        print("  " + json.dumps(json_data, indent=2, ensure_ascii=False)[:500].replace("\n", "\n  "))
        print("  " + "-" * 76)
    else:
        print(f"✗ JSON导出失败: {response.status_code}")
        print(f"  错误信息: {response.text}")
except Exception as e:
    print(f"✗ JSON导出异常: {str(e)}")

# 测试空数据导出
print("\n3. 测试空数据导出...")
print("-" * 80)
empty_data = {
    "columns": [{"name": "id", "dataType": "integer"}],
    "rows": [],
    "format": "csv"
}
try:
    response = requests.post(
        f"{BASE_URL}/dbs/test_db/export",
        json=empty_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        print("✓ 空数据导出成功!")
        print(f"  - 数据内容: '{result['data']}'")
    else:
        print(f"✗ 空数据导出失败: {response.status_code}")
except Exception as e:
    print(f"✗ 空数据导出异常: {str(e)}")

# 测试无效格式
print("\n4. 测试无效格式...")
print("-" * 80)
invalid_data = {
    "columns": [{"name": "id", "dataType": "integer"}],
    "rows": [{"id": 1}],
    "format": "xml"
}
try:
    response = requests.post(
        f"{BASE_URL}/dbs/test_db/export",
        json=invalid_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 400:
        print("✓ 无效格式正确拒绝!")
        print(f"  - 错误信息: {response.json()}")
    else:
        print(f"✗ 应该返回400错误，实际返回: {response.status_code}")
except Exception as e:
    print(f"✗ 测试异常: {str(e)}")

print("\n" + "=" * 80)
print("测试完成!")
print("=" * 80)
