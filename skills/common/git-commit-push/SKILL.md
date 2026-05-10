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
  - `<skill_dir>/scripts/select_rebase_base.py`

## 输入约定

- 执行前应已确定以下变量：
  - `<upstream_remote>`
  - `<origin_remote>`
  - `<default_branch>`
  - `<current_branch>`

## 执行步骤

### 1. 暂存与 pre-commit

- 仅允许 `git add --update`，禁止 `git add .`。
- 严禁将未跟踪文件加入暂存区（stage）；不得使用任何会纳入 untracked 文件的 add 方式。
- 若存在 `.pre-commit-config.yaml`：
  - 禁止 `--no-verify`
  - 禁止 `pre-commit run --all-files`
  - 仅对 staged 文件执行 pre-commit（或依赖 commit hook）
  - 失败时优先尝试修复（可用 `fix-with-pre-commit`）

### 2. 提交

- 无 staged 改动时：
  - 必须跳过 commit/push
  - 明确反馈“无可提交改动，已跳过 commit/push”
- 有 staged 改动时：
  - 生成中文提交说明并 `git commit`

### 3. Rebase 与推送

- 同步上游：
  - 执行脚本选择 rebase base（会自动 `fetch` 并输出 JSON）：
    - `python3 <skill_dir>/scripts/select_rebase_base.py <upstream_remote> <default_branch>`
  - 读取返回中的：
    - `remote_ref`（记为 `R`）
    - `base_commit`（记为 `BASE`）
    - `strategy`（`tree_match` 或 `merge_base_fallback`）
  - 执行：`git rebase --autostash --onto "$R" "$BASE"`
  - 语义说明：
    - `tree_match`：当前分支存在某个祖先提交的文件树已被目标分支吸收（常见于 squash merge），优先以该点为 base，避免重复重放已吸收改动
    - `merge_base_fallback`：未找到树匹配时，回退标准 `merge-base` 行为
  - 若冲突：仅允许 `git add --update` 或显式冲突文件路径，之后必须 `git rebase --continue`
  - 冲突处理中禁止额外新建 commit
- 推送：
  - 默认 `git push <origin_remote> <current_branch>`
  - rebase 后需覆盖远程时，使用 `--force-with-lease`
  - 未设置上游时可先 `--set-upstream`

## 约束总结

- 提交说明必须使用中文。
- 禁止 `git add .`、`--no-verify`、`pre-commit run --all-files`。
- 允许提交用户已暂存的改动；但 Agent 不得主动将未跟踪文件加入 stage。
