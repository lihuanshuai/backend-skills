---
name: backend-skill-project-conventions
description: 创建、更新、重命名或校验 backend-skills 技能时，统一检查 frontmatter、目录结构、路径可移植性、内部依赖和 README 技能列表。
---

# backend-skills 项目规范

约定 `<repo_dir>` 为本仓库根目录，`<conventions_dir>` 为本技能目录，`<target_dir>` 为目标技能目录。

## 流程

1. 读取 `<repo_dir>/AGENTS.md` 和 `<target_dir>/SKILL.md`。先搜索影响范围；只在资源、脚本、依赖或配置受影响时读取对应文件。
2. 仅修改任务所需内容，并遵守：
   - 技能位于 `<repo_dir>/skills/common/<name>/` 或 `<repo_dir>/skills/python/<name>/`，目录名使用 kebab-case。
   - `SKILL.md` frontmatter 的 `name` 必须与目录一致；`description` 必须是一行、无冒号，并同时说明能力和触发场景。
   - 正文使用中文和命令式表达，只保留非显然决策、硬约束、执行入口和输出契约。重复且确定的操作收口到 `scripts/`；只在条件分支复杂时使用 `references/`。
   - 路径先声明 `<skill_dir>` 或 `<repo_dir>`，不写死用户目录、Agent 安装目录、`$HOME` 或 provider 的 skills 路径。
   - `metadata.depends_on` / `used_by` 只引用 README 已列出的技能。脚本默认兼容 Python 3.6+ 和标准库；更高版本或外部依赖必须在技能和 README 中声明。
3. 仅在影响成立时同步关联文件：新增、删除、重命名，或修改 `name`、`description`、依赖时更新 README；存在 `agents/openai.yaml` 且展示信息受影响时同步更新；公开入口变化时同步调用方。
4. 从任意目录执行仓库级机械校验：

   ```bash
   python3 <conventions_dir>/scripts/validate_project.py <repo_dir>
   ```

5. 修改任务只修复本次引入或范围内的 JSON `errors`，重跑至 `status=ok`；校验任务只报告结果。最后复核触发语义、最短执行路径和引用一致性，并把机械校验与运行时验证分开报告。

## 硬约束

- 不创建技能运行不需要的 README、安装指南、changelog 或重复 quick reference。
- 不把 provider-specific 配置塞进通用 `SKILL.md`；已有 `agents/openai.yaml` 时同步核对其展示名称、简述和默认提示。
- 不覆盖或顺手整理无关改动；删除或重命名前必须搜索并同步所有仓内引用。
