# 迁移 Legacy Linters 到 Ruff

约定 `<skill_dir>` 为当前技能目录，`<repo_dir>` 为目标项目根目录。

## 迁移

1. 搜索 Black、isort、Flake8、autoflake 和旧 Ruff 在以下位置的全部入口：
   - `.pre-commit-config.yaml`、`pyproject.toml` 及其他工具配置。
   - requirements、开发依赖和 lock 文件。
   - CI 脚本、任务定义、归档文件名和 README 命令。
2. 先记录原行为，再合并 Ruff：
   - Black 行宽、exclude 和 quote 诉求映射到 `[tool.ruff]` / `[tool.ruff.format]`。
   - isort 行为由 Ruff `I` 接管，并保留必要的 first-party/section 配置。
   - Flake8 select、ignore、per-file-ignores 和插件规则逐项映射到 `[tool.ruff.lint]`；不能映射的规则必须显式说明。
   - autoflake 的 import/unused 清理映射到对应 Ruff 规则，不默认启用 unsafe fixes。
3. 将 pre-commit 收口为独立的 `ruff-check` 与 `ruff-format` hook。Python 3-only 才在 check hook 启用 `I,UP`；Python 2/混合运行时只启用 `I`。
4. 只有 Ruff 已覆盖且 CI 不再调用后，才从 hook、配置、依赖和 CI 中删除 legacy 工具。保留平台要求的任务类型或归档契约，除非目标 CI 同时完成迁移。
5. Mypy 不属于 Ruff 替代范围；保留既有入口，新增或调整严格度时按注解覆盖率单独决策。

## 验证

1. 对同一组代表文件分别记录迁移前后结果，确认格式、import 排序和关键 lint 覆盖没有意外丢失。
2. 对变更文件运行新 pre-commit hook，审查 autofix 后复跑。
3. 执行目标项目真实 CI lint/format/type-check 入口，并确认输出文件与归档配置一致。
4. 搜索 legacy 工具残留；区分仍有意保留的配置、文档历史和应删除的执行入口，不做盲目全局替换。

## 终止条件

- 无法确认 runtime、插件规则映射、CI task 契约或版本兼容性时停止并列出缺口，不猜测删除。
- 若迁移需要大范围历史格式化或新增大量 ignore，拆成独立迁移计划，不把范围扩进基础配置提交。
