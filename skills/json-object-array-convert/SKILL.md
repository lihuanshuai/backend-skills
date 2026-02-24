---
name: json-object-array-convert
description: 'Converts between JSON object and array using a user-specified key field. Object→array: each key becomes a field in the item; array→object: one field's value becomes the object key. Use when converting JSON object to array, array to object, or when the user asks for "对象转数组", "数组转对象", "key 转成字段".'
---

# JSON 对象与数组互转

支持两个方向，均需提供 **key 对应字段名**：

1. **对象 → 数组**：每个 key 作为一项，放入指定字段，value 与该字段合并为同一元素。
2. **数组 → 对象**：用每个元素中指定字段的值作为对象的 key，该字段从 value 中移除。

## 用户需提供

1. **JSON 文件路径**（或要转换的 JSON）
2. **key 字段名**：`id`、`key`、`name` 等
   - 对象→数组：该字段用于存放「原对象的 key」
   - 数组→对象：该字段的值作为「生成对象的 key」

## 使用方式

用脚本 `scripts/json_convert.py`，子命令 `to-array` / `to-object`（仅 Python 标准库）：

```bash
# 对象 → 数组
python scripts/json_convert.py <输入.json> to-array --key-field <字段名> [-o 输出.json]

# 数组 → 对象
python scripts/json_convert.py <输入.json> to-object --key-field <字段名> [-o 输出.json]
```

- **必选**：输入路径、子命令 `to-array`/`to-object`、`--key-field`（或 `-k`）。
- **可选**：`-o`/`--output` 输出文件；不指定则输出到 stdout。
- **可选**：`--indent N` 缩进（默认 2），0 为紧凑。

## 转换规则

**对象 → 数组**

- 输入：`{ "k1": {...}, "k2": {...} }`
- 输出：`[ { "<key字段名>": "k1", ...v1 }, { "<key字段名>": "k2", ...v2 } ]`
- value 为对象时与 key 合并；非对象时放入该元素的 `"value"` 键。

**数组 → 对象**

- 输入：`[ { "<key字段名>": "k1", ...rest1 }, { "<key字段名>": "k2", ...rest2 } ]`
- 输出：`{ "k1": rest1, "k2": rest2 }`（key 字段会从 value 中移除，避免重复）

## 示例

### 对象 → 数组

**输入** `data.json`：

```json
{ "a": { "name": "甲", "score": 90 }, "b": { "name": "乙", "score": 85 } }
```

```bash
python scripts/json_convert.py data.json to-array -k id -o result.json
```

**输出**：

```json
[
  { "id": "a", "name": "甲", "score": 90 },
  { "id": "b", "name": "乙", "score": 85 }
]
```

### 数组 → 对象

**输入** `list.json`：

```json
[
  { "id": "a", "name": "甲", "score": 90 },
  { "id": "b", "name": "乙", "score": 85 }
]
```

```bash
python scripts/json_convert.py list.json to-object -k id -o out.json
```

**输出**：

```json
{
  "a": { "name": "甲", "score": 90 },
  "b": { "name": "乙", "score": 85 }
}
```

## 注意事项

- 对象→数组时根节点须为对象；数组→对象时根节点须为数组。
- 数组→对象时，每个元素必须为对象且包含 key 字段，key 字段值须为字符串或数字。
- 编码建议 UTF-8，输出中文使用 `ensure_ascii=False`（脚本已默认）。
