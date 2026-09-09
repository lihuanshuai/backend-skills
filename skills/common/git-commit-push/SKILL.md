---
name: git-commit-push
description: 提交已跟踪改动和经用户确认的必要新文件、以 squash-aware 策略 rebase 并推送当前 Git 分支。适用于用户明确要求完成 commit 和 push，且不需要创建或更新 PR 的场景。
metadata:
  depends_on:
    - fix-with-pre-commit
---

# Git Commit Push

约定 `<skill_dir>` 为当前技能目录。使用 `<skill_dir>/scripts/commit_rebase_push.py` 完成提交、squash-aware rebase 与推送，不手工重建等价流程。

## 执行

1. 一次性检查 `git status --short --branch`、相关 diff 和 untracked 文件，确定本次提交边界：

   - tracked modifications 必须都属于本次任务；无关改动保留在工作区。
   - 仅当缺少某个 untracked 文件会导致当前代码、测试或配置逻辑不完整时，逐项展示文件路径与必要性，并要求用户确认。把用户明确同意加入的精确路径记为 `<confirmed_untracked_files>`；没有确认时不得暂存。
   - 若 `<confirmed_untracked_files>` 非空且仓库存在 `.pre-commit-config.yaml`，先执行 `pre-commit run --files <confirmed_untracked_files>`。按 `fix-with-pre-commit` 处理可修复问题并在相同范围复验；若 hook 明确判定某文件不应进入仓库，则不得添加该文件，并停止同步，避免提交缺少必要文件的不完整改动。
   - `<confirmed_untracked_files>` 非空且上述检查通过后，才执行 `git add -- <confirmed_untracked_files>`；列表为空时跳过。禁止使用目录、`.` 或 glob 扩大范围。

2. 根据整体 diff 生成简洁的中文提交说明，直接执行：

   ```bash
   python3 <skill_dir>/scripts/commit_rebase_push.py --message "<中文提交说明>"
   ```

3. 直接消费脚本输出的 JSON 事件：`skip` 表示无需继续；成功时汇报 `commit.head`、`rebase.changed`、`push.remote/branch` 与忽略的 untracked 文件。无需重复执行已成功的 Git 步骤。若 pre-commit 明确阻止本步骤暂存的某个新文件，将其精确路径记为 `<blocked_file>`，执行 `git restore --staged -- <blocked_file>` 仅撤出该文件并停止，不使用 `--no-verify` 绕过。

脚本自动探测 upstream、`origin`、远端默认分支和当前分支。仅在自动探测失败或用户明确指定非标准拓扑时，按 `--help` 使用 `--upstream-remote`、`--origin-remote`、`--default-branch` 或 `--current-branch` 显式指定；只提交和 rebase 时使用 `--no-push`。

## 硬约束

- 除执行第 1 步时经用户确认且通过 pre-commit 的必要新文件外，只处理已跟踪改动；禁止 `git add .`、目录级 `git add`、glob 或主动暂存其他 untracked 文件，不得新建或切换分支。
- `docs/agent_plans/` 与 `.agents/plans/` 默认是本地辅助物，除非用户明确要求，否则不得进入 stage 或 commit。
- 默认只推送 `origin`；只有用户明确指定时才覆盖 push remote。
- 有 `.pre-commit-config.yaml` 时只检查 staged 文件；禁止 `--no-verify` 和 `pre-commit run --all-files`。仅确认 commit hook 已覆盖相同检查时才使用 `--skip-pre-commit`。
- 出现 `rebase_conflict` 时立即停止并报告冲突文件；不得编辑冲突、`git add` 或 `git rebase --continue`，等待用户处理。
