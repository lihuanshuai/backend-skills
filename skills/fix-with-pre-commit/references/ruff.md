# ruff 修复参考

## 可自动 / 半自动修复

| 规则码 | 说明 | 修复方式 |
|--------|------|----------|
| UP009 | 移除多余 UTF-8 coding 声明 | 删除文件首行的 `# -*- coding: utf-8 -*-` 等声明 |
| C408 | `dict()` / `list()` / `tuple()` 改字面量 | 将 `dict(a=1)` 改为 `{"a": 1}`，`list()` 改为 `[]` 等 |
| SIM102 | 可合并的嵌套 `if` | 将 `if a: if b:` 合并为 `if a and b:` |
| UP004 | 移除无必要的 `__future__` import | 删除已为 Python 3 默认行为的 `from __future__ import ...` |
| I001 / I002 | import 排序与空白 | 运行 `ruff format` 或 `ruff check --fix --select I` 自动排序 |
| F401 | 未使用的 import | 删除该 import；若属于 `__init__.py` 的 re-export 则保留并加 `# noqa: F401` |
| F841 | 未使用的局部变量 | 删除变量或改为 `_` |

## 需人工判断

| 规则码 | 说明 | 原因 |
|--------|------|------|
| DTZ001 / DTZ002 / DTZ003 / DTZ005 / DTZ006 | `datetime.now()` 等无时区调用 | 需确认业务意图：是否应指定时区或使用 UTC |
| S101 | `assert` 在非测试代码 | 可能是业务逻辑约束，不可盲目移除 |
| TRY300 / TRY301 | try 块内建议提取或避免 return | 涉及流程重构，需理解上下文 |
| E501 | 行过长 | 可能需要重构表达式而非简单截断 |