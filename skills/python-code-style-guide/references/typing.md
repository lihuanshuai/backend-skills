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

## 3.4 TypedDict 构造形式

- 需要得到「满足某 `TypedDict` 形状」的值时，**优先**用 **`TypedDict` 子类以关键字解包构造**：`MyTypedDict(**args)`（`args` 为 `Mapping[str, Any]` 或与字段一致的 `dict` / 另一映射；字段与 `total` 语义以该 `TypedDict` 定义为准）
- 相对地，少用「裸字面量 `{...}` + 依赖推断/`cast`」作为常规写法；前者在调用点更明确「正在构造哪一种结构」，且便于类型检查器按类定义校验字段名与可空性
- 字面量仅在局部、字段极少且无需复用构造逻辑时可接受；一旦结构在多处出现或从变量/函数组装的映射构造，应统一为 `MyTypedDict(**...)`
- 仍须遵守项目 Python 版本与 `typing` / `typing_extensions` 的可用性；若运行时需在旧版本上兼容，以项目既有 `TypedDict` 引入方式为准

## 示例

```python
from typing import Any

def fetch_member(member_id: int, fields: list[str] | None = None) -> dict[str, Any] | None:
    ...
```

```python
from typing import TypedDict

class UserRow(TypedDict):
    id: int
    name: str

def row_from_mapping(parts: dict[str, int | str]) -> UserRow:
    # 优选：TypedDict 子类 + **，键与字段一致时类型检查器可对齐校验
    return UserRow(**parts)

def row_explicit() -> UserRow:
    return UserRow(id=1, name="ada")
```
