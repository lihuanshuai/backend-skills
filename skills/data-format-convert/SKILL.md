---
name: data-format-convert
description: 数据格式转换与提取技能，覆盖 CSV 提取导出、YAML 与 JSON 互转、JSON 对象与数组互转。Use when 用户需要转换或提取数据格式，包括 CSV 转 YAML/JSON、YAML/JSON 互转、JSON 对象与数组互转。
---

# 数据格式转换与提取

## 概述

本技能用于常见数据格式的转换与提取，根据用户需求路由到具体子任务。覆盖三种场景：

1. **CSV 提取导出**：从 CSV 按列提取数据，导出为 YAML 或 JSON
2. **YAML / JSON 互转**：YAML 与 JSON 双向转换，支持指定字段类型
3. **JSON 对象 / 数组互转**：JSON 对象与数组双向转换，需指定 key 字段

## 路径约定

约定 `<skill_dir>` 为本技能所在目录。后续路径均基于该约定展开。

## 路由逻辑

根据用户描述判断子任务，读取对应参考文档并执行：

| 用户意图关键词 | 子任务 | 参考文档 | 脚本 |
|----------------|--------|----------|------|
| CSV 提取、CSV 导出、CSV 转 YAML/JSON | CSV 提取导出 | `<skill_dir>/references/csv-extract-export.md` | `<skill_dir>/scripts/csv_export.py` |
| YAML 转 JSON、JSON 转 YAML、yaml json 互转 | YAML / JSON 互转 | `<skill_dir>/references/yaml-json-convert.md` | `<skill_dir>/scripts/yaml_json_convert.py` |
| 对象转数组、数组转对象、key 转成字段 | JSON 对象 / 数组互转 | `<skill_dir>/references/json-object-array-convert.md` | `<skill_dir>/scripts/json_convert.py` |

若用户意图涉及多个子任务（如先 CSV 提取再 YAML 转换），按顺序依次执行。

## 依赖

- **Python 3.6+**
- **PyYAML**：CSV 提取导出（YAML 输出时）和 YAML / JSON 互转需要。安装：
  ```bash
  pip install -r <skill_dir>/scripts/requirements.txt
  ```
- JSON 对象 / 数组互转仅用标准库，无需额外依赖。

## References

各子任务的详细说明、用法与示例见 `<skill_dir>/references/` 下对应文档。