---
name: python-upgrade-deps
description: Upgrades Python dependency versions in pip-req.txt, requirements.txt, or pyproject.toml. Use when the user asks to upgrade a package version, update dependency, bump pip-req, or modify requirements.txt/pyproject.toml dependencies.
---

# Python 依赖版本升级

在 Python 项目中提升指定依赖包的版本，支持多种依赖文件格式（如 pip-req.txt、requirements.txt、pyproject.toml 等）。

## 触发场景

- 用户要求「升级某包版本」「更新 pip-req」「升级依赖」「修改 requirements」
- 用户指定包名和（可选）目标版本

## 依赖文件格式

| 文件 | 常见位置 | 行格式示例 |
|------|----------|------------|
| `pip-req.txt` | 项目根目录 | `package==1.2.3`、`package~=1.2.0`、`package>=1.2.0` |
| `requirements.txt` | 项目根目录 | 同上 |
| `pyproject.toml` | 项目根目录 | `dependencies = ["package~=1.2.0", ...]` |

## 版本约束符（PEP 440）

- `==`：精确版本
- `~=`：兼容版本（如 `~=1.2.0` 等价于 `>=1.2.0,<1.3.0`）
- `>=`：最低版本
- 升级后默认使用 `~=` 以保持兼容性，除非用户指定其他约束符

## 路径约定

本文中的 `<skill_dir>` 表示“当前 skill 目录”（即本 `SKILL.md` 所在目录）。后续路径均基于该约定展开，例如 `<skill_dir>/scripts/upgrade_dep.py`。

## 执行步骤

### 1. 确定目标版本

- **用户已指定版本**：直接使用
- **用户未指定**：可用 `pip index versions <package>` 或 PyPI 查询最新版本；内部项目可用内部 PyPI API
- **输出过滤**：用管道仅取最新版本，避免冗长列表传入上下文：
  ```bash
  pip index versions <package> 2>/dev/null | head -1 | sed -n 's/.*(\([^)]*\)).*/\1/p'
  ```

### 2. 定位依赖文件

按优先级检查项目根目录：

1. `pip-req.txt`（常用）
2. `requirements.txt`
3. `pyproject.toml`（`[project]` 下的 `dependencies` 或 `[project.optional-dependencies]`）

可同时存在多个文件，需在**所有包含该依赖**的文件中更新。

### 3. 修改规则

**pip-req.txt / requirements.txt**：

- 每行格式：`包名[extras] 约束符 版本 # 行尾注释`
- 包名匹配不区分大小写；`package[extra]` 与 `package` 视为同一包
- 跳过：空行、`#` 开头的注释、`-e` 可编辑安装、`-r` 引用
- 替换时保留行尾注释（`;` 或 `#` 后的内容）
- 新约束符默认 `~=`，如用户要求 `==` 则用 `==`

**pyproject.toml**：

- 依赖在 `dependencies = ["...", "..."]` 或 `[project.optional-dependencies.xxx]` 中
- 每项格式：`"package[extra]>=1.2.0"` 或 `'package~=1.2.0'`
- 用 `search_replace` 匹配并替换对应项，保持引号风格

### 4. 使用脚本（推荐）

```bash
python <skill_dir>/scripts/upgrade_dep.py <项目根目录> <包名> [目标版本]
```

- `目标版本` 省略时，脚本会尝试从 PyPI 获取最新版本（需网络）
- 成功输出：`Updated <文件名>: <包名> 旧版本 -> 新版本`
- 依赖：仅标准库；获取最新版本需 `pip` 可用或可访问 PyPI

## 示例

**升级 ArticleCommonLib 到 1.1.128**

pip-req.txt 修改前：
```
ArticleCommonLib~=1.1.127
```

修改后：
```
ArticleCommonLib~=1.1.128
```

**升级 pidl 到 0.6.37（用户指定 ==）**

```
pidl>=0.6.36  →  pidl==0.6.37
```

## 注意事项

- 修改后建议运行 `pip install -r pip-req.txt` 或 `pip install -e .` 验证安装
- `-e git+...` 形式的依赖需单独处理，一般不通过本技能升级
- 若同一包在多个 optional-dependencies 中出现，需全部更新
