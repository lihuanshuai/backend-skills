# 类型注释与注解规范

## 3.0 先确认项目 Python 版本

- 在选择注解写法前，先确认项目运行时与 CI 的 Python 版本
- 若版本较低或存在多版本兼容约束，优先采用兼容写法（如 `typing.List`、`typing.Optional` 或保留 type comment）
- 仅在项目版本明确支持时，使用 `list[str]`、`X | None` 等较新语法

## 3.1 默认优先使用 Python 3 类型注解

- 新增 Python 3 代码优先写函数注解（参数与返回值）
- 公共函数、跨模块接口、复杂返回结构必须显式标注类型
- 容器类型优先使用内建泛型（如 `list[str]`、`dict[str, Any]`，按项目 Python 版本可用性调整）

## 3.2 Type Comment 使用边界

- 仅在必须兼容旧代码形态或工具链限制时使用 type comment
- 不要在同一函数混用「完整函数注解」和「函数 type comment」
- 历史 type comment 迁移时，优先统一为函数注解

## 3.3 Optional 与 None 约定

- 默认值为 `None` 的参数应显式写可空类型
- 返回值可能为空时，明确标注可空语义

## 示例

```python
from typing import Any

def fetch_member(member_id: int, fields: list[str] | None = None) -> dict[str, Any] | None:
    ...
```
