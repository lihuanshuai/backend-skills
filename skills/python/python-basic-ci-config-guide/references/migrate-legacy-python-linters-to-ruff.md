# 场景：迁移 legacy Python linters 到 ruff

约定 `<skill_dir>` 为 `python-basic-ci-config-guide` 技能所在目录。

本参考用于将已有 black、isort、flake8、autoflake 或旧 ruff 配置迁移到统一的 ruff、mypy、pre-commit 基线。

## 1. 迁移 `.pre-commit-config.yaml`

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

## 2. 迁移 `pyproject.toml`

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

## 3. 清理依赖

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

## 4. 更新 CI 配置

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

## 5. 迁移 legacy Python linters 到 ruff 检查点

- 旧工具的 hook、配置段、依赖和 CI 任务已同步移除。
- ruff 配置继承了原有行宽、排除目录、忽略规则和 per-file ignores。
- `UP` 规则只在确认 Python 3-only 后启用。
- CI 脚本输出文件与归档配置一致。
