# 建立索引（同步 / 生成 / 刷新）

**按需加载**：仅在用户要生成、刷新或重建 workspace 索引、或同步后需按规范**补全/校验简介**时阅读本文；纯查询已就绪索引时不必打开。

`<skill_dir>` 表示本文件所在目录（与 `SKILL.md` 同级），即 `skills/code-workspace-index/`。

## 何时执行

**典型说法**：同步 workspace、生成索引、刷新索引、更新了 `.code-workspace`、新增/删除多根目录、重建索引文件。

若索引文件缺失、明显过期，或用户明确要求刷新，再执行下文命令。

## 路径与产出

| 项 | 路径 |
|----|------|
| 同步脚本 | `<skill_dir>/scripts/sync_workspace_index.py` |
| 依赖清单 | `<skill_dir>/scripts/requirements.txt` |
| 默认输出 YAML | `<skill_dir>/workspace-index.local.yaml` |
| 默认输出 JSON | `<skill_dir>/workspace-index.local.json`（`--format json` 且未指定 `-o` 时） |

上述默认索引文件已在仓库根 `.gitignore` 中忽略，**勿提交**。若使用 `-o` 指向仓库内其它路径，须自行加入 `.gitignore`。

## 命令

```bash
pip install -r <skill_dir>/scripts/requirements.txt
python <skill_dir>/scripts/sync_workspace_index.py /path/to/repo.code-workspace
```

## 参数

| 参数 | 说明 |
|------|------|
| `workspace` | 必选。`.code-workspace` 文件路径。 |
| `-o` / `--output` | 可选。索引输出文件路径。 |
| `--format` | 可选。`yaml`（默认）或 `json`。当 `-o` 文件名**无** `.yaml`/`.yml`/`.json` 后缀时，用此选项决定写出格式。 |

## 脚本行为摘要

- 解析 `.code-workspace` 的 `folders`：写入 `meta`（含 `workspace_base`、`workspace_file`）、每条 `path_relative` / `path_resolved`、git remotes、语言/框架启发式、`project.summary` 启发式填充。
- JSONC：**简化**支持行内 `//` 与对象/数组**尾随逗号**（VS Code 常见）；仍失败时可改为严格 JSON。
- `summary`：按 README 分节（跳过「开发」等）、`pyproject` / `package.json` / `docs` / 根目录 `SKILL.md` / `app.yaml` 等顺序抽取；规则摘要见本文「注意事项」。

## 简介补全与校验（Agent；与脚本默认填充配合）

同步命令会写入脚本侧的 `project.summary` 启发式结果。**交付「索引可用」或依赖 summary 做语义检索前**，建议 Agent 按下述规则抽查、润色或纠偏（与同步流程同属「建立索引」阶段的可选步骤）。

**目标**：保证每条 `project.summary` **可读、可复查**。偏题、仍为兜底文案或需业务化表述时，由 Agent 读关键文件后**编辑索引**修正。

**关键文件**（按优先级，够用即停）：

1. `README.md` / `README.rst` / `readme.md`
2. `pyproject.toml`：`[project]` 的 `description`
3. `package.json`：`description`
4. `docs/` 下 `index.md`、`README.md`
5. 仓库根 `SKILL.md` 的 frontmatter `description`
6. 仍无有效信息：写一句如实说明（须非空）

**写回**：只改各条 `summary`；或再次执行本文「命令」中的同步（会**覆盖**已有 summary）。

### 校验标准（必须满足）

- 每条均有 `project.summary`；trim 后 **长度 > 0**
- 内容与 `path_resolved` 下文件可对证，禁止臆造

## 依赖环境

- Python 3.9+；从 `pyproject.toml` 读 `[project].description` 需 **3.11+**（`tomllib`），更低版本跳过该来源。
- YAML 输出：PyYAML（见 `requirements.txt`）。
- JSON 输出：标准库即可。

## 注意事项

- 脚本对 JSONC 做 **简化** 处理：行内 `//`、对象/数组末尾 **尾随逗号**（VS Code 常见）；仍失败时可改为严格 JSON。
- README 摘要：将常见 HTML 转为可解析文本后按 `##` 分节，**跳过**「开发 / 前端 / Grafana / Links(仅 URL)」等，**优先**「管理员后台」「Docs」「项目介绍」等小节；无可用正文时用一级标题；仍无法识别时回退其它来源（与 `sync_workspace_index.py` 一致）。
- 项目类型（`languages` / `frameworks`）为 **启发式**，可能为 `unknown`，以仓库实际为准。
- **勿提交**默认索引文件；自定义 `-o` 落在仓库内须自行 `.gitignore`。

## 完成后

同步成功后终端会打印输出路径。若已按上文完成简介校验，后续「查询索引」见主文档 [SKILL.md](SKILL.md) 的「需求二」。
