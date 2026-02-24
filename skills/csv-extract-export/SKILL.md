---
name: csv-extract-export
description: Extracts specified CSV columns into a list of objects and exports as YAML or JSON. Field mapping uses "col:key" or "col:key:type" (types int/float/bool/str). Use when converting CSV to YAML/JSON, extracting columns to structured data, or when the user asks to export CSV fields as YAML or JSON.
---

# CSV 提取导出为 YAML / JSON

从 CSV 中按用户指定的列提取数据，组成对象列表并导出为 **YAML** 或 **JSON**。列名与输出键、类型的对应由用户提供。

## 使用方式

用脚本 `scripts/csv_export.py` 执行转换：

```bash
python scripts/csv_export.py <csv_path> --fields <映射> [--format yaml|json] [-o 输出路径]
```

**映射格式**：`列名:键` 或 `列名:键:类型`，多个用逗号分隔。不写类型时默认为字符串。

**支持类型**：`int`、`float`、`bool`、`str`。bool 接受 1/0、true/false、yes/no（不区分大小写）。

**输出格式**：
- `--format yaml` 或 `--format json` 显式指定；
- 若未指定但使用了 `-o`，则根据扩展名推断（`.json` → JSON，`.yaml`/`.yml` → YAML）；
- 若未指定且无 `-o`，默认为 YAML。

## 依赖

输出 YAML 时脚本依赖 PyYAML，在技能目录下用 `requirements.txt` 声明。安装：

```bash
cd skills/csv-extract-export && pip install -r requirements.txt
```

仅输出 JSON 时无需安装。

## 示例

导出为 YAML（默认）：

```bash
python scripts/csv_export.py feed_info.csv --fields "小组id:id:int,小马名称:horse_name" --output result.yaml
```

导出为 JSON：

```bash
python scripts/csv_export.py feed_info.csv --fields "小组id:id:int,小马名称:horse_name" --format json --output result.json
```

或仅写 `-o result.json`，脚本会根据扩展名自动用 JSON：

```bash
python scripts/csv_export.py feed_info.csv --fields "小组id:id:int,小马名称:horse_name" -o result.json
```

输出到 stdout 且要 JSON 时显式加 `--format json`：

```bash
python scripts/csv_export.py feed_info.csv --fields "小组id:id:int,小马名称:horse_name" --format json
```

## 用户需提供

1. **CSV 文件路径**
2. **字段映射**：列名 → 输出键（可选 `:类型`），格式 `列名1:键1,列名2:键2:类型,...`
3. **输出格式**（可选）：yaml 或 json；或通过 `-o` 的文件扩展名推断

## 输出示例

YAML（`--format yaml` 或 `-o out.yaml`）：

```yaml
- id: 368401
  horse_name: 蘿蔔
- id: 733403
  horse_name: 奥米伽
```

JSON（`--format json` 或 `-o out.json`）：

```json
[
  {
    "id": 368401,
    "horse_name": "蘿蔔"
  },
  {
    "id": 733403,
    "horse_name": "奥米伽"
  }
]
```

空单元格在两种格式中均为 `null`。

## 依赖

- Python 3.6+
- **JSON**：仅用标准库 `json`，无额外依赖。
- **YAML**：需安装 PyYAML（`pip install pyyaml`）。仅在选择 YAML 输出时才需要。

CSV 默认按 `utf-8-sig` 读取（自动去除 BOM，适合 Excel 导出的 CSV）。
