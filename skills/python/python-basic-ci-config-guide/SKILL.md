---
name: python-basic-ci-config-guide
description: Guide Python projects to add or migrate basic CI code quality config including ruff mypy pre-commit pyproject.toml and legacy black isort flake8 replacement.
---

# Python 基础 CI 配置指南

约定 `<skill_dir>` 为本技能所在目录。

## 概述

本技能用于给 Python 项目新增或迁移基础代码质量检查配置，覆盖本地 `pre-commit` 与 CI 中常见的 lint、format、type-check 配置。

适用场景：

- **新增配置**：新项目初始化、旧项目补齐基础检查、跨仓统一代码检查基线。
- **迁移配置**：将已有 black、isort、flake8、autoflake 等工具迁移到 ruff，避免重复规则与格式化冲突。
- **CI 对齐**：同步更新 `pyproject.toml`、`.pre-commit-config.yaml`、依赖文件、CI 脚本和项目 README。

基础工具组合：

- `ruff`：lint、import 排序与 format。
- `mypy`：静态类型检查。
- `pre-commit`：本地提交前检查。

## 总体流程

1. 确认项目根目录和现有配置：`pyproject.toml`、`.pre-commit-config.yaml`、依赖文件、CI 配置、README。
2. 判断任务类型：
   - 没有基础检查配置时，走「新增配置场景」。
   - 已有 black、isort、flake8、autoflake 或旧 ruff 配置时，走「迁移配置场景」。
3. 合并模板或迁移配置，避免重复 hook、重复 `[tool.*]` 配置与重复依赖。
4. 更新 CI 配置和项目 README，确保本地与 CI 使用同一套命令。
5. 用变更文件或少量抽样文件验证，不默认全量格式化历史代码。

## 新增配置场景

### 1. 更新 `.pre-commit-config.yaml`

若项目没有 `.pre-commit-config.yaml`，可从模板创建；若已存在，合并模板中的 repo 与 hooks。

模板位置：

- `<skill_dir>/references/pre-commit-config-template.yaml`

默认包含：

- `pre-commit-hooks` 基础文件检查。
- `mirrors-mypy` 的 `mypy` hook。
- `ruff-pre-commit` 的 `ruff-check` 与 `ruff-format` 两个 hook。

注意：

- `ruff-check` 用于 lint 与自动修复，`ruff-format` 用于格式化；不要只配置单个旧式 `ruff` hook。
- 模板默认只启用 `I` 规则做 import 排序；`UP` 规则仅适用于 Python 3-only 项目。
- hook 版本优先与团队现有仓库保持一致；模板版本只是基础参考。

### 2. 更新 `pyproject.toml`

若项目没有 `pyproject.toml`，先创建基础文件；若已存在，合并模板中的配置段。

模板位置：

- `<skill_dir>/references/pyproject-template.toml`

默认包含：

- `[tool.ruff]`
- `[tool.ruff.lint]`
- `[tool.mypy]`

建议：

- `line-length`、`exclude`、`ignore` 按项目现有风格微调。
- mypy 初始落地可保留 `ignore_missing_imports = true` 作为过渡，再按项目逐步收紧。
- 如需格式化时保留既有引号风格，可补充：

```toml
[tool.ruff.format]
quote-style = "preserve"
```

### 3. 补充依赖与 README

- 在项目依赖文件中加入本地和 CI 实际会使用的工具，例如 `ruff`、`mypy`、`pre-commit`。
- 若项目将 CI 检查依赖拆到独立文件，按现有约定新增或更新对应 reqs 文件。
- 更新项目 `README.md`，说明常用命令：

```bash
pre-commit install
pre-commit run --files <changed_file_1.py> <changed_file_2.py>
ruff check .
ruff format --check .
mypy <package_or_module>
```

## 迁移配置场景

### 1. 迁移 `.pre-commit-config.yaml`

删除以下 repo 及对应 hooks（若存在）：

- `PyCQA/isort`
- `psf/black`
- `PyCQA/flake8`
- 可选：`PyCQA/autoflake`

新增或更新 ruff 配置：

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.15.2
  hooks:
  - id: ruff-check
    args: [--fix, --extend-select, "I", --unsafe-fixes]
  - id: ruff-format
```

说明：

- `--extend-select, "I"` 用 ruff 覆盖 import 排序。
- `UP` 规则仅限 Python 3 环境使用；如果项目仍需兼容 Python 2 或混合运行时，不要启用 `UP`。
- 仅在确认项目为 Python 3-only 后，才可将参数调整为 `--extend-select, "I,UP"` 以启用部分语法升级类修复。
- `--unsafe-fixes` 只在项目接受自动替换语义风险时保留；若项目保守，可先去掉。
- 若项目已有 ruff，只需调整为 `ruff-check` 与 `ruff-format` 双 hook，并对齐参数。

### 2. 迁移 `pyproject.toml`

删除旧工具配置（若存在）：

- `[tool.black]`
- `[tool.isort]`
- `[tool.flake8]`
- `[tool.autoflake]`

新增或合并 ruff 配置：

```toml
[tool.ruff]
line-length = 100
exclude = ["venv", "build", ".venv"]

[tool.ruff.lint]
extend-select = ["RUF100", "RUF101", "RUF102", "PGH"]
preview = false
ignore = ["E203", "E226"]

[tool.ruff.format]
quote-style = "preserve"
```

迁移时要对齐原配置：

- 原 black 的 `line-length`、`exclude` 迁移到 `[tool.ruff]`。
- 原 isort 的导入排序诉求优先由 ruff 的 `I` 规则覆盖。
- 原 flake8 的 `ignore`、`per-file-ignores` 迁移到 `[tool.ruff.lint]` 或 `[tool.ruff.lint.per-file-ignores]`。
- 不再单独配置 `select` 时，ruff 默认已覆盖常见 `E`、`F` 规则；需要扩展时使用 `extend-select`。

### 3. 清理依赖

从项目依赖文件中移除已被 ruff 替代的工具（若存在）：

- `black`
- `isort`
- `flake8`
- `autoflake`

检查范围包括：

- `requirements.txt`
- `pip-req.txt`
- `pip-req.d/`
- `pyproject.toml` 的开发依赖分组
- CI 专用依赖文件

保留或新增：

- `ruff`
- `mypy`
- `pre-commit`

### 4. 更新 CI 配置

若项目有 CI 配置，例如 `app.yaml` 的 `test_handlers`、Jenkinsfile、GitHub Actions、GitLab CI 等，需要同步更新：

1. 删除 black、isort、flake8、autoflake 相关 lint/format 任务。
2. 新增或更新 ruff 任务：执行 `ruff check`，必要时追加 `ruff format --check`。
3. 保留或新增 mypy 任务，确保类型检查入口和本地文档一致。
4. 若 CI 需要产物归档，确保脚本输出文件与 CI 配置的 archive 字段一致。

`app.yaml` 的 `test_handlers` 示例：

```yaml
- name: ruff
  type: flake8
  test_script: tools/ci-scripts/ruff.sh
  pip_req_path: tools/ci-scripts/ruff-reqs.txt
  enable_pr: true
  archive: ruff.out
```

ruff 脚本示例：

```bash
set -e

rm -f ruff.out

ruff check --output-file=ruff.out .
ruff format --check .
```

## 验证方式

优先按变更文件验证：

```bash
pre-commit run --files <changed_file_1.py> <changed_file_2.py>
```

迁移配置时额外抽样验证：

```bash
pre-commit run ruff-check --files <sample_file_1.py> <sample_file_2.py>
pre-commit run ruff-format --files <sample_file_1.py> <sample_file_2.py>
```

如项目已有 CI 脚本，也要直接执行对应脚本：

```bash
ruff check .
ruff format --check .
mypy <package_or_module>
```

注意：

- 不默认对全量历史代码执行自动格式化，除非用户明确要求或项目已有全量迁移计划。
- 若 mypy 对第三方库报错较多，先用基础过渡配置保证 CI 可落地，再逐步收紧。
- 若 ruff 报错集中在历史目录，可优先使用 `exclude` 或 `per-file-ignores` 控制迁移范围，并在 README 或计划中记录后续收敛策略。

## 检查清单

- `pyproject.toml` 中没有重复或冲突的 black、isort、flake8、ruff 配置。
- `.pre-commit-config.yaml` 中 ruff 使用 `ruff-check` 与 `ruff-format` 双 hook。
- 依赖文件已移除被 ruff 替代的旧工具，并保留 CI 实际需要的工具。
- CI 配置和脚本调用的是迁移后的命令。
- README 说明了本地安装、lint、format、type-check 与 pre-commit 用法。
- 验证命令已针对变更文件或抽样文件执行，并记录遗留问题。

## 参考

- Ruff 配置与规则映射可参考 Ruff 官方文档。
- 若项目与团队既有仓库风格一致，优先复用已有仓库的 ruff、mypy、pre-commit 与 CI 脚本约定。
