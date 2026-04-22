---
name: python-basic-code-check-template
description: 添加 Python 基础代码检查配置模板 including ruff mypy pre-commit 与 pyproject.toml 和 .pre-commit-config.yaml 示例。Use when 需要快速初始化或统一 Python 项目的基础代码质量检查。
---

# Python 基础代码检查模板

约定 `<skill_dir>` 为本技能所在目录。

## 概述

本技能用于给 Python 项目快速添加一套基础代码质量检查配置，核心包括：

- `ruff`（lint + format）
- `mypy`（静态类型检查）
- `pre-commit`（提交前自动执行检查）

适用于新项目初始化、旧项目补齐检查、或多仓库统一代码检查基线。

## 使用方式

1. 确认项目根目录存在 `pyproject.toml`。
2. 新增或更新项目根目录 `.pre-commit-config.yaml`。
3. 在 `pyproject.toml` 中补齐 `[tool.ruff]` 与 `[tool.mypy]`。
4. 安装并执行 `pre-commit` 验证配置。
5. 模板落地后同步更新项目 `README.md`，补充代码检查工具、执行命令与本地使用说明。

## 配置模板

模板已拆分到 `<skill_dir>/references/` 目录：

- `.pre-commit-config.yaml` 模板：`<skill_dir>/references/pre-commit-config-template.yaml`
- `pyproject.toml` 模板：`<skill_dir>/references/pyproject-template.toml`

使用时将模板内容合并到目标项目对应文件，注意不要重复添加已存在配置项。

## 执行与验证

在目标项目根目录执行：

```bash
pre-commit install
pre-commit run --files <changed_file_1.py> <changed_file_2.py>
```

说明：

- 不建议默认执行 `--all-files`，优先按变更文件验证。
- 如果 `mypy` 对第三方库报错较多，先使用 `ignore_missing_imports = true` 作为基础过渡，再按项目逐步收紧。

## 调整建议

- 若项目已有 black/isort/flake8，使用 `/replace-black-with-ruff` 进行迁移，并移除重复检查配置，避免规则冲突。
- 若项目对类型严格度要求较高，可逐步开启更严格的 mypy 配置（例如限制 Any、收紧未注解函数）。
- 若目录结构复杂，可在 `ruff` 或 `mypy` 中增加项目级 `exclude`。

## 注意事项

- 本技能只提供基础模板，落地时应结合项目现有规范调整行宽、忽略规则与排除目录。
- 更新 hook 版本时，请保持 `.pre-commit-config.yaml` 与团队其他仓库尽量一致，降低协作成本。
- 模板合并完成后，必须同步维护项目 `README.md`，确保新成员能直接看到 lint、format、type-check 的使用方式。
