---
name: python-basic-ci-config-guide
description: 为 Python 项目新增 Ruff、Mypy、pre-commit 基础 CI，或将 Black、isort、Flake8、autoflake 等 legacy 工具迁移到 Ruff。适用于配置本地与 CI 代码质量基线的场景。
---

# Python 基础 CI 配置

约定 `<skill_dir>` 为当前技能目录，`<repo_dir>` 为目标项目根目录。

## 场景路由

- 项目缺少 Ruff、Mypy 或 pre-commit 基线时，只读取 `<skill_dir>/references/add-python-basic-ci-config.md`。
- 已有 Black、isort、Flake8、autoflake 或旧 Ruff 配置需要迁移时，只读取 `<skill_dir>/references/migrate-legacy-python-linters-to-ruff.md`。
- 仅在目标同时包含两个场景时读取两份 reference；模板位于 `<skill_dir>/references/pre-commit-config-template.yaml` 和 `<skill_dir>/references/pyproject-template.toml`，只能作为合并起点。

## 通用流程

1. 读取 `<repo_dir>` 的 runtime、依赖、`pyproject.toml`、`.pre-commit-config.yaml`、CI 入口和项目说明，先确认 Python 版本与真实执行命令。
2. 按场景 reference 合并配置，不覆盖无关段落；同步 hook、工具配置、依赖、CI 脚本/任务和 README，避免本地与 CI 漂移。
3. 先对变更文件或少量代表文件运行 hook，再执行目标项目真实 CI 入口。自动改写后审查 diff 并重跑同一范围。
4. 汇报修改的配置面、实际验证范围与遗留项；局部抽样通过不得表述为全仓库或 CI 通过。

## 决策门禁

- 只有确认 Python 3-only 才启用 Ruff `UP`；Python 2 或混合运行时只启用 `I`。不得从仓库名称或单个本地解释器推断 runtime。
- 模板版本是快照，不是升级目标；优先对齐目标仓库或团队已验证版本，未经要求不执行 `pre-commit autoupdate`。
- `--unsafe-fixes` 必须由项目明确接受语义风险后才启用。不得用新增 ignore/exclude、规则收窄或版本 pin 掩盖本次引入的真实失败；保留历史 baseline 时记录理由与收敛范围。
- Mypy 严格度必须匹配现有注解覆盖率和 CI 迁移策略，不得机械套用模板后用大范围 `type: ignore` 收尾。
- 默认禁止全量自动格式化历史代码；只有用户明确要求或已有独立迁移计划时才扩大范围。
