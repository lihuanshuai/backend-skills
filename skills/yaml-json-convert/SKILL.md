---
name: yaml-json-convert
description: Converts between YAML and JSON using a script. Supports YAML→JSON (to-json) and JSON→YAML (to-yaml), and optional field type coercion (e.g. field to int). Use when converting YAML to JSON, JSON to YAML, or when the user asks for "yaml json 互转", "指定字段转 int", "yaml 转 json", "json 转 yaml".
---

# YAML 与 JSON 互转

通过脚本实现 YAML 与 JSON 的双向转换，支持将指定字段转为指定类型（如 int）。需安装 PyYAML（见依赖）。

## 使用方式

用脚本 `scripts/yaml_json_convert.py`，子命令 `to-json` / `to-yaml`：

```bash
# YAML → JSON
python scripts/yaml_json_convert.py <输入文件> to-json [-o 输出.json] [--indent N] [-t 字段类型]

# JSON → YAML
python scripts/yaml_json_convert.py <输入文件> to-yaml [-o 输出.yaml] [-t 字段类型]
```

- **必选**：输入文件路径、子命令 `to-json` 或 `to-yaml`。
- **可选**：`-o`/`--output` 输出文件；不指定则输出到 stdout。
- **可选**（仅 to-json）：`--indent N` 缩进（默认 2），0 为紧凑。
- **可选**：`--field-types` / `-t` 指定字段类型，格式 `字段名:类型`，多个用逗号分隔。类型：`int`、`float`、`bool`、`str`。对结构中所有同名字段递归生效。

## 依赖

本技能脚本依赖 PyYAML，在技能目录下用 `requirements.txt` 声明。安装：

```bash
cd skills/yaml-json-convert && pip install -r requirements.txt
```

## 示例

**YAML → JSON**

```bash
python scripts/yaml_json_convert.py config.yaml to-json -o config.json
```

**JSON → YAML**

```bash
python scripts/yaml_json_convert.py data.json to-yaml -o data.yaml
```

**指定字段类型**（例如将 `group_id` 转为 int 再输出）：

```bash
python scripts/yaml_json_convert.py data.json to-yaml -t "group_id:int" -o data.yaml
```

输出到 stdout 时省略 `-o` 即可。

## 注意事项

- 输入格式由子命令决定：`to-json` 要求输入为合法 YAML，`to-yaml` 要求输入为合法 JSON。
- 编码使用 UTF-8；JSON 输出使用 `ensure_ascii=False`，YAML 使用 `allow_unicode=True`，中文不会转义。
