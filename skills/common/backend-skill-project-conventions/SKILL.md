---
name: backend-skill-project-conventions
description: 创建、更新、重命名或校验 backend-skills 技能时，统一检查 frontmatter、目录结构、路径可移植性、内部依赖和 README 技能列表。
---

# backend-skills 项目规范

约定 `<skill_dir>` 为当前技能目录，`<repo_dir>` 为 backend-skills 仓库根目录。使用 `<skill_dir>/scripts/validate_project.py` 校验可机械判断的约束。

## 执行

1. 先读取 `<repo_dir>/AGENTS.md`、目标技能及其直接引用资源；只按任务需要修改，不复制仓库背景或通用模型知识。
2. 创建或维护技能时遵守：
   - 技能位于 `<repo_dir>/skills/common/<name>/` 或 `<repo_dir>/skills/python/<name>/`，目录名使用 kebab-case。
   - `<skill_dir>/SKILL.md` frontmatter 至少包含与目录一致的 `name`，以及同时说明能力和触发场景的单行 `description`；元数据值避免冒号。
   - 正文使用中文和命令式表达，只保留非显然决策、硬约束、执行入口与输出契约。重复且确定的操作优先收口到 `scripts/`，大段条件细节才放入 `references/`。
   - 文档路径先声明 `<skill_dir>` 或 `<repo_dir>` 再引用，不写死用户目录、Agent 安装目录、`$HOME` 或某个 provider 的 skills 路径。
   - `metadata.depends_on` / `used_by` 只引用本仓 README 已列出的技能。脚本默认兼容 Python 3.6+ 和标准库；更高版本或外部依赖必须在技能与 README 中明确声明。
3. 新增、删除、重命名技能，或修改技能名称、description、依赖时，同步 README 技能列表及依赖说明。安装和发现说明只维护在 README，不复制到各技能。
4. 执行仓库级校验：

   ```bash
   python3 <skill_dir>/scripts/validate_project.py <repo_dir>
   ```

5. 修复 JSON `errors` 后重跑至 `status=ok`；再人工审查 description 是否易触发、正文是否精简、引用内容是否仍与实现一致。不得把 helper 通过表述为内容语义已审查。

## 硬约束

- 不创建技能运行不需要的 README、安装指南、changelog 或重复 quick reference。
- 不把 provider-specific 配置塞进通用 `SKILL.md`；已有 `agents/openai.yaml` 时同步核对其展示名称、简述和默认提示。
- 不覆盖或顺手整理无关技能；删除或重命名前先搜索所有引用并同步调用方。
