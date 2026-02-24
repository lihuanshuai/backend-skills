#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON 对象与数组互转：对象→数组（key 写入指定字段）、数组→对象（用指定字段值作为 key）。
仅用标准库，无额外依赖。
"""
from __future__ import annotations

import argparse
import json
import sys


def object_to_array(data: dict, key_field: str) -> list:
    """将对象转为数组，key 放入 key_field 指定字段。"""
    result = []
    for k, v in data.items():
        if isinstance(v, dict):
            item = {key_field: k, **v}
        else:
            item = {key_field: k, "value": v}
        result.append(item)
    return result


def array_to_object(data: list, key_field: str) -> dict:
    """将数组转为对象，用每个元素中 key_field 的值作为对象的 key，该字段从 value 中移除。"""
    result = {}
    for item in data:
        if not isinstance(item, dict):
            raise ValueError(f"Array element must be object, got {type(item).__name__}")
        if key_field not in item:
            raise ValueError(f"Key field '{key_field}' not found in element: {item}")
        k = item[key_field]
        if isinstance(k, (dict, list)):
            raise ValueError(f"Key field value must be string or number, got {type(k).__name__}")
        rest = {kk: vv for kk, vv in item.items() if kk != key_field}
        result[k] = rest
    return result


def _write_output(out: dict | list, args: argparse.Namespace) -> int:
    kwargs = {"ensure_ascii": False, "indent": args.indent if args.indent else None}
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(out, f, **kwargs)
        except OSError as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            return 1
    else:
        json.dump(out, sys.stdout, **kwargs)
        if args.indent:
            print()
    return 0


def cmd_to_array(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print("Error: for to-array, root must be a JSON object.", file=sys.stderr)
        return 1

    out = object_to_array(data, args.key_field)
    return _write_output(out, args)


def cmd_to_object(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return 1

    if not isinstance(data, list):
        print("Error: for to-object, root must be a JSON array.", file=sys.stderr)
        return 1

    try:
        out = array_to_object(data, args.key_field)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return _write_output(out, args)


def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--key-field",
        "-k",
        type=str,
        required=True,
        metavar="NAME",
        help="to-array: 存放原 key 的字段名；to-object: 用作对象 key 的字段名",
    )
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
        help="JSON 缩进空格数，0 为紧凑输出（默认 2）",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="JSON 对象与数组互转：to-array 将对象转为数组，to-object 将数组转为对象。"
    )
    parser.add_argument(
        "input",
        type=str,
        help="输入的 JSON 文件路径",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_array = subparsers.add_parser("to-array", help="对象 → 数组，key 写入指定字段")
    _add_common_args(p_array)
    p_array.set_defaults(func=cmd_to_array)

    p_object = subparsers.add_parser("to-object", help="数组 → 对象，用指定字段值作为 key")
    _add_common_args(p_object)
    p_object.set_defaults(func=cmd_to_object)

    args = parser.parse_args()
    return args.func(parser, args)


if __name__ == "__main__":
    sys.exit(main())
