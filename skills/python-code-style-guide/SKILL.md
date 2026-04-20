---
name: python-code-style-guide
description: Provides a shared Python code style guide for common backend projects including local import rules variable naming conventions and type comment or annotation practices. Use when writing Python code reviewing style issues or standardizing code conventions across repositories.
---

# Python 代码风格规范（通用后端项目）

用于统一常见 Python 约束，降低跨仓库协作成本。覆盖 import、命名、类型标注、函数设计与可读性等常见规范。

## 路径约定

本文中的 `<skill_dir>` 表示当前 skill 目录（本 `SKILL.md` 所在目录）。后续路径说明均基于该约定，例如 `<skill_dir>/SKILL.md`。

## 使用场景

- 用户要求“按项目规范改代码”“统一代码风格”“补类型注释”
- 代码 review 出现风格分歧，需要统一判断口径
- 跨项目迁移代码，需要对齐命名与类型写法

## 1. Import 规范

### 1.1 顶部 import 为默认方式

- 常规依赖、标准库、项目内模块，默认都放在文件顶部
- 顺序建议：标准库 -> 三方库 -> 项目内模块（组间空行）
- 禁止无用 import；禁止 `from x import *`

### 1.2 局部 import（函数内 import）仅在以下场景允许

- **打破循环依赖**：模块级 import 会触发循环引用
- **降低冷启动开销**：仅限特别必要场景，且重依赖只在少量分支使用
- **环境隔离**：某依赖只在特定运行环境存在（如可选依赖）

局部 import 必须满足：

- 紧邻首次使用位置，不提前、不分散
- 加一行简短注释说明原因（如“避免循环依赖”）
- 不在高频循环体中重复 import

示例：

```python
def build_payload(data):
    # 局部导入用于避免循环依赖
    from .serializer import serialize_payload
    return serialize_payload(data)
```

## 2. 命名规范

- **变量/函数**：`snake_case`
- **类名**：`PascalCase`
- **常量**：`UPPER_SNAKE_CASE`
- **私有成员**：前缀 `_`（如 `_cache`）
- **布尔变量**：使用可读前缀，如 `is_`、`has_`、`can_`、`should_`

避免：

- `tmp`, `data2`, `foo`, `bar` 这类语义弱命名（短生命周期临时变量除外）
- 单字符命名泛滥（`i`, `j` 仅用于短循环索引）

推荐：

- 名称体现业务语义与单位，如 `retry_count`, `timeout_seconds`, `member_ids`

## 3. 类型注释与注解规范

### 3.0 先确认项目 Python 版本

- 在选择注解写法前，先确认项目运行时与 CI 的 Python 版本
- 若版本较低或存在多版本兼容约束，优先采用兼容写法（如 `typing.List`、`typing.Optional` 或保留 type comment）
- 仅在项目版本明确支持时，使用 `list[str]`、`X | None` 等较新语法

### 3.1 默认优先使用 Python 3 类型注解

- 新增 Python 3 代码优先写函数注解（参数与返回值）
- 公共函数、跨模块接口、复杂返回结构必须显式标注类型
- 容器类型优先使用内建泛型（如 `list[str]`、`dict[str, Any]`，按项目 Python 版本可用性调整）

### 3.2 Type Comment 使用边界

- 仅在必须兼容旧代码形态或工具链限制时使用 type comment
- 不要在同一函数混用“完整函数注解”和“函数 type comment”
- 历史 type comment 迁移时，优先统一为函数注解

### 3.3 Optional 与 None 约定

- 默认值为 `None` 的参数应显式写可空类型
- 返回值可能为空时，明确标注可空语义

示例：

```python
from typing import Any

def fetch_member(member_id: int, fields: list[str] | None = None) -> dict[str, Any] | None:
    ...
```

## 4. 函数与结构规范

- 单函数职责单一，避免“既查数据又拼装响应又打日志”
- 参数数量建议不超过 5 个；超过时优先封装对象或拆分函数
- 函数建议提供必要的文档注释（docstring），至少说明用途、关键参数与返回值语义（复杂副作用或异常也应说明）
- 尽早返回（guard clause）优于深层嵌套
- 异常处理要具体，避免裸 `except Exception` 吞错

## 5. 可读性与维护性规范

- 注释解释“为什么”，不要复述“做了什么”
- 日志必须包含关键上下文（业务主键、状态、错误原因）
- 魔法值提取为命名常量
- 复制粘贴超过两处时优先抽象复用

## 6. 常见禁忌清单

- 在模块顶层执行重逻辑（请求网络、扫描大量数据）
- 在循环体内做数据库或 RPC 的重复调用且无批量化
- 返回结构字段不稳定（同一函数不同分支 key 集合差异过大）
- 局部 import 无理由、无注释、分布混乱

## 7. 执行建议（Agent 工作流）

1. 先识别当前仓库 Python 版本与历史兼容约束
2. 再决定使用类型注解还是保留 type comment
3. 修改 import 与命名时，避免引入行为变更
4. 提交前运行项目既有 lint / test / pre-commit

## 注意事项

- 本规范是跨项目“共识基线”；若仓库已有更严格约束，以仓库本地规范优先
- 若用户明确要求保留旧风格（例如 Python 2/3 兼容 type comment），按用户要求执行并说明取舍
