# Import 规范（详细）

## 默认规则

- 依赖放在文件顶部。
- 分组顺序为「标准库 → 三方库 → 项目内模块」，组间空行。
- 具体排序 **以项目 ruff/isort 配置为准**。
- 禁止无用 import 与 `from x import *`。

## 例外：函数内 import

仅当存在明确收益时使用：

- **打破循环依赖**
- **可证实的冷启动 / 重依赖隔离**
- **可选或环境相关依赖**

必须同时满足：

- **紧邻首次使用**
- **单行注释说明原因**
- **不在循环体内重复 import**

类型引用导致的环可优先用 `typing.TYPE_CHECKING`，将类型-only import 移出运行时路径。

## 示例

```python
def build_payload(data):
    # 局部导入用于避免循环依赖
    from .serializer import serialize_payload
    return serialize_payload(data)
```

## 反例（避免）

- 模块顶层无理由的局部 import、无注释。
- 在循环内重复 `import`。
- 用局部 import「掩盖」可顶层整理好的依赖结构，却无收益说明。
