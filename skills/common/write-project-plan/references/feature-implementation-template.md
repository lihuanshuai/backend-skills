# 功能需求实施计划样板

> 此样板演示「用户功能需求」的计划结构：明确需求 → API 草稿 → mock 代码 → 分步实现 → 联调修复。以 PR 合并为完成标志，关联 issue 地址。

**目标：** 为用户管理模块新增「用户偏好设置」功能，支持 CRUD 操作

**架构：** 新增 `UserPreference` model，通过 `/api/v1/preferences/` 端点提供 RESTful API，前端由独立 task 处理

**技术栈：** Django 4.2 + Django REST Framework + PostgreSQL

**关联 Issue：** `owner/repository#42`

---

## 任务 1: 明确用户需求与验收标准

**状态：** 未开始

**完成标志：** 用户明确确认需求要点与验收标准

**文件：**
- 创建: `docs/plans/2026-05-10-user-preferences.md`（即本计划文件）

- [ ] **步骤 1: 梳理需求要点**

从 `owner/repository#42` 提取需求要点，列出功能范围、边界条件与验收标准：

```markdown
## 需求要点
- 用户可创建、读取、更新、删除自己的偏好设置
- 偏好设置包含：语言、主题、通知频率
- 每个用户仅有一组偏好（one-to-one 与 User 关联）
- 未设置偏好时返回默认值

## 验收标准
- API 端点符合 OpenAPI 草稿
- 单测覆盖 CRUD 与默认值逻辑
- lint 与 type check 通过
```

- [ ] **步骤 2: 向用户确认需求要点**

将上述需求要点与验收标准呈现给用户，获得确认后方可继续编写后续任务。

---

## 任务 2: 编写 API 草稿

**状态：** 未开始

**完成标志：** PR owner/repository#42 合并到 main

**文件：**
- 创建: `docs/api/v1-preferences-openapi.yaml`

- [ ] **步骤 1: 编写 OpenAPI 草稿**

```yaml
openapi: "3.0.3"
info:
  title: User Preferences API
  version: "1.0.0"
paths:
  /api/v1/preferences/:
    get:
      summary: Retrieve user preferences
      responses:
        "200":
          description: Preferences object or default values
    post:
      summary: Create or update user preferences
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/PreferencesInput"
      responses:
        "201":
          description: Preferences created
        "200":
          description: Preferences updated
    delete:
      summary: Delete user preferences (reset to defaults)
      responses:
        "204":
          description: Preferences deleted
components:
  schemas:
    PreferencesInput:
      type: object
      properties:
        language:
          type: string
          default: "zh-CN"
        theme:
          type: string
          default: "light"
        notification_frequency:
          type: string
          enum: ["realtime", "daily", "weekly"]
          default: "daily"
    PreferencesOutput:
      type: object
      properties:
        language:
          type: string
        theme:
          type: string
        notification_frequency:
          type: string
```

- [ ] **步骤 2: 提交 API 草稿**

```bash
git add docs/api/v1-preferences-openapi.yaml
git commit -m "docs: add preferences API draft for owner/repository#42"
git push origin feature/user-preferences
```

- [ ] **步骤 3: 创建 PR 并合并**

```bash
gh pr create --title "docs: preferences API draft" --body "API 草稿，关联 owner/repository#42"
```

---

## 任务 3: 实现 mock 代码

**状态：** 未开始

**完成标志：** PR 合并到 main，pytest apps/preferences/tests/ 通过

**文件：**
- 创建: `apps/preferences/models.py`
- 创建: `apps/preferences/serializers.py`
- 创建: `apps/preferences/views.py`
- 创建: `apps/preferences/urls.py`
- 创建: `apps/preferences/tests/test_views.py`
- 修改: `config/settings.py:INSTALLED_APPS`
- 修改: `config/urls.py`

- [ ] **步骤 1: 创建 Django app 并注册**

```bash
python manage.py startapp preferences apps/preferences
```

修改 `config/settings.py` 的 `INSTALLED_APPS`：

```python
INSTALLED_APPS = [
    # ...existing apps...
    "apps.preferences",
]
```

- [ ] **步骤 2: 编写 mock model**

```python
from django.db import models
from django.conf import settings


class UserPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preferences",
    )
    language = models.CharField(max_length=10, default="zh-CN")
    theme = models.CharField(max_length=20, default="light")
    notification_frequency = models.CharField(
        max_length=20,
        choices=[("realtime", "Realtime"), ("daily", "Daily"), ("weekly", "Weekly")],
        default="daily",
    )

    class Meta:
        app_label = "preferences"
```

- [ ] **步骤 3: 编写 mock serializer**

```python
from rest_framework import serializers
from .models import UserPreference


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ["language", "theme", "notification_frequency"]
```

- [ ] **步骤 4: 编写 mock view（返回硬编码默认值）**

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def preferences_mock(request):
    return Response({
        "language": "zh-CN",
        "theme": "light",
        "notification_frequency": "daily",
    })
```

- [ ] **步骤 5: 编写测试验证 mock 端点可访问**

```python
import pytest
from django.test import RequestFactory
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_preferences_mock_returns_defaults():
    client = APIClient()
    user = ...  # create test user
    client.force_authenticate(user=user)
    response = client.get("/api/v1/preferences/")
    assert response.status_code == 200
    assert response.data["language"] == "zh-CN"
```

- [ ] **步骤 6: 运行测试确认通过**

运行: `pytest apps/preferences/tests/test_views.py -v`
预期: PASS

- [ ] **步骤 7: 配置 URL 路由**

修改 `apps/preferences/urls.py`：

```python
from django.urls import path
from .views import preferences_mock

urlpatterns = [
    path("preferences/", preferences_mock, name="preferences-mock"),
]
```

修改 `config/urls.py`：

```python
urlpatterns = [
    # ...existing patterns...
    path("api/v1/", include("apps.preferences.urls")),
]
```

- [ ] **步骤 8: 提交 mock 代码**

```bash
git add apps/preferences/ config/settings.py config/urls.py
git commit -m "feat: add preferences mock endpoint for owner/repository#42"
git push origin feature/user-preferences
```

- [ ] **步骤 9: 创建 PR 并合并**

```bash
gh pr create --title "feat: preferences mock endpoint" --body "Mock 端点，关联 owner/repository#42"
```

---

## 任务 4: 实现 Model 层

**状态：** 未开始

**完成标志：** PR 合并到 main，pytest apps/preferences/tests/test_models.py 通过

**文件：**
- 修改: `apps/preferences/models.py`
- 创建: `apps/preferences/tests/test_models.py`

- [ ] **步骤 1: 编写 model 单测**

```python
import pytest
from apps.preferences.models import UserPreference


@pytest.mark.django_db
def test_user_preference_defaults():
    user = ...  # create test user
    pref = UserPreference.objects.create(user=user)
    assert pref.language == "zh-CN"
    assert pref.theme == "light"
    assert pref.notification_frequency == "daily"


@pytest.mark.django_db
def test_user_preference_one_to_one():
    user = ...  # create test user
    UserPreference.objects.create(user=user)
    with pytest.raises(Exception):
        UserPreference.objects.create(user=user)  # 不允许重复创建
```

- [ ] **步骤 2: 运行测试确认失败**

运行: `pytest apps/preferences/tests/test_models.py -v`
预期: FAIL（model 已在 mock 阶段创建，但 one-to-one 约束测试验证边界）

- [ ] **步骤 3: 运行数据库迁移**

```bash
python manage.py makemigrations preferences
python manage.py migrate
```

- [ ] **步骤 4: 运行测试确认通过**

运行: `pytest apps/preferences/tests/test_models.py -v`
预期: PASS

- [ ] **步骤 5: 提交 model 层**

```bash
git add apps/preferences/models.py apps/preferences/tests/test_models.py apps/preferences/migrations/
git commit -m "feat: implement UserPreference model with tests for owner/repository#42"
git push origin feature/user-preferences
```

- [ ] **步骤 6: 创建 PR 并合并**

```bash
gh pr create --title "feat: UserPreference model" --body "Model 层实现，关联 owner/repository#42"
```

---

## 任务 5: 实现 View 与 Serializer 层

**状态：** 未开始

**完成标志：** PR 合并到 main，pytest apps/preferences/tests/test_views_full.py 通过

**文件：**
- 修改: `apps/preferences/views.py`
- 修改: `apps/preferences/serializers.py`
- 创建: `apps/preferences/tests/test_views_full.py`

- [ ] **步骤 1: 编写完整 CRUD 测试**

```python
import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestPreferencesCRUD:
    def setup_method(self):
        self.client = APIClient()
        self.user = ...  # create test user
        self.client.force_authenticate(user=self.user)

    def test_get_defaults_when_not_set(self):
        response = self.client.get("/api/v1/preferences/")
        assert response.status_code == 200
        assert response.data["language"] == "zh-CN"

    def test_create_preferences(self):
        response = self.client.post("/api/v1/preferences/", {"language": "en"})
        assert response.status_code == 201

    def test_update_preferences(self):
        self.client.post("/api/v1/preferences/", {"language": "en"})
        response = self.client.post("/api/v1/preferences/", {"language": "ja"})
        assert response.status_code == 200
        assert response.data["language"] == "ja"

    def test_delete_preferences(self):
        self.client.post("/api/v1/preferences/", {"language": "en"})
        response = self.client.delete("/api/v1/preferences/")
        assert response.status_code == 204
```

- [ ] **步骤 2: 运行测试确认失败**

运行: `pytest apps/preferences/tests/test_views_full.py -v`
预期: FAIL（mock view 不支持 POST/DELETE）

- [ ] **步骤 3: 替换 mock view 为完整实现**

```python
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserPreference
from .serializers import UserPreferenceSerializer

DEFAULTS = {"language": "zh-CN", "theme": "light", "notification_frequency": "daily"}


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def preferences(request):
    user = request.user
    pref = UserPreference.objects.filter(user=user).first()

    if request.method == "GET":
        if pref:
            serializer = UserPreferenceSerializer(pref)
            return Response(serializer.data)
        return Response(DEFAULTS)

    if request.method == "POST":
        if pref:
            serializer = UserPreferenceSerializer(pref, data=request.data, partial=True)
        else:
            serializer = UserPreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED if not pref else status.HTTP_200_OK)

    if request.method == "DELETE":
        if pref:
            pref.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

- [ ] **步骤 4: 运行测试确认通过**

运行: `pytest apps/preferences/tests/test_views_full.py -v`
预期: PASS

- [ ] **步骤 5: 提交 View 层实现**

```bash
git add apps/preferences/views.py apps/preferences/serializers.py apps/preferences/tests/test_views_full.py
git commit -m "feat: implement preferences CRUD endpoint for owner/repository#42"
git push origin feature/user-preferences
```

- [ ] **步骤 6: 创建 PR 并合并**

```bash
gh pr create --title "feat: preferences CRUD endpoint" --body "View 与 Serializer 层实现，关联 owner/repository#42"
```

---

## 任务 6: 联调与修复

**状态：** 未开始

**完成标志：** PR 合并到 main，pytest -v 全量通过，ruff check + mypy 无报错

**文件：**
- 修改: `apps/preferences/views.py`（如需修复）
- 修改: `apps/preferences/tests/test_views_full.py`（如需补充测试）

- [ ] **步骤 1: 运行全量测试**

运行: `pytest -v`
预期: 全部 PASS

- [ ] **步骤 2: 运行 lint 与 type check**

运行: `ruff check apps/preferences/ && mypy apps/preferences/`
预期: 无报错

- [ ] **步骤 3: 手动联调验证**

启动开发服务器，通过浏览器或 httpie 验证 CRUD 流程：

```bash
python manage.py runserver
http GET :8000/api/v1/preferences/ --auth user:pass
http POST :8000/api/v1/preferences/ language=en --auth user:pass
http DELETE :8000/api/v1/preferences/ --auth user:pass
```

- [ ] **步骤 4: 修复联调发现的 bug（如有）**

根据联调结果修复代码，补充测试，再次运行验证。

- [ ] **步骤 5: 最终提交与 PR**

```bash
git add -A
git commit -m "fix: integration fixes for preferences feature owner/repository#42"
git push origin feature/user-preferences
gh pr create --title "fix: preferences integration fixes" --body "联调修复，关联 owner/repository#42"
```