# backend-skills

后端开发技能。本仓库目前维护技能仓项目规范和无构建 Lit 页面指南；Git、计划与 Python CI 技能已迁往下列独立仓库。

## 相关仓库

- [git-skills](https://github.com/lihuanshuai/git-skills)：`git-commit-push`、`fix-with-pre-commit`。
- [plan-skills](https://github.com/lihuanshuai/plan-skills)：`write-project-plan`、`execute-project-plan`。
- [python-skills](https://github.com/lihuanshuai/python-skills)：`python-basic-ci-config-guide`。

## 安装

不同 Agent 的安装路径示例见下表；具体发现机制以对应 Agent 文档为准。

| Agent | 安装路径示例 |
|-------|--------------|
| Cursor | `~/.cursor/skills/backend-skills` |
| Claude（迁移兼容） | `~/.claude/skills/backend-skills` |
| Codex（迁移兼容） | `~/.codex/skills/backend-skills` |
| 项目级（通用约定） | `<项目根>/.agents/skills/backend-skills` |

将本仓库 clone 到 Cursor 的 skills 目录下：

```bash
mkdir -p ~/.cursor/skills
cd ~/.cursor/skills
git clone https://github.com/lihuanshuai/backend-skills.git
# 若已有目录，可进入后 git pull 更新
```

完成后技能位于 `~/.cursor/skills/backend-skills/skills/common/`，Cursor Agent 会在「Agent Skills」中发现并读取各技能目录下的 `SKILL.md`。

## 技能列表

### 项目维护

| 技能目录 | 说明 |
|----------|------|
| [skills/common/backend-skill-project-conventions/](skills/common/backend-skill-project-conventions/) | 维护并校验 backend-skills 的 frontmatter、路径、内部依赖和 README 技能列表约束 |

### 代码规范与工具

| 技能目录 | 说明 |
|----------|------|
| [skills/common/lit-code-style-guide/](skills/common/lit-code-style-guide/) | 设计、实现或审查随后端发布的无构建 Lit 页面，覆盖模板入口、import map、vendor 管理和浏览器验证 |
