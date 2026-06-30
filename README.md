# backend-skills

后端开发相关 Cursor Agent 技能（pre-commit、Python CI、项目规划等）。

## 依赖

- **Python**：带脚本的技能按各自 `SKILL.md` 与 `scripts/requirements.txt` 声明安装依赖。
- **pre-commit / ruff / mypy**：`python-basic-ci-config-guide` 用于配置这些工具；`fix-with-pre-commit` 在项目根目录执行，需已安装 [pre-commit](https://pre-commit.com/) 且项目存在 `.pre-commit-config.yaml`。

## 安装

将本仓库 clone 到 Cursor 的 skills 目录下：

```bash
mkdir -p ~/.cursor/skills
cd ~/.cursor/skills
git clone https://github.com/lihuanshuai/backend-skills.git
# 若已有目录，可进入后 git pull 更新
```

完成后技能位于 `~/.cursor/skills/backend-skills/skills/`（含 `python/` 和 `common/` 两个子目录），Cursor Agent 会在「Agent Skills」中发现并读取各技能目录下的 `SKILL.md`。

## 技能列表

### 项目维护

| 技能目录 | 说明 |
|----------|------|
| [skills/common/backend-skill-project-conventions/](skills/common/backend-skill-project-conventions/) | 维护 backend-skills 的项目约束，统一 frontmatter、路径引用、依赖声明与 README 技能列表同步规则 |

### 代码规范与工具

| 技能目录 | 说明 |
|----------|------|
| [skills/common/lit-code-style-guide/](skills/common/lit-code-style-guide/) | Lit 前端代码风格与无构建发布规范，覆盖后端模板入口、本地 import map、页面级模块加载、vendor 管理与真实页面验证 |
| [skills/python/python-basic-ci-config-guide/](skills/python/python-basic-ci-config-guide/) | Python 基础 CI 配置指南，覆盖 ruff、mypy、pre-commit 的新增配置，以及 black、isort、flake8 到 ruff 的迁移配置 |
| [skills/common/fix-with-pre-commit/](skills/common/fix-with-pre-commit/) | 检查并自动修复 pre-commit 报错，支持按文件列表或 linter 输出跑 hook |

### 版本与依赖

| 技能目录 | 说明 |
|----------|------|
| [skills/python/python-bump-version/](skills/python/python-bump-version/) | 提升 Python 包版本，支持 setup.py、setup.cfg、pyproject.toml，可选 patch/minor/major |

### 流程与规划

| 技能目录 | 说明 |
|----------|------|
| [skills/common/write-project-plan/](skills/common/write-project-plan/) | 编写详尽的实施计划，面向零项目上下文的工程师，包含完整代码、命令与验证方式，遵循 TDD 和零占位符原则 |
| [skills/common/execute-project-plan/](skills/common/execute-project-plan/) | 执行已写就的项目实施计划，按步骤推进并逐步验证，通过计划文件维护进度与状态 |
| [skills/common/git-commit-push/](skills/common/git-commit-push/) | 执行 Git 提交、rebase --onto 与推送的标准流程，包含 staged 限制、pre-commit 约束与冲突处理 |
