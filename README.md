# backend-skills

后端开发相关 Cursor Agent 技能（pre-commit、CSV/YAML/JSON 等）。

## 依赖

- **Python**：带脚本的技能（csv-extract-export、yaml-json-convert）需 Python 3.6+；输出 YAML 时需安装 PyYAML（见各技能目录下的 `requirements.txt`）。
- **pre-commit**：`fix-with-pre-commit` 技能在项目根目录执行，需已安装 [pre-commit](https://pre-commit.com/) 且项目存在 `.pre-commit-config.yaml`。

## 安装

将本仓库 clone 到 Cursor 的 skills 目录下：

```bash
mkdir -p ~/.cursor/skills
cd ~/.cursor/skills
git clone https://github.com/lihuanshuai/backend-skills.git
# 若已有目录，可进入后 git pull 更新
```

完成后技能位于 `~/.cursor/skills/backend-skills/skills/`，Cursor Agent 会在「Agent Skills」中发现并读取各技能目录下的 `SKILL.md`。

使用带脚本的技能（如 csv-extract-export、yaml-json-convert）时，若需 YAML 输出，在对应技能目录下安装依赖即可：

```bash
cd ~/.cursor/skills/backend-skills/skills/csv-extract-export && pip install -r requirements.txt
cd ~/.cursor/skills/backend-skills/skills/yaml-json-convert && pip install -r requirements.txt
```

## 技能列表

| 技能目录 | 说明 |
|----------|------|
| `skills/fix-with-pre-commit/` | 检查并自动修复 pre-commit 报错，支持按文件列表或 linter 输出跑 hook |
| `skills/csv-extract-export/` | 从 CSV 按列提取并导出为 YAML/JSON |
| `skills/yaml-json-convert/` | YAML 与 JSON 互转，支持指定字段类型（如 int），脚本实现，依赖 PyYAML |