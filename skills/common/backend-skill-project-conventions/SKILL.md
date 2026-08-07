---
name: backend-skill-project-conventions
description: 创建、更新、重命名或校验 backend-skills 技能时，统一检查 frontmatter、目录结构、路径可移植性、内部依赖和 README 技能列表。
---

# backend-skills 项目规范

约定 `<skill_dir>` 为目标技能目录，`<repo_dir>` 为本仓库根目录。把本文件当作路由：先识别变更类型，只读取和修改相关文件；不要重复解释通用模型知识。

## 执行

1. 读取 `<repo_dir>/AGENTS.md` 和目标 `SKILL.md`。仅在目标技能引用了资源、或本次涉及脚本/依赖/配置时，再读取对应资源；先用搜索确认引用和影响范围。
2. 按变更类型执行：
   - **新增、删除或重命名技能**：检查目录、所有仓内引用和 README；同步技能列表及依赖说明。
   - **修改 `name`、`description` 或 frontmatter 依赖**：同步 README；核对 `agents/openai.yaml`（若存在）。
   - **只改正文或脚本**：不改 README，除非技能目录、依赖、触发语义或公开接口发生变化。
   - **只做校验**：直接运行校验脚本并报告错误；不为修复未发现的问题扩大改动范围。
3. 创建或维护技能时遵守：
   - 技能位于 `<repo_dir>/skills/common/<name>/` 或 `<repo_dir>/skills/python/<name>/`，目录名使用 kebab-case。
   - `SKILL.md` frontmatter 的 `name` 必须与目录一致；`description` 必须是一行、无冒号，并同时说明能力和触发场景。
   - 正文使用中文和命令式表达，只保留非显然决策、硬约束、执行入口和输出契约。重复且确定的操作收口到 `scripts/`；只在条件分支复杂时使用 `references/`。
   - 路径先声明 `<skill_dir>` 或 `<repo_dir>`，不写死用户目录、Agent 安装目录、`$HOME` 或 provider 的 skills 路径。
   - `metadata.depends_on` / `used_by` 只引用 README 已列出的技能。脚本默认兼容 Python 3.6+ 和标准库；更高版本或外部依赖必须在技能和 README 中声明。
4. 执行仓库级校验：

   ```bash
   python3 <skill_dir>/scripts/validate_project.py <repo_dir>
   ```

5. 修复 JSON `errors` 后重跑至 `status=ok`。最后只做一次人工审查：触发描述是否准确、正文是否仍是最短可执行路径、引用是否与实现一致。机械校验通过不代表语义审查或运行时验证通过。

## 硬约束

- 不创建技能运行不需要的 README、安装指南、changelog 或重复 quick reference。
- 不把 provider-specific 配置塞进通用 `SKILL.md`；已有 `agents/openai.yaml` 时同步核对其展示名称、简述和默认提示。
- 不覆盖或顺手整理无关技能；删除或重命名前先搜索所有引用并同步调用方。
