---
name: com2ann-type-comment-to-hint
description: Converts Python type comments to type annotations (type hints) using com2ann. Use when migrating type comments to modern function annotations, when the user asks to convert type comments to type hints, or when modernizing Python 2/3 compatible type comments to Python 3 annotations.
---

# 将 Type Comment 转为 Type Hint（com2ann）

## 概述

使用 [com2ann](https://github.com/ilevkivskyi/com2ann) 将 Python 类型注释（type comments）自动转换为函数注解（type hints）。适用于从 Python 2/3 兼容写法迁移到纯 Python 3 注解风格。

## 前置条件

- **Python 3.8+**：com2ann 运行环境
- **com2ann**：`pip install com2ann`

## 基本用法

```bash
# 单文件，原地修改
com2ann path/to/file.py

# 单文件，输出到新文件
com2ann path/to/file.py -o output.py

# 整个目录，原地修改
com2ann path/to/dir/
```

## 常用选项

| 选项 | 说明 |
|------|------|
| `-i, --add-future-imports` | 在成功转换的文件中添加 `from __future__ import annotations`（推荐，便于 forward reference） |
| `-v, --python-minor-version` | 目标 Python 版本（如 4 表示 3.4），用于解析兼容语法 |
| `-w, --wrap-signatures N` | 函数签名超过 N 字符时换行 |
| `-n, --drop-none` | 将 `x = None  # type: int` 转为 `x: int = None` 时去掉 `= None` |
| `-e, --drop-ellipsis` | 将 `x = ...  # type: int` 转为 `x: int = ...` 时去掉 `= ...` |
| `-s, --silent` | 不打印转换摘要 |

## 推荐流程

0. **检查 com2ann 是否已安装**
   - 执行 `com2ann --help` 或 `which com2ann` 检查；
   - 若命令不存在或报错，**提示用户安装**：`pip install com2ann`，并说明需 Python 3.8+。

1. **确认目标**
   - 文件或目录为 Python 3 专用；
   - 若项目仍兼容 Python 2，需确认该目录/文件已不再在 Python 2 下运行。

2. **执行转换**
   ```bash
   com2ann -i path/to/file.py
   # 或目录
   com2ann -i path/to/module/
   ```

3. **验证**
   - 运行 `pre-commit run` 或项目既有类型检查（mypy、ruff 等）；
   - 若需兼容 Python 3.9 及以下，可加 `-v 9` 等，避免使用 `list[str]` 等 3.9+ 语法。

## 转换示例

**转换前（type comment）：**
```python
def get_movies(city_id, limit=8, poster_size="medium"):
    # type: (int, int, str) -> dict[str, Any]
    return {}
```

**转换后（type hint）：**
```python
def get_movies(city_id: int, limit: int = 8, poster_size: str = "medium") -> dict[str, Any]:
    return {}
```

## 注意事项

- **com2ann 未安装时**：若执行 `com2ann` 失败或命令不存在，提示用户运行 `pip install com2ann`（需 Python 3.8+）。
- com2ann 要求输入文件**无语法错误**，否则会失败。
- 若项目有 `pyproject.toml` 的 `per-file-ignores` 等忽略特定文件（如 PIDL 定义），可跳过这些文件，避免影响工具链。
- 转换后建议运行 pre-commit 或格式化工具，确保风格一致。
