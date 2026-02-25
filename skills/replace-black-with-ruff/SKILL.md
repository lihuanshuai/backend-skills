---
name: replace-black-with-ruff
description: Replaces black, isort, and flake8 (and optionally autoflake) with ruff in pre-commit and pyproject.toml. Use when the user asks to migrate to ruff, replace black/isort/flake8 with ruff, or unify lint and format with ruff.
---

# 用 Ruff 替换 Black / isort / flake8

将项目中的 black、isort、flake8（及可选的 autoflake）统一替换为 [ruff](https://docs.astral.sh/ruff/)，在 `.pre-commit-config.yaml` 和 `pyproject.toml` 中完成配置迁移。

## 执行步骤

### 1. 修改 `.pre-commit-config.yaml`

- **删除**以下 repo 及其 hooks（若存在）：
  - `PyCQA/isort`
  - `psf/black`
  - `PyCQA/flake8`（含 `additional_dependencies`）
  - 可选：`PyCQA/autoflake`（ruff 的 I/UP 规则可替代）
- **新增** ruff-pre-commit（若已有 ruff 则改为下述配置）：
  - `repo: https://github.com/astral-sh/ruff-pre-commit`
  - `rev: v0.15.2`（或与团队一致）
  - 使用**两个** hook：`ruff-check`、`ruff-format`（不要用单一的 `ruff`）
  - `ruff-check` 的 `args`: `[--fix, --extend-select, "I,UP", --unsafe-fixes]`
  - `ruff-format` 无需 args

示例（YAML 缩进 2 空格）：

```yaml
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.2
    hooks:
    - id: ruff-check
      args: [--fix, --extend-select, "I,UP", --unsafe-fixes]
    - id: ruff-format
```

### 2. 修改 `pyproject.toml`

- **删除**（若存在）：`[tool.black]`、`[tool.isort]`、`[tool.flake8]`、可选 `[tool.autoflake]`。
- **删除依赖**：从项目的依赖文件中移除上述工具对应的包（若存在）：
  - **requirements.txt** 或 **pip-req.txt**：删除包含 `black`、`isort`、`flake8`、`autoflake` 的行（含带版本约束的，如 `black==24.x`）。
  - **pip-req.d/**：若项目用该目录分散依赖，检查其中各文件并删除上述包对应的行。
- **新增或合并** `[tool.ruff]` 配置：

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

- **说明**：
  - `line-length`、`exclude` 按项目需要调整；`exclude` 可参考现有 black/flake8 的 exclude。
  - 若项目原先 flake8 有 `ignore`（如 E203、W503），在 ruff 中用 `ignore = ["E203", "E226"]` 对齐常见约定；不再单独配 `select` 时，ruff 默认已包含 E/F 等。
  - `quote-style = "preserve"` 与多数既有代码库一致；若项目统一双引号可改为 `"double"`。
  - 若有特殊目录需忽略某些规则，可加 `[tool.ruff.lint.per-file-ignores]`（参见 [ruff 文档](https://docs.astral.sh/ruff/configuration/)）。

### 3. 验证

- 在项目根目录执行：`pre-commit run --all-files`
- 若有失败：按 ruff 报错修代码或微调 `ignore` / `per-file-ignores`，再跑直到通过。

## 参考

- 若项目与豆瓣 group 等仓库风格一致，可直接参照其 `pyproject.toml` 中 `[tool.ruff]`、`[tool.ruff.lint]`、`[tool.ruff.format]` 及 `.pre-commit-config.yaml` 中的 ruff 部分。
- Ruff 规则与 black/isort/flake8 的对应关系见 [Ruff 规则映射](https://docs.astral.sh/ruff/rules/)。
