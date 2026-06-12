---
name: python-basic-ci-config-guide
description: Guide Python projects to add or migrate basic CI code quality config including ruff mypy pre-commit pyproject.toml and legacy black isort flake8 replacement.
---

# Python 基础 CI 配置指南

约定 `<skill_dir>` 为本技能所在目录。

## 概述

本技能用于给 Python 项目新增或迁移基础代码质量检查配置，覆盖本地 `pre-commit` 与 CI 中常见的 lint、format、type-check 配置。

适用场景：

- **新增 Python 基础 CI 配置**：新项目初始化、旧项目补齐基础检查、跨仓统一代码检查基线。
- **迁移 legacy Python linters 到 ruff**：将已有 black、isort、flake8、autoflake 等工具迁移到 ruff，避免重复规则与格式化冲突。
- **CI 对齐**：同步更新 `pyproject.toml`、`.pre-commit-config.yaml`、依赖文件、CI 脚本和项目 README。

基础工具组合：

- `ruff`：lint、import 排序与 format。
- `mypy`：静态类型检查。
- `pre-commit`：本地提交前检查。

## 场景索引

根据目标项目现状选择对应参考文档，并完整读取后执行：

- **新增 Python 基础 CI 配置**：没有基础检查配置，或需要补齐 ruff、mypy、pre-commit 基线时，读取 `<skill_dir>/references/add-python-basic-ci-config.md`。
- **迁移 legacy Python linters 到 ruff**：已有 black、isort、flake8、autoflake 或旧 ruff 配置，需要统一迁移到 ruff 时，读取 `<skill_dir>/references/migrate-legacy-python-linters-to-ruff.md`。

通用模板位置：

- `.pre-commit-config.yaml` 模板：`<skill_dir>/references/pre-commit-config-template.yaml`
- `pyproject.toml` 模板：`<skill_dir>/references/pyproject-template.toml`

## 总体流程

1. 确认项目根目录和现有配置：`pyproject.toml`、`.pre-commit-config.yaml`、依赖文件、CI 配置、README。
2. 按「场景索引」读取对应参考文档。
3. 合并模板或迁移配置，避免重复 hook、重复 `[tool.*]` 配置与重复依赖。
4. 更新 CI 配置和项目 README，确保本地与 CI 使用同一套命令。
5. 用变更文件或少量抽样文件验证，不默认全量格式化历史代码。

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

## 场景与模板索引

- 新增 Python 基础 CI 配置：`<skill_dir>/references/add-python-basic-ci-config.md`
- 迁移 legacy Python linters 到 ruff：`<skill_dir>/references/migrate-legacy-python-linters-to-ruff.md`
- `.pre-commit-config.yaml` 模板：`<skill_dir>/references/pre-commit-config-template.yaml`
- `pyproject.toml` 模板：`<skill_dir>/references/pyproject-template.toml`
