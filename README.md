# backend-skills

后端开发相关 Cursor Agent 技能（pre-commit、CSV/YAML/JSON 等）。

## 依赖

- **Python**：带脚本的技能（csv-extract-export、yaml-json-convert、json-object-array-convert）需 Python 3.6+；输出 YAML 时需安装 PyYAML（见各技能目录下的 `scripts/requirements.txt`）。json-object-array-convert 仅用标准库，无额外依赖。
- **pre-commit**：`fix-with-pre-commit` 技能在项目根目录执行，需已安装 [pre-commit](https://pre-commit.com/) 且项目存在 `.pre-commit-config.yaml`。
- **com2ann**：`com2ann-type-comment-to-hint` 技能需 Python 3.8+ 并安装 `pip install com2ann`。

## 安装

将本仓库 clone 到 Cursor 的 skills 目录下：

```bash
mkdir -p ~/.cursor/skills
cd ~/.cursor/skills
git clone https://github.com/lihuanshuai/backend-skills.git
# 若已有目录，可进入后 git pull 更新
```

完成后技能位于 `~/.cursor/skills/backend-skills/skills/`，Cursor Agent 会在「Agent Skills」中发现并读取各技能目录下的 `SKILL.md`。

使用带脚本的技能（如 csv-extract-export、yaml-json-convert）时，若需 YAML 输出，在对应技能目录下安装 `scripts/requirements.txt` 依赖即可：

```bash
cd ~/.cursor/skills/backend-skills/skills/csv-extract-export && pip install -r scripts/requirements.txt
cd ~/.cursor/skills/backend-skills/skills/yaml-json-convert && pip install -r scripts/requirements.txt
```

## 技能列表

### 项目维护

| 技能目录 | 说明 |
|----------|------|
| [skills/backend-skill-project-conventions/](skills/backend-skill-project-conventions/) | 维护 backend-skills 的项目约束，统一 frontmatter、路径引用、依赖声明与 README 技能列表同步规则 |

### 代码规范与工具

| 技能目录 | 说明 |
|----------|------|
| [skills/python-code-style-guide/](skills/python-code-style-guide/) | Python 通用代码风格规范，覆盖局部 import 约束、变量命名、类型注释与类型注解实践，适用于跨后端仓库统一代码约束 |
| [skills/replace-black-with-ruff/](skills/replace-black-with-ruff/) | 将 black、isort、flake8（及可选 autoflake）替换为 ruff，统一配置 pre-commit 与 pyproject.toml |
| [skills/fix-with-pre-commit/](skills/fix-with-pre-commit/) | 检查并自动修复 pre-commit 报错，支持按文件列表或 linter 输出跑 hook |
| [skills/com2ann-type-comment-to-hint/](skills/com2ann-type-comment-to-hint/) | 使用 com2ann 将 type comment 转为 type hint（函数注解），适用于迁移 Python 2/3 兼容写法到纯 Python 3 注解 |
| [skills/add-python-basic-code-checks/](skills/add-python-basic-code-checks/) | 添加 Python 基础代码检查配置模板 including ruff mypy pre-commit 与 pyproject.toml 和 .pre-commit-config.yaml 示例 |

### 数据转换

| 技能目录 | 说明 |
|----------|------|
| [skills/csv-extract-export/](skills/csv-extract-export/) | 从 CSV 按列提取并导出为 YAML/JSON |
| [skills/yaml-json-convert/](skills/yaml-json-convert/) | YAML 与 JSON 互转，支持指定字段类型（如 int），脚本实现，依赖 PyYAML |
| [skills/json-object-array-convert/](skills/json-object-array-convert/) | JSON 对象与数组互转（对象→数组、数组→对象），需提供 key 字段名，仅用标准库 |

### 网页抓取

| 技能目录 | 说明 |
|----------|------|
| [skills/crawl4ai-web-scraping/](skills/crawl4ai-web-scraping/) | 使用 Crawl4AI 抓取网页并保存为 Markdown，适用于 URL 转 Markdown 或批量抓取导出 |

### 版本与依赖

| 技能目录 | 说明 |
|----------|------|
| [skills/python-bump-version/](skills/python-bump-version/) | 提升 Python 包版本，支持 setup.py、setup.cfg、pyproject.toml，可选 patch/minor/major |
| [skills/python-upgrade-deps/](skills/python-upgrade-deps/) | 升级依赖包版本，支持 pip-req.txt、requirements.txt、pyproject.toml |

### 流程与规划

| 技能目录 | 说明 |
|----------|------|
| [skills/plan-and-execute/](skills/plan-and-execute/) | 通用的「先规划、再确认、再执行」流程，适用于复杂产品需求、重构、迁移、拆分大文件等分步任务 |
| [skills/git-commit-push/](skills/git-commit-push/) | 执行 Git 提交、rebase --onto 与推送的标准流程，包含 staged 限制、pre-commit 约束与冲突处理 |
