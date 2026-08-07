# 计划文档结构

## 文档头部

```markdown
# [功能名称] 实施计划

**目标：** [一句话描述最终产出]

**架构：** [2–3 句说明实现路径、关键边界和依赖顺序]

**技术栈：** [真实使用的关键技术或库]

**关联：** [Issue、需求文档或其他证据链接]

**假设：** [仅列出无法直接验证但不阻塞规划的假设；没有则写“无”]

---
```

## 任务总览

放在第一个具体任务之前，按实际执行顺序写 3–7 条；每条必须映射到后续任务。跨项目任务标明项目和依赖关系。

```markdown
## 任务总览

- 任务 1: [阶段目标]；产出 [关键文件、接口或行为]；验证 [主要命令或验收方式]
- 任务 2: [阶段目标]；产出 [关键文件、接口或行为]；验证 [主要命令或验收方式]
- 任务 3: [阶段目标]；产出 [关键文件、接口或行为]；验证 [主要命令或验收方式]
```

## 具体任务

```markdown
### 任务 N: [项目或组件] — [阶段目标]

**状态：** 未开始

**完成标志：** [可客观判定的条件]

**文件：**
- 创建: `exact/path/to/new_file.py` — [职责]
- 修改: `exact/path/to/existing.py` — `Class.method` 或 [配置项]
- 测试: `tests/exact/path/to/test_file.py` — `test_specific_behavior`

- [ ] **步骤 1: 写失败测试**

在 `tests/exact/path/to/test_file.py` 添加：

```python
def test_specific_behavior():
    result = function(input_value)
    assert result == expected_value
```

- [ ] **步骤 2: 验证测试按预期失败**

运行：`pytest tests/exact/path/to/test_file.py::test_specific_behavior -q`

预期：失败，原因是 [尚未实现的具体行为]。

- [ ] **步骤 3: 实现最小改动**

在 `exact/path/to/existing.py` 修改 `function`：

```python
def function(input_value):
    return expected_value
```

- [ ] **步骤 4: 验证任务完成**

运行：`pytest tests/exact/path/to/test_file.py::test_specific_behavior -q`

预期：通过；同时确认 [关键可观察行为]。

- [ ] **步骤 5: 扩大验证并提交**

运行：[受影响测试、静态检查或集成验证的精确命令]。

预期：[可观察结果]。

提交：

```bash
git add [本任务的精确文件列表]
git commit -m "[准确提交说明]"
```
```

按任务类型调整步骤，不为文档、配置或其他不适合 TDD 的改动虚构失败测试。代码块必须完整到可直接落地；提交步骤仅在仓库工作流允许且确有源码变更时使用。

## 状态机制

- 任务状态：`未开始` → `进行中` → `已完成 (YYYY-MM-DD)`。
- 步骤状态：验证通过后把 `- [ ]` 更新为 `- [x]`。
- 完成标志必须可客观判定，例如指定测试通过、Pre 验证通过或 PR 达到可合并状态；不要把 Agent 无权执行的 merge 作为其自行推进的步骤。
