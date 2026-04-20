# backend-skills — AGENTS

## 项目背景

backend-skills 是面向后端开发的 AI Agent 技能文档集合，供 Cursor、内部 AI 助手等复用。每个技能对应一个独立目录，内含 `SKILL.md` 及可选脚本，供 Agent 在相关任务中自动读取并遵循执行。

## 编码与文档标准

项目规范统一以 `backend-skill-project-conventions` 技能约定为准。

当需求涉及「新建技能」「重命名技能」「补充技能文档规范」「校验 SKILL frontmatter」时，应优先使用该技能并按其步骤执行。

## 安装与发现

不同 Agent 的 skill 安装路径不同，常见示例：

| Agent | 安装路径示例 |
|-------|--------------|
| Cursor | `~/.cursor/skills/backend-skills` |
| Claude（迁移兼容） | `~/.claude/skills/backend-skills` |
| Codex（迁移兼容） | `~/.codex/skills/backend-skills` |
| 项目级（通用约定） | `<项目根>/.agents/skills/backend-skills` |
| 其他 Agent | 请参考其文档 |

各 Agent 会在各自约定的目录下发现并读取各技能子目录中的 `SKILL.md`，依赖与使用说明详见 [README.md](README.md)。

## 注意事项

- 技能编写与维护规范（包括 description 写法、依赖声明、README 技能列表同步、路径可移植性等）统一以 `backend-skill-project-conventions` 技能约定为准。
