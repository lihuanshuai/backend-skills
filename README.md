# backend-skills

后端开发相关 Cursor Agent 技能（pre-commit、CSV/YAML/JSON 等）。

## 依赖

- **Python**：带脚本的技能（data-format-convert）需 Python 3.6+；输出 YAML 时需安装 PyYAML（见技能目录下的 `scripts/requirements.txt`）。JSON 对象/数组互转仅用标准库，无额外依赖。
- **pre-commit**：`fix-with-pre-commit` 技能在项目根目录执行，需已安装 [pre-commit](https://pre-commit.com/) 且项目存在 `.pre-commit-config.yaml`。

## 安装

将本仓库 clone 到 Cursor 的 skills 目录下：

```bash
mkdir -p ~/.cursor/skills
cd ~/.cursor/skills
git clone https://github.com/lihuanshuai/backend-skills.git
# 若已有目录，可进入后 git pull 更新
```

完成后技能位于 `~/.cursor/skills/backend-skills/skills/`（含 `python/` 和 `common/` 两个子目录），Cursor Agent 会在「Agent Skills」中发现并读取各技能目录下的 `SKILL.md`。

使用带脚本的技能（data-format-convert）时，若需 YAML 输出，在技能目录下安装 `scripts/requirements.txt` 依赖即可：

```bash
cd ~/.cursor/skills/backend-skills/skills/common/data-format-convert && pip install -r scripts/requirements.txt
```

## 技能列表

### 项目维护

| 技能目录 | 说明 |
|----------|------|
| [skills/common/backend-skill-project-conventions/](skills/common/backend-skill-project-conventions/) | 维护 backend-skills 的项目约束，统一 frontmatter、路径引用、依赖声明与 README 技能列表同步规则 |

### 代码规范与工具

| 技能目录 | 说明 |
|----------|------|
| [skills/common/lit-code-style-guide/](skills/common/lit-code-style-guide/) | Lit 前端代码风格与无构建发布规范，覆盖后端模板入口、本地 import map、页面级模块加载、vendor 管理与真实页面验证 |
| [skills/python/replace-black-with-ruff/](skills/python/replace-black-with-ruff/) | 将 black、isort、flake8（及可选 autoflake）替换为 ruff，统一配置 pre-commit 与 pyproject.toml |
| [skills/common/fix-with-pre-commit/](skills/common/fix-with-pre-commit/) | 检查并自动修复 pre-commit 报错，支持按文件列表或 linter 输出跑 hook |
| [skills/python/add-python-basic-code-checks/](skills/python/add-python-basic-code-checks/) | 添加 Python 基础代码检查配置模板 including ruff mypy pre-commit 与 pyproject.toml 和 .pre-commit-config.yaml 示例 |

### 数据转换

| 技能目录 | 说明 |
|----------|------|
| [skills/common/data-format-convert/](skills/common/data-format-convert/) | 数据格式转换与提取，覆盖 CSV 提取导出、YAML/JSON 互转、JSON 对象/数组互转，按需求路由到具体子任务 |

### 版本与依赖

| 技能目录 | 说明 |
|----------|------|
| [skills/python/python-bump-version/](skills/python/python-bump-version/) | 提升 Python 包版本，支持 setup.py、setup.cfg、pyproject.toml，可选 patch/minor/major |
| [skills/python/python-upgrade-deps/](skills/python/python-upgrade-deps/) | 升级依赖包版本，支持 pip-req.txt、requirements.txt、pyproject.toml |

### 流程与规划

| 技能目录 | 说明 |
|----------|------|
| [skills/common/write-project-plan/](skills/common/write-project-plan/) | 编写详尽的实施计划，面向零项目上下文的工程师，包含完整代码、命令与验证方式，遵循 TDD 和零占位符原则 |
| [skills/common/execute-project-plan/](skills/common/execute-project-plan/) | 执行已写就的项目实施计划，按步骤推进并逐步验证，通过计划文件维护进度与状态 |
| [skills/common/git-commit-push/](skills/common/git-commit-push/) | 执行 Git 提交、rebase --onto 与推送的标准流程，包含 staged 限制、pre-commit 约束与冲突处理 |
