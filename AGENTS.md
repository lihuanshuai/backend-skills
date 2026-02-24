# 项目背景

backend-skills 是面向后端开发的 Cursor Agent 技能集合。每个技能对应一个独立目录，内含 `SKILL.md` 及可选脚本，供 Agent 在相关任务中自动读取并遵循执行。当前技能覆盖 pre-commit 检查修复、CSV 提取导出、YAML/JSON 互转等通用后端场景。

# 编码与文档标准

- 每个技能必须有 **YAML frontmatter**，包含：
  - `name`: 技能标识，与目录名一致，简短英文
  - `description`: 一句话说明技能用途与触发场景，供 Agent 匹配
  - 可选：`commandPalette`、`metadata` 等
- 使用中文编写技能正文，结构清晰（概述、使用方式、示例、注意事项等）
- 若技能依赖外部工具或库（如 PyYAML、pre-commit），在技能内和 README 中明确说明

# 首选依赖与工具

- **Python**：带脚本的技能使用 Python 3.6+，仅用标准库或明确声明的依赖（如 PyYAML）
- **pre-commit**：fix-with-pre-commit 技能在项目根目录执行，依赖 `.pre-commit-config.yaml`

# 文件结构

```
.gitignore
AGENTS.md          # 本文件，项目 Agents 说明
README.md          # 安装方式、技能列表、使用说明
skills/            # 技能目录，每个技能一个子目录
├── <skill-name>/  # 技能名即目录名，建议 kebab-case
│   ├── SKILL.md   # 必选，技能说明与流程
│   ├── scripts/   # 可选，该技能用到的可执行脚本
│   │   └── *.py
│   └── requirements.txt  # 可选，脚本依赖
└── ...
```

# 技能规范

- **SKILL.md**：必须包含 frontmatter（name、description），正文建议包含「概述、使用方式/流程、示例、注意事项」等区块
- **scripts/**：若技能需要执行脚本，放在该技能目录下的 `scripts/` 中，在 SKILL.md 中写明调用方式与参数
- 新增技能后，需在 **README.md** 的「技能列表」表格中补充一行

# 安装与发现

将本仓库 clone 到 `~/.cursor/skills` 下（如 `~/.cursor/skills/backend-skills`），Cursor 会在该目录下发现并读取各技能子目录中的 `SKILL.md`，详见 README.md。

# 注意事项

- 技能描述（description）应明确「何时使用」，便于 Agent 正确选用
- 修改现有技能时保持与既有技能风格一致，并同步更新 README 技能列表（若有名称或说明变更）
