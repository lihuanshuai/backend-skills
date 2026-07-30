---
name: fix-with-pre-commit
description: 在最小文件范围内运行 pre-commit、修复真实问题并复验。适用于用户要求运行 pre-commit、修复 hook 失败，或根据 linter 输出处理相关文件的场景。
---

# 修复 Pre-commit

约定 `<skill_dir>` 为当前技能目录。依赖项目根目录中的 `.pre-commit-config.yaml` 和已安装的 `pre-commit`。

## 执行

1. 读取项目 `AGENTS.md` 或等价约束，确认项目根目录和验证范围：
   - 用户指定文件时，仅使用这些文件。
   - 用户提供 linter 输出时，只提取其中唯一、存在的仓库内文件路径。
   - 未指定范围时，只检查 staged 文件；没有 staged 文件则停止，不得扩大到全仓库。
2. 在项目根目录执行唯一适用的命令：

   ```bash
   pre-commit run --files <file1> <file2> ...
   # 或仅检查 staged 文件
   pre-commit run
   ```

3. 根据结果继续：
   - hook 自动修改文件时，先审查 diff，再对同一范围重跑；自动修改不等于检查已通过。
   - 仍有失败时，结合报错和上下文修复根因；工具的安全 autofix 可用，但必须审查结果。
   - 修复波及必要的调用方或 import 时，将这些文件加入后续验证范围，不顺手处理无关问题。
4. 重复同范围验证，直到通过；若失败需要业务决策、缺少依赖或连续尝试没有新进展，停止并报告准确 blocker。

## 硬约束

- 禁止 `pre-commit run --all-files`；禁止未经用户明确要求执行 `pre-commit autoupdate`。
- 不得仅为让检查通过而新增 `noqa`、`type: ignore`、exclude/ignore 配置、规则收窄或版本 pin；只有项目约定确有语义必要或用户明确要求时才可采用，并说明理由。
- 不得覆盖或回退用户已有改动；自动修复产生意外语义变化时停止并说明。
- 只报告实际执行的命令、文件范围和结果；局部通过不得表述为全仓库或 CI 通过，工具不可用也不得表述为代码失败。
