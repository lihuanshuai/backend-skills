#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YAML 与 JSON 互转。依赖 PyYAML：pip install pyyaml
"""
from __future__ import annotations

import argparse
import json
import sys

try:
    import yaml
except ImportError:
    print(
        "Error: PyYAML required. Install: pip install -r requirements.txt (from skill dir)",
        file=sys.stderr,
    )
    sys.exit(1)

CONVERTERS = {
    "int": lambda v: int(v) if v is not None else None,
    "float": lambda v: float(v) if v is not None else None,
    "str": lambda v: str(v) if v is not None else None,
    "bool": lambda v: _to_bool(v) if v is not None else None,
}


def _to_bool(v):  # noqa: ANN001, ANN202
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("1", "true", "yes", "on"):
        return True
    if s in ("0", "false", "no", "off"):
        return False
    raise ValueError(f"无法解析为 bool: {v!r}")


def _parse_field_types(s: str) -> dict[str, str]:
    """解析 --field-types 'a:int,b:float' 为 {'a':'int','b':'float'}"""
    if not s or not s.strip():
        return {}
    out = {}
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            continue
        key, typ = part.split(":", 1)
        key, typ = key.strip(), typ.strip().lower()
        if key and typ in CONVERTERS:
            out[key] = typ
    return out


def _apply_field_types(data, field_types: dict[str, str]) -> None:
    """递归遍历，对字典中指定 key 按 field_types 转换类型（原地修改）。"""
    if not field_types:
        return
    if isinstance(data, dict):
        for k, t in field_types.items():
            if k in data:
                try:
                    data[k] = CONVERTERS[t](data[k])
                except (ValueError, TypeError) as e:
                    raise ValueError(f"字段 {k!r} 转为 {t} 失败: {data[k]!r} -> {e}") from e
        for v in data.values():
            _apply_field_types(v, field_types)
    elif isinstance(data, list):
        for item in data:
            _apply_field_types(item, field_types)


def cmd_to_json(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1
    except yaml.YAMLError as e:
        print(f"Invalid YAML: {e}", file=sys.stderr)
        return 1

    if data is None:
        data = {}

    field_types = getattr(args, "field_types", None) or {}
    try:
        _apply_field_types(data, field_types)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    kwargs = {"ensure_ascii": False, "indent": args.indent if args.indent else None}
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(data, f, **kwargs)
        except OSError as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            return 1
    else:
        json.dump(data, sys.stdout, **kwargs)
        if args.indent:
            print()
    return 0


def cmd_to_yaml(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return 1

    field_types = getattr(args, "field_types", None) or {}
    try:
        _apply_field_types(data, field_types)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    kwargs = {"default_flow_style": False, "allow_unicode": True, "sort_keys": False}
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                yaml.dump(data, f, **kwargs)
        except OSError as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            return 1
    else:
        print(yaml.dump(data, **kwargs), end="")
    return 0


def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        metavar="FILE",
        help="输出文件路径；不指定则输出到 stdout",
    )
    p.add_argument(
        "--indent",
        type=int,
        default=2,
        metavar="N",
        help="仅 to-json 有效：JSON 缩进空格数，0 为紧凑（默认 2）",
    )
    p.add_argument(
        "--field-types",
        "-t",
        type=str,
        default="",
        metavar="SPEC",
        help="指定字段类型，格式 字段名:类型，多个用逗号分隔。类型: int, float, bool, str。递归作用于所有同名字段。",
    )


def _parse_field_types_arg(s: str) -> dict[str, str]:
    return _parse_field_types(s) if s else {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="YAML 与 JSON 互转。依赖 PyYAML（pip install pyyaml）。"
    )
    parser.add_argument("input", type=str, help="输入文件路径（YAML 或 JSON）")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_json = subparsers.add_parser("to-json", help="YAML → JSON")
    _add_common(p_json)
    p_json.set_defaults(func=cmd_to_json)

    p_yaml = subparsers.add_parser("to-yaml", help="JSON → YAML")
    _add_common(p_yaml)
    p_yaml.set_defaults(func=cmd_to_yaml)

    args = parser.parse_args()
    args.field_types = _parse_field_types_arg(getattr(args, "field_types", "") or "")
    return args.func(parser, args)


if __name__ == "__main__":
    sys.exit(main())
