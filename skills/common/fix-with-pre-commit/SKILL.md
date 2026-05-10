---
name: fix-with-pre-commit
description: 检查并自动修复 pre-commit 报错。在需要跑 pre-commit、修复 hook 失败或希望自动修复到全部通过时使用此技能。
---

# 用 Pre-commit 检查并修复

## 概述

本技能用于在项目内运行 pre-commit，并根据报错尝试自动修复，直到检查通过或遇到需人工处理的问题。适用于提交前自检、CI 修复、或按指定文件列表跑 pre-commit 后修剩余问题。

## 使用方式

- **触发场景**：用户要求「跑 pre-commit」「修 pre-commit 报错」「让 pre-commit 通过」、或提供 ruff/其他 linter 输出文件（如 `ruff.out`）要求对其中涉及的文件跑 pre-commit 并修复。
- **工作目录**：在项目根目录执行（存在 `.pre-commit-config.yaml` 的目录）。

## 流程步骤

### 1. 环境检查与更新

- 确认项目根目录存在 `.pre-commit-config.yaml`。
- 若用户允许或项目惯例允许，可执行 `pre-commit autoupdate` 更新 hook 版本（可选）。

### 2. 运行 Pre-commit

- **不得使用 `--all-files` 对全部文件执行**。
- **仅 staged 文件**：`pre-commit run`（无参数时默认对 staged 文件执行）。
- **仅指定文件**：若用户给定了文件列表或某次 linter 输出（如 `ruff.out`）中的文件，提取这些文件的路径后执行：
  `pre-commit run --files <file1> <file2> ...`

### 3. 循环修复逻辑

若输出中出现 `Failed` 或报错：

1. **分析**：从报错日志中识别受影响的文件、行号及具体规则（如 ruff 规则码、mypy 错误类型）。
2. **修复**：
   - 优先处理可自动修复项（见 `<skill_dir>/references/` 下各工具修复表）；必要时再次运行 `pre-commit run`（仅针对刚改动的文件）以确认。
   - 对需人工判断的（见各参考文档中「需人工判断」部分）不做盲目自动改。
3. **验证**：修复后对受影响文件执行 `pre-commit run`（或 `pre-commit run --files <受影响文件>`）。
4. **迭代**：重复分析→修复→验证，直到全部通过或达到终止条件。

### 4. 终止与汇总

- 若某类报错在数轮（如 3 次）尝试后仍无法自动修复，或属于需人工决策的逻辑/类型问题：
  - 停止自动修复。
  - 汇总未解决的报错（文件、规则、简要说明）。
  - 明确提示用户：「以下报错无法自动修复，请手动处理：[报错列表]」。

## 执行指南

- 修复时尽量保持项目既有风格，符合项目 `AGENTS.md` 或等价文档中的编码标准。
- 若某次修复引入新的 linter 报错，应一并处理或回退并记录。
- 具体工具的修复方式见 `<skill_dir>/references/` 下各参考文档。

## References

修复参考文档位于 `<skill_dir>/references/`，按工具分文件：

- **ruff**：`<skill_dir>/references/ruff.md` — 可自动/半自动修复与需人工判断的规则码表
- **mypy**：`<skill_dir>/references/mypy.md` — 可自动/半自动修复与需人工判断的错误类型表

## 注意事项

- 对 `ruff.out` 等大文件：先从中提取**唯一文件路径**（如通过 `--> <path>:行:列` 模式），再只对这些路径执行 `pre-commit run --files ...`，避免全仓库全量跑导致超时或无关改动。
- 部分 hook 会自动修改文件（属于预期行为），其报错不一定代表存在需要修复的代码，应先区分是 hook 自身行为导致的变更还是真正的代码问题。