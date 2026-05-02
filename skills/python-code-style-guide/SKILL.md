---
name: python-code-style-guide
description: Provides a shared Python code style guide for common backend projects including local import rules variable naming conventions and type comment or annotation practices. Use when writing Python code reviewing style issues or standardizing code conventions across repositories.
---

# Python 代码风格规范（通用后端项目）

跨仓库共识基线；若某仓库已有更严约束，以仓库本地规范优先。

## 路径约定

`<skill_dir>` 表示本 skill 目录（本 `SKILL.md` 所在目录）。下文路径均相对该目录。

## references（按需深入）

主文档只保留「何时用、读哪份、一句话规则」。细则、示例与边界见：

| 主题 | 文件 |
| --- | --- |
| Import（顶层分组、局部 import、`TYPE_CHECKING`） | `<skill_dir>/references/import-guide.md` |
| 命名 | `<skill_dir>/references/naming.md` |
| 类型注解与 type comment | `<skill_dir>/references/typing.md` |
| 函数与结构 | `<skill_dir>/references/functions-and-structure.md` |
| 可读性与注释 / docstring | `<skill_dir>/references/readability.md` |
| 性能 | `<skill_dir>/references/performance.md` |
| 常见禁忌 | `<skill_dir>/references/anti-patterns.md` |
| Agent 执行顺序 | `<skill_dir>/references/agent-workflow.md` |

## 使用场景

- 用户要求「按项目规范改代码」「统一代码风格」「补类型注释」
- 代码 review 出现风格分歧，需要统一判断口径
- 跨项目迁移代码，需要对齐命名与类型写法

## 决策摘要（扫读）

- **Import**：默认顶层；分组顺序标准库 → 三方 → 项目内，排序以项目 ruff/isort 为准；禁止无用 import 与 `from x import *`。局部 import 仅用于循环依赖 / 冷启动隔离 / 可选依赖，须注释且勿放循环内。类型环优先 `TYPE_CHECKING`。详见 `<skill_dir>/references/import-guide.md`。
- **命名**：`snake_case` / `PascalCase` / `UPPER_SNAKE_CASE`；私有 `_` 前缀；布尔 `is_`/`has_` 等。详见 `<skill_dir>/references/naming.md`。
- **类型**：先确认 Python 版本；新代码优先函数注解；type comment 仅在兼容需要时使用。`TypedDict` 实例优先 `MyTypedDict(**args)` 构造，少用裸 `{...}` 依赖推断。详见 `<skill_dir>/references/typing.md`。
- **函数**：单一职责、参数不宜过多、具体异常、guard clause。详见 `<skill_dir>/references/functions-and-structure.md`。
- **可读性**：注释写「为什么」；中文 docstring/注释（除非仓库另有约定）。详见 `<skill_dir>/references/readability.md`。
- **性能**：慢查询与内存。详见 `<skill_dir>/references/performance.md`。
- **禁忌**：顶层重逻辑、循环内重复 IO、不稳定返回结构、滥用局部 import。详见 `<skill_dir>/references/anti-patterns.md`。
- **落地顺序**：详见 `<skill_dir>/references/agent-workflow.md`。

## 注意事项

- 若用户明确要求保留旧风格（例如 Python 2/3 兼容 type comment），按用户要求执行并说明取舍
