# 新增 Python 基础 CI

约定 `<skill_dir>` 为当前技能目录，`<repo_dir>` 为目标项目根目录。

## 配置

1. 盘点 `<repo_dir>` 已有 hook、`[tool.*]`、依赖文件和 CI 入口，确认 Python runtime、包管理方式及待检查模块。
2. 从 `<skill_dir>/references/pre-commit-config-template.yaml` 和 `<skill_dir>/references/pyproject-template.toml` 选择缺失部分合并；不得覆盖已有无关配置或重复 repo、hook、表段。
3. 根据项目事实调整：
   - `ruff-check` 与 `ruff-format` 保持为独立 hook。
   - Python 3-only 使用 `I,UP`；Python 2/混合运行时使用 `I`。
   - 默认不启用 `--unsafe-fixes`；行宽、exclude、quote style 和 Mypy 严格度沿用项目基线。
   - hook `rev` 对齐团队或相邻仓库已验证版本，不把模板版本视为升级要求。
4. 在项目实际使用的开发或 CI 依赖位置声明 Ruff、Mypy、pre-commit；若 hook 有额外 import 依赖，按其隔离环境补 `additional_dependencies`，不要假设项目环境会透传给 hook。
5. 同步 CI 任务和 README，使本地文档、hook 与 CI 调用同一入口；不为文档示例额外发明一套命令。

## 验证

- 先对变更文件或少量代表文件运行 `pre-commit run --files <files>`，审查自动修复后复跑。
- 再执行目标项目真实 lint、format-check 和 type-check CI 脚本；缺少可运行环境时准确报告，不能以模板解析成功代替 CI。
- 确认没有重复配置、未声明依赖或不受 CI 消费的孤立工具配置。
