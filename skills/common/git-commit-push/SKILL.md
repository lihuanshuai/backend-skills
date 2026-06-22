---
name: git-commit-push
description: 执行 Git 提交、rebase 与推送的标准流程，包含 staged 限制、pre-commit 约束与冲突处理。适用于仅需完成 commit 和 push 的场景。
metadata:
  depends_on:
    - fix-with-pre-commit
---

# Git Commit Push

围绕 `commit`、`rebase` 与 `push` 提供标准流程。为降低已被 squash merge 的历史再次重放导致的冲突，默认使用 `rebase --onto`。

## 路径约定

- 约定 `<skill_dir>` 表示当前 skill 目录（本 `SKILL.md` 所在目录）。
- 本技能脚本路径：
  - `<skill_dir>/scripts/commit_rebase_push.py`
  - `<skill_dir>/scripts/select_rebase_base.py`

## 输入约定

- 执行前应已确定以下变量：
  - `<upstream_remote>`
  - `<origin_remote>`
  - `<default_branch>`
  - `<current_branch>`
- 执行前应先确认 `git status --short`，明确本次只提交已跟踪的预期改动；untracked 文件默认忽略，不交给脚本暂存。

## subagent 执行策略

优先将本技能交给 subagent 执行，主 Agent 负责确认边界、回收结果和最终汇报。

- **适合交给 subagent**：用户已明确要求 commit/push，当前改动范围清晰，且只需要完成标准 `commit -> rebase -> push` 流程。
- **主 Agent 自行执行**：当前仓库存在 rebase/merge 冲突、需要用户选择提交范围、要处理敏感线上配置，或当前环境没有可用 subagent 能力。
- **主 Agent 委派前检查**：确认当前分支、remote、默认分支、`git status --short`、是否存在 `.pre-commit-config.yaml`，并给出提交说明。
- **subagent 回传要求**：必须回传脚本完整输出中的 commit hash、rebase 结果、push 结果、是否忽略 untracked 文件，以及最终 `git status --short`。
- **主 Agent 回收复核**：收到回传后必须复核工作区状态；若已成功暂存、提交或推送，应在最终回复中发出对应 Git 指令事件。

### subagent 委派模板

```text
请在仓库 <repo_path> 执行 git-commit-push。
变量：
- upstream_remote: <upstream_remote>
- origin_remote: <origin_remote>
- default_branch: <default_branch>
- current_branch: <current_branch>
- commit_message: <中文提交说明>

边界：
- 只允许使用 <skill_dir>/scripts/commit_rebase_push.py 聚合脚本。
- 不要新建分支，不要执行 git add .，不要暂存 untracked 文件。
- 如遇 rebase_conflict，立即停止并回传冲突文件；不要自动解冲突，不要执行 git rebase --continue。

回传：
- git status --short 的执行前后结果
- commit hash
- rebase 结果
- push 结果
- untracked_ignored 提醒（如有）
```

## 执行方式

优先使用聚合脚本一次性串联暂存、提交、选择 rebase base、rebase 与 push，减少 Agent 多次手动执行命令带来的往返与状态遗漏。

```bash
python3 <skill_dir>/scripts/commit_rebase_push.py \
  <upstream_remote> \
  <origin_remote> \
  <default_branch> \
  <current_branch> \
  --message "<中文提交说明>"
```

- 脚本只执行 `git add --update`，不会暂存 untracked 文件；若发现 untracked 文件，仅输出 `untracked_ignored` 提醒。
- 无 staged 改动时，脚本输出 `skip` 并跳过 commit/push。
- 若存在 `.pre-commit-config.yaml`，脚本默认在 commit 前执行 `pre-commit run --files <staged files>`，不会执行 `--all-files`；确认项目 commit hook 已覆盖检查时，可追加 `--skip-pre-commit` 避免重复执行。
- 脚本会复用 squash-aware base 选择逻辑，内部完成 `fetch`、`rebase --autostash --onto` 与 push。
- rebase 后 HEAD 发生变化时，脚本使用 `--force-with-lease` 推送；未设置上游且无需 force 时，脚本使用 `--set-upstream`。
- 如 rebase 冲突，脚本只输出 `rebase_conflict` 与冲突文件列表后退出；Agent 必须暂停，交由用户手动解决并执行 `git rebase --continue`。
- 若只需要提交和 rebase、不推送，可追加 `--no-push`。

## 约束总结

### 🚫 禁止项（红线）

| 禁止行为 | 说明 |
|---------|------|
| **新建分支** | 严禁 `git switch -c` / `git checkout -b` |
| **`git add .`** | 仅允许 `--update`，避免纳入未跟踪文件 |
| **`--no-verify`** | 必须执行 pre-commit 检查 |
| **`pre-commit run --all-files`** | 仅对 staged 文件执行 |
| **主动暂存 untracked 文件** | Agent 不得主动执行 |
| **自动处理 rebase 冲突** | **必须交由用户手动处理**，Agent 严禁自动编辑冲突文件或执行 `git add` / `git rebase --continue` |
