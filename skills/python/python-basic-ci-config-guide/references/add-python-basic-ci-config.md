# 场景：新增 Python 基础 CI 配置

约定 `<skill_dir>` 为 `python-basic-ci-config-guide` 技能所在目录。

本参考用于新项目初始化、旧项目补齐基础检查、或多仓库统一 Python 代码检查基线。

## 1. 更新 `.pre-commit-config.yaml`

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

## 2. 更新 `pyproject.toml`

若项目没有 `pyproject.toml`，先创建基础文件；若已存在，合并模板中的配置段。

模板位置：

- `<skill_dir>/references/pyproject-template.toml`

默认包含：

- `[tool.ruff]`
- `[tool.ruff.lint]`
- `[tool.ruff.format]`
- `[tool.mypy]`

建议：

- `line-length`、`exclude`、`ignore` 按项目现有风格微调。
- mypy 初始落地可保留 `ignore_missing_imports = true` 作为过渡，再按项目逐步收紧。
- 如需统一双引号，可将 `[tool.ruff.format]` 的 `quote-style` 从 `"preserve"` 调整为 `"double"`。

## 3. 补充依赖与 README

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

## 4. 新增 Python 基础 CI 配置检查点

- 不重复添加已有 repo、hook 或 `[tool.*]` 配置段。
- `ruff-check` 与 `ruff-format` 分成两个 hook。
- `UP` 规则只在确认 Python 3-only 后启用。
- README 与 CI 文档里的命令和实际配置一致。
