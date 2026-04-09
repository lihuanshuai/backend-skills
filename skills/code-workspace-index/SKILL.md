---
name: code-workspace-index
description: Build vs query of a VS Code multi-root workspace index. Query uses workspace-index.local.yaml/json. Build/sync commands, script behavior, and post-sync summary validation live in build-workspace-index.md—read that file when generating, refreshing the index, or polishing summaries after sync. Use when syncing code-workspace metadata, refreshing the index, or finding related projects in a multi-root workspace.
---

# Code Workspace 索引

本技能对应 **两类需求**，先区分再执行：

| 需求 | 目标 | Agent 动作 |
|------|------|------------|
| **建立索引** | 从 `.code-workspace` **生成或刷新** 本地索引，并在需要时 **补全/校验简介** | 见下文 **需求一** |
| **查询索引** | 基于已有索引 **筛选、列举、比对** 相关项目 | 见下文 **需求二**；索引缺失或过期时先 **需求一** |

## 路径约定

`<skill_dir>` 为 `skills/code-workspace-index/`（本 `SKILL.md` 所在目录）。

- 同步脚本：`<skill_dir>/scripts/sync_workspace_index.py`
- 默认索引输出：`<skill_dir>/workspace-index.local.yaml` 或 `.json`（详见 [build-workspace-index.md](build-workspace-index.md)）
- 若建立时用过 `-o`，查询与补全以用户说明或对话约定路径为准

## 需求一：建立索引（同步 / 生成 / 刷新）

**典型说法**：同步 workspace、生成/刷新索引、更新了 `.code-workspace`、新增或删除多根目录、索引缺失或过期、同步后需规范 **简介补全/校验**。

**流程概要**：

1. **按需**打开 [build-workspace-index.md](build-workspace-index.md)（不要默认加载；仅在本需求触发时阅读）。
2. 按该文档执行：**依赖安装** → **同步命令**（`python ... sync_workspace_index.py <.code-workspace>`）→ 可选 **简介补全与校验** → 查阅该文档 **注意事项**（JSONC、README 规则、勿提交等）。

脚本会写入 `meta`、`projects`（含路径、git、语言框架启发式）并 **启发式填充 `project.summary`**。仅重算摘要且多根未变时，用同一 workspace 与 `-o` 再执行同步命令即可。

## 需求二：查询索引（检索 / 选项目 / 相关仓）

**典型说法**：哪个项目负责某功能、相关仓库、多根里改哪里、前后端路径、PR 推到哪个 remote。

1. **读取** 默认或用户指定的索引文件；不存在时再要 `.code-workspace` 并按 [build-workspace-index.md](build-workspace-index.md) 建立索引。
2. 对照 `meta.workspace_base` / `workspace_file` 是否同一 workspace；多根列表刚变更时先建立索引再查。
3. 用 **关键词** 匹配 `name`、`path_relative`、`languages`、`frameworks`、`summary`；`summary` 异常时按 [build-workspace-index.md](build-workspace-index.md)「简介补全与校验」处理。
4. 多仓联调：优先语言或路径相近项，必要时请用户确认。
5. PR / 推送：参考 `git.remotes` 与 `remote_notes`。

**纯查询不要默认跑同步**；仅在索引缺失、过期或用户要求刷新时执行 **需求一**。

## 索引内容说明

| 字段 | 含义 |
|------|------|
| `meta.workspace_base` | `.code-workspace` 所在目录 |
| `meta.workspace_file` | workspace 文件绝对路径 |
| `projects[].path_relative` | 相对 `workspace_base` 的路径（异常时为绝对路径字符串） |
| `projects[].path_resolved` | 根目录绝对路径 |
| `projects[].git.remotes` | `git remote -v` fetch URL |
| `projects[].git.remote_notes` | upstream / origin 常见分工说明 |
| `projects[].project.languages` / `frameworks` / `package_name` | 启发式检测结果 |
| `projects[].project.summary` | 脚本启发式 + 可经 Agent 润色（规则见 `build-workspace-index.md`） |
| `agent_hints` | 匹配与 git、summary 质量提示 |

## 依赖（查询侧）

阅读或解析 YAML 索引需 PyYAML（与建立索引相同，见 `build-workspace-index.md`）。

## 注意事项

- 同步脚本行为、JSONC/README 摘要规则、简介补全与校验、勿提交索引文件等，均见 [build-workspace-index.md](build-workspace-index.md)。
