---
name: git-commit-push
description: 提交已跟踪改动、以 squash-aware 策略 rebase 并推送当前 Git 分支。适用于用户明确要求完成 commit 和 push，且不需要创建或更新 PR 的场景。
metadata:
  depends_on:
    - fix-with-pre-commit
---

# Git Commit Push

约定 `<skill_dir>` 为当前技能目录。使用 `<skill_dir>/scripts/commit_rebase_push.py` 完成提交、squash-aware rebase 与推送，不手工重建等价流程。

## 执行

1. 一次性检查 `git status --short --branch` 与相关 diff，确认所有 tracked modifications 都属于本次提交；untracked 文件默认留在工作区。范围不明确时先请用户确认。
2. 根据整体 diff 生成简洁的中文提交说明，直接执行：

   ```bash
   python3 <skill_dir>/scripts/commit_rebase_push.py --message "<中文提交说明>"
   ```

3. 直接消费脚本输出的 JSON 事件：`skip` 表示无需继续；成功时汇报 `commit.head`、`rebase.changed`、`push.remote/branch` 与忽略的 untracked 文件。无需重复执行已成功的 Git 步骤。

脚本自动探测 upstream、`origin`、远端默认分支和当前分支。仅在自动探测失败或用户明确指定非标准拓扑时，按 `--help` 使用 `--upstream-remote`、`--origin-remote`、`--default-branch` 或 `--current-branch` 显式指定；只提交和 rebase 时使用 `--no-push`。

## 硬约束

- 只处理已跟踪改动；禁止 `git add .` 或主动暂存 untracked 文件，不得新建或切换分支。
- 默认只推送 `origin`；只有用户明确指定时才覆盖 push remote。
- 有 `.pre-commit-config.yaml` 时只检查 staged 文件；禁止 `--no-verify` 和 `pre-commit run --all-files`。仅确认 commit hook 已覆盖相同检查时才使用 `--skip-pre-commit`。
- 出现 `rebase_conflict` 时立即停止并报告冲突文件；不得编辑冲突、`git add` 或 `git rebase --continue`，等待用户处理。
