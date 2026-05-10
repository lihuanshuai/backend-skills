#!/usr/bin/env python3
"""
从 CSV 中按指定列提取数据，输出为 YAML 或 JSON 对象列表。
字段映射格式：--fields "列名:键" 或 "列名:键:类型"，类型可选 int/float/bool/str。
"""
import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

try:
    import yaml as _yaml_mod
except ImportError:
    _yaml_mod = None  # 仅输出 YAML 时需要

CONVERTERS: Dict[str, Callable[[str], Any]] = {}


def _to_bool(s: str) -> bool:
    v = s.strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    raise ValueError(f"无法解析为 bool: {s!r}")


def _init_converters() -> None:
    global CONVERTERS
    if CONVERTERS:
        return
    CONVERTERS.update({
        "str": lambda s: s.strip(),
        "int": lambda s: int(s.strip()),
        "float": lambda s: float(s.strip()),
        "bool": _to_bool,
    })


def parse_mapping(fields_arg: str) -> List[Tuple[str, str, str]]:
    """
    解析映射为 [(csv列名, 输出键, 类型名), ...]。
    格式: "列名:键" 或 "列名:键:类型"，类型默认为 str。
    """
    _init_converters()
    result: List[Tuple[str, str, str]] = []
    for part in fields_arg.split(","):
        part = part.strip()
        if not part:
            continue
        parts = part.split(":")
        if len(parts) == 2:
            csv_col, out_key = parts[0].strip(), parts[1].strip()
            type_name = "str"
        elif len(parts) >= 3:
            csv_col = parts[0].strip()
            out_key = parts[1].strip()
            type_name = parts[2].strip().lower() or "str"
        else:
            continue
        if not csv_col or not out_key:
            continue
        if type_name not in CONVERTERS:
            raise ValueError(
                f"不支持的类型 {type_name!r}，可选: {list(CONVERTERS.keys())}"
            )
        result.append((csv_col, out_key, type_name))
    return result


def csv_to_list_of_dicts(
    csv_path: Path,
    mapping: List[Tuple[str, str, str]],
    encoding: str = "utf-8-sig",
) -> List[Dict[str, Any]]:
    """
    读取 CSV，按 mapping 提取每行并做类型转换，返回对象列表。
    空单元格为 None。
    """
    rows: List[Dict[str, Any]] = []
    with open(csv_path, encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return rows
        fieldnames = list(reader.fieldnames)
        for csv_col, _out_key, _ in mapping:
            if csv_col not in fieldnames:
                raise ValueError(f"CSV 中不存在列: {csv_col!r}。可用列: {fieldnames}")
        for row in reader:
            obj: Dict[str, Any] = {}
            for csv_col, out_key, type_name in mapping:
                raw = row.get(csv_col, "")
                value: Any
                if raw is None or (isinstance(raw, str) and raw.strip() == ""):
                    value = None
                else:
                    conv = CONVERTERS[type_name]
                    try:
                        value = conv(raw)
                    except (ValueError, TypeError) as e:
                        raise ValueError(
                            f"列 {csv_col!r} 转为 {type_name} 失败: {raw!r} -> {e}"
                        ) from None
                obj[out_key] = value
            rows.append(obj)
    return rows


def serialize(rows: List[Dict[str, Any]], fmt: Literal["yaml", "json"]) -> str:
    """将对象列表序列化为 YAML 或 JSON 字符串。"""
    if fmt == "json":
        return json.dumps(rows, ensure_ascii=False, indent=2)
    if fmt == "yaml":
        if _yaml_mod is None:
            print(
                "Error: PyYAML required for YAML output. Install: pip install -r requirements.txt (from skill dir)",
                file=sys.stderr,
            )
            sys.exit(1)
        return _yaml_mod.dump(
            rows,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
    raise ValueError(f"不支持的格式: {fmt!r}")


def get_format_from_path(path: Path) -> Literal["yaml", "json"]:
    """根据文件扩展名推断格式。"""
    suf = path.suffix.lower()
    if suf == ".json":
        return "json"
    if suf in (".yaml", ".yml"):
        return "yaml"
    return "yaml"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从 CSV 提取指定列，输出为 YAML 或 JSON 对象列表。"
    )
    parser.add_argument(
        "csv_path",
        type=Path,
        help="CSV 文件路径",
    )
    parser.add_argument(
        "--fields",
        "-f",
        required=True,
        metavar="MAPPING",
        help='映射，格式 "列名:键" 或 "列名:键:类型"。类型可选: int, float, bool, str（默认）',
    )
    parser.add_argument(
        "--format",
        choices=("yaml", "json"),
        default=None,
        help="输出格式。未指定时：若用了 -o 则按扩展名推断，否则为 yaml",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="输出文件路径；不指定则输出到 stdout",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="CSV 文件编码（默认 utf-8-sig，自动去除 BOM）",
    )
    args = parser.parse_args()

    if not args.csv_path.is_file():
        print(f"错误: 文件不存在 {args.csv_path}", file=sys.stderr)
        return 1

    try:
        mapping = parse_mapping(args.fields)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1
    if not mapping:
        print("错误: --fields 至少需要一对 列名:键 或 列名:键:类型", file=sys.stderr)
        return 1

    if args.format is not None:
        fmt: Literal["yaml", "json"] = args.format
    elif args.output is not None:
        fmt = get_format_from_path(args.output)
    else:
        fmt = "yaml"

    if fmt == "yaml":
        try:
            import yaml  # noqa: F401
        except ImportError:
            print("YAML 输出需要 PyYAML: pip install pyyaml", file=sys.stderr)
            return 1

    try:
        rows = csv_to_list_of_dicts(args.csv_path, mapping, args.encoding)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

    out = serialize(rows, fmt)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out, end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
