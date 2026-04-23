# 执行建议（Agent 工作流）

1. 先识别当前仓库 Python 版本与历史兼容约束
2. 再决定使用类型注解还是保留 type comment
3. 修改 import 与命名时，避免引入行为变更；若涉及循环依赖、`TYPE_CHECKING` 或是否允许局部 import，先对照 `import-guide.md`
4. 提交前运行项目既有 lint / test / pre-commit
