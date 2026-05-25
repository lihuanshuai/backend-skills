# 计划文档结构说明

> 此文档说明计划文档的标准结构和格式要求。

## 计划文档头部（必须）

```markdown
# [功能名称] 实施计划

**目标：** [一句话描述最终产出]

**架构：** [2-3 句说明实现思路]

**技术栈：** [关键技术/库]

**关联：** [关联的 Issue 地址或需求文档链接，如 `owner/repo#123` 或 `docs/requirements/feature.md`]

---
```

## 任务总览（必须）

具体任务清单之前必须先给出任务总览，用于让执行者先理解整体顺序、边界和验证闭环。

```markdown
## 任务总览

- 任务 1: [阶段目标]，产出 [关键文件/接口/行为]，验证 [主要命令或验收方式]
- 任务 2: [阶段目标]，产出 [关键文件/接口/行为]，验证 [主要命令或验收方式]
- 任务 3: [阶段目标]，产出 [关键文件/接口/行为]，验证 [主要命令或验收方式]
```

要求：
- 任务总览必须出现在第一个 `### 任务 N:` 之前
- 总览条目按执行顺序排列，且必须能映射到后续一个或多个具体任务
- 总览只写阶段目标、关键产出和主要验证方式，不替代后续任务中的完整步骤、代码和命令
- 多项目协作时，在总览条目中标明项目名与依赖顺序

## 每个任务格式

```markdown
### 任务 N: [组件名称]

**状态：** 未开始

**完成标志：** [具体验证条件，如 "PR 合并到 main"、"全量测试通过"]

**文件：**
- 创建: `exact/path/to/file.py`
- 修改: `exact/path/to/existing.py:123-145`
- 测试: `tests/exact/path/to/test.py`

- [ ] **步骤 1: 写失败测试**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **步骤 2: 运行测试确认失败**

运行: `pytest tests/path/test.py::test_name -v`
预期: FAIL，报错 "function not defined"

- [ ] **步骤 3: 写最小实现**

```python
def function(input):
    return expected
```

- [ ] **步骤 4: 运行测试确认通过**

运行: `pytest tests/path/test.py::test_name -v`
预期: PASS

- [ ] **步骤 5: 提交**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
```

## 状态机制

- **任务级状态**（`**状态：**` 行）：`未开始` → `进行中` → `已完成`，执行时由 `execute-project-plan` 技能更新
- **步骤级状态**（checkbox）：`- [ ]` → `- [x]`，每步验证通过后勾选
- **完成标志**：每个任务必须声明具体的完成条件，禁止模糊描述（如 "功能实现"），必须可客观判定（如 "PR owner/repo#123 合并到 main"、"pytest tests/ 全量通过"）
