---
name: python-bump-version
description: Bumps Python package version in setup.py, setup.cfg, or pyproject.toml. Supports patch/minor/major bump. Use when the user asks to bump version, upgrade package version, release new version, or update version in setup.py/setup.cfg/pyproject.toml.
---

# Python 包版本提升

在 Python 项目中提升包版本号，支持 `setup.py`、`setup.cfg`、`pyproject.toml` 三种配置方式，以及 patch/minor/major 三种 bump 类型。

## 使用方式

- **触发场景**：用户要求「提升版本」「bump version」「发版」「升级包版本」、或指定要修改 `setup.py`/`setup.cfg`/`pyproject.toml` 中的版本号。
- **工作目录**：在项目根目录执行。

## 检测配置类型

按优先级检查项目根目录下是否存在以下文件，并确定版本所在位置：

| 文件 | 版本位置 | 示例 |
|------|----------|------|
| `pyproject.toml` | `[project]` 下的 `version` | `version = "1.2.3"` |
| `setup.cfg` | `[metadata]` 下的 `version` | `version = 1.2.3` |
| `setup.py` | 变量赋值或 `setup(version=...)` | `version = '1.2.3'` 或 `setup(version='1.2.3')` |

若同时存在多个文件（如既有 `setup.py` 又有 `pyproject.toml`），以 `pyproject.toml` 为准；否则以 `setup.cfg` 为准；最后才用 `setup.py`。只更新**一个**文件中的版本，避免重复。

## Bump 类型

- **patch**（默认）：`1.2.3` → `1.2.4`
- **minor**：`1.2.3` → `1.3.0`
- **major**：`1.2.3` → `2.0.0`

版本格式假定为 `x.y.z`（x、y、z 为数字）；若为 `x.y` 则按 `x.y.0` 处理，bump 后补齐。

## 执行步骤

### 1. pyproject.toml

在 `[project]` 下查找 `version = "..."` 或 `version = '...'`，用正则替换：

```python
# 匹配: version = "1.2.3" 或 version = '1.2.3'
import re
pattern = r'(version\s*=\s*["\'])(\d+)\.(\d+)\.(\d+)(["\'])'
# 替换时根据 bump 类型计算新版本，保留前后引号
```

### 2. setup.cfg

在 `[metadata]` 段下查找 `version = x.y.z`（无引号或带引号均可）：

```ini
[metadata]
name = my-package
version = 1.2.3
```

用 `search_replace` 将 `version = 1.2.3` 替换为新版本。

### 3. setup.py

两种常见写法：

**写法 A**：变量赋值 + setup 引用

```python
version = '1.1.127'
setup(..., version=version, ...)
```

需同时更新变量赋值行和 `setup()` 中的 `version` 参数（若为字面量）。若 `setup(version=version)` 引用变量，则**只改变量赋值行**。

**写法 B**：直接字面量

```python
setup(..., version='1.2.3', ...)
```

只改 `setup()` 中的 `version` 关键字参数。

用 `search_replace` 时注意：
- 匹配 `version = 'x.y.z'` 或 `version = "x.y.z"`（变量赋值）
- 匹配 `version='x.y.z'` 或 `version="x.y.z"`（setup 关键字）
- 保持原有引号风格（单引号/双引号）不变。

### 4. 使用脚本（可选）

若项目结构复杂或需批量处理，可执行技能目录下的脚本：

```bash
python scripts/bump_version.py <项目根目录> [patch|minor|major]
```

**参数**：
- `项目根目录`：必选，包含 setup.py / setup.cfg / pyproject.toml 的项目根路径（可用 `.` 表示当前目录）
- `patch|minor|major`：可选，默认 `patch`

**行为**：
- 按优先级检测：`pyproject.toml`（需含 `[project]` 且 `version`）→ `setup.cfg`（需含 `[metadata]`）→ `setup.py`
- 仅更新**一个**文件，原地写入
- 成功时输出：`Updated <文件名>: 旧版本 -> 新版本`
- 失败时输出到 stderr 并 exit code 1（如未找到版本、目录不存在等）

**依赖**：仅用 Python 3 标准库，无需额外安装。

**示例**（从技能目录执行，或传入脚本绝对路径）：

```bash
# 在待 bump 的项目根目录执行（脚本用绝对路径）
python ~/.cursor/skills/backend-skills/skills/python-bump-version/scripts/bump_version.py . patch

# 或先 cd 到技能目录，再指定项目路径
cd ~/.cursor/skills/backend-skills/skills/python-bump-version
python scripts/bump_version.py /path/to/my-project minor
```

## 示例

**patch bump（1.2.3 → 1.2.4）**

- pyproject.toml: `version = "1.2.3"` → `version = "1.2.4"`
- setup.cfg: `version = 1.2.3` → `version = 1.2.4`
- setup.py: `version = '1.2.3'` → `version = '1.2.4'`

**minor bump（1.2.3 → 1.3.0）**

- pyproject.toml: `version = "1.2.3"` → `version = "1.3.0"`

## 注意事项

- 仅修改版本号，不改动其他内容。
- 若版本格式非 `x.y.z`（如含 `dev`、`post`、`a`、`b` 等后缀），需先确认用户意图，或只处理主版本部分。
- 修改后建议运行 `pre-commit` 或项目既有检查，确保无格式问题。
