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
| [skills/common/backend-skill-project-conventions/](skills/common/backend-skill-project-conventions/) | 维护并校验 backend-skills 的 frontmatter、路径、内部依赖和 README 技能列表约束 |

### 代码规范与工具

| 技能目录 | 说明 |
|----------|------|
| [skills/common/lit-code-style-guide/](skills/common/lit-code-style-guide/) | 设计、实现或审查随后端发布的无构建 Lit 页面，覆盖模板入口、import map、vendor 管理和浏览器验证 |
| [skills/python/python-basic-ci-config-guide/](skills/python/python-basic-ci-config-guide/) | 新增 Python 基础 CI，或将 Black、isort、Flake8、autoflake 等 legacy 工具迁移到 Ruff |
| [skills/common/fix-with-pre-commit/](skills/common/fix-with-pre-commit/) | 在最小文件范围内运行 pre-commit，修复真实问题并准确报告验证结果 |

### 流程与规划

| 技能目录 | 说明 |
|----------|------|
| [skills/common/write-project-plan/](skills/common/write-project-plan/) | 基于真实仓库证据编写零上下文可执行的实施计划，包含精确文件、完整代码、验证命令和完成条件 |
| [skills/common/execute-project-plan/](skills/common/execute-project-plan/) | 执行已写就的项目实施计划，按步骤推进并逐步验证，通过计划文件维护进度与状态 |
| [skills/common/git-commit-push/](skills/common/git-commit-push/) | 自动探测 Git 上下文，提交已跟踪改动、执行 squash-aware rebase 并推送当前分支 |
