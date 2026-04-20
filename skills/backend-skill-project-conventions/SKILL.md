---
name: backend-skill-project-conventions
description: Define and check backend-skills project conventions when creating or updating skill docs and structure including frontmatter path references dependency declarations and README skill list sync.
---

# backend-skills 项目规范技能

约定 `<skill_dir>` 为本技能所在目录。

当需求涉及「新建技能」「重命名技能」「补充技能文档规范」「校验 SKILL frontmatter」「确认路径写法与依赖声明」时使用本技能。

## 项目背景

backend-skills 是面向后端开发的 Cursor Agent 技能集合。每个技能对应一个独立目录，内含 `SKILL.md` 及可选脚本，供 Agent 在相关任务中自动读取并遵循执行。当前技能覆盖 pre-commit 检查修复、CSV 提取导出、YAML/JSON 互转等通用后端场景。

## 编码与文档标准

- 每个技能必须有 **YAML frontmatter**，包含：
  - `name`：技能标识，与目录名一致，简短英文
  - `description`：一句话说明技能用途与触发场景，供 Agent 匹配
  - **避免在 description 等元数据值中使用冒号**：YAML 中冒号（`:`）为键值分隔符，在 description、metadata 等字段值中使用冒号可能导致解析歧义；可用「包括」「including」等词替代（如将 `Use when: get logs` 改为 `Use when including get logs`）
  - 可选：`metadata` 等
- **metadata.depends_on / used_by**：仅可引用本仓库 README「技能列表」中列出的技能，不得依赖未列出项目的 skill
- 使用中文编写技能正文，结构清晰（概述、使用方式、示例、注意事项等）
- 若技能依赖外部工具或库（如 PyYAML、pre-commit、com2ann），在技能内和 README 中明确说明

## 首选依赖与工具

- **Python**：带脚本的技能使用 Python 3.6+（个别技能如 com2ann 需更高版本，以该技能 SKILL 为准），仅用标准库或明确声明的依赖（如 PyYAML）
- **pre-commit**：fix-with-pre-commit 技能在项目根目录执行，依赖 `.pre-commit-config.yaml`

## 项目文件结构约定

```text
.gitignore
AGENTS.md          # 简短入口，详细约定见本技能
README.md          # 安装方式、技能列表、使用说明
skills/            # 技能目录，每个技能一个子目录
├── <skill-name>/  # 技能名即目录名，建议 kebab-case
│   ├── SKILL.md   # 必选，技能说明与流程
│   ├── scripts/   # 可选，该技能用到的可执行脚本与脚本依赖
│   │   ├── *.py
│   │   └── requirements.txt  # 可选，脚本依赖（统一放在 scripts/ 下）
└── ...
```

## 技能规范

- **SKILL.md**：必须包含 frontmatter（`name`、`description`），正文建议包含「概述、使用方式/流程、示例、注意事项」等区块
- **scripts/**：若技能需要执行脚本，放在该技能目录下的 `scripts/` 中，在 `SKILL.md` 中写明调用方式与参数
- **路径引用（强制约定）**：先在文档中声明约定 `<skill_dir>`（表示「当前 skill 目录」），后续所有路径说明都必须基于该约定展开；**禁止在没有此前提时直接使用相对路径**。推荐写法：`<skill_dir>/SKILL.md`、`<skill_dir>/scripts/xxx.py`、`<skill_dir>/scripts/requirements.txt`。同时避免写死绝对路径与环境变量（如 `/Users/...`、`~/.cursor/...`、`$HOME/...`），以免因安装路径不一致造成错误
- **安装路径不可写死**：不同 Agent 的 skill 安装路径各异；`SKILL.md` 中不得出现 `~/.cursor/skills/...`、`~/.claude/skills/...` 等某一款 Agent 特有的路径。应使用「从本 skill 目录推断」「本 skill 目录下的 scripts/」等通用表述，确保跨 Agent 可移植
- 新增技能后，须在 **README.md** 的「技能列表」表格中补充一行；修改技能名称或说明时同步更新表格

## 安装与发现（文档职责）

仓库级安装步骤与技能发现方式写在 **README.md**（安装、依赖、各技能脚本依赖安装示例）。本技能不重复展开具体 clone 路径，避免与「禁止写死安装路径」冲突；向用户说明安装时引用 README 即可。

## 技能规范检查清单

- `SKILL.md` 含有效 frontmatter，`name` 与父目录名一致
- `description` 明确「何时使用」，且值中避免冒号引发 YAML 歧义
- 若声明 `metadata.depends_on` / `used_by`，目标技能均在 README 技能列表中
- 路径先声明 `<skill_dir>`，正文中的文件路径均相对该约定
- 无写死的用户目录、Agent 专属 skills 路径或绝对路径示例
- 有脚本时存在 `<skill_dir>/scripts/`，且 SKILL 中说明调用方式与参数
- README 技能列表与仓库内 `skills/*/` 一致

## 注意事项

- 技能描述（description）应明确「何时使用」，便于 Agent 正确选用
- 修改现有技能时保持与既有技能风格一致，并同步更新 README 技能列表（若有名称或说明变更）
