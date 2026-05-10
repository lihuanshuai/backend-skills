# 代码迁移实施计划样板

> 此样板演示「代码迁移」的计划结构：先在分支上逐步实现并提交 commit，执行完后逐个 cherry-pick 到独立分支提交 PR。以 PR 合并为完成标志，关联 issue 地址。

**目标：** 将旧版通知模块从 `apps.notifications_legacy` 迁移到 `apps.notifications`，采用新版消息队列架构

**架构：** 分 5 个迁移阶段逐步替换旧模块：新增新版 model → 实现新版 view → 切换 URL 路由 → 数据迁移 → 删除旧代码。每阶段完成后 commit 并推送，最终逐阶段 cherry-pick 提交独立 PR

**技术栈：** Django 4.2 + Celery + PostgreSQL

**关联 Issue：** `owner/repository#87`

---

## 执行策略

本迁移采用「先逐步 commit，后逐个 cherry-pick 提交 PR」策略：

1. 在 `migration/notifications-v2` 分支上按任务顺序逐步实现，每完成一个任务 commit 并 push
2. 所有任务完成后，逐个将 commit cherry-pick 到独立分支，提交独立 PR
3. PR 按依赖顺序逐个合并

Cherry-pick 流程示例：

```bash
# 假设任务 1 的 commit 为 abc1234
git checkout -b migration/notifications-v2-model main
git cherry-pick abc1234
git push origin migration/notifications-v2-model
gh pr create --title "feat: new Notification model" --body "迁移阶段 1，关联 owner/repository#87"

# 假设任务 2 的 commit 为 def5678
git checkout -b migration/notifications-v2-view main
git cherry-pick def5678
git push origin migration/notifications-v2-view
gh pr create --title "feat: new Notification view" --body "迁移阶段 2，关联 owner/repository#87"
```

---

## 任务 1: 新增新版 Notification model

**状态：** 未开始

**完成标志：** commit 推送到 `migration/notifications-v2` 分支，pytest apps/notifications/tests/test_models.py 通过

**文件：**
- 创建: `apps notifications/models.py`
- 创建: `apps/notifications/migrations/0001_initial.py`
- 创建: `apps/notifications/tests/test_models.py`
- 修改: `config/settings.py:INSTALLED_APPS`

- [ ] **步骤 1: 创建 Django app 并注册**

```bash
python manage.py startapp notifications apps/notifications
```

修改 `config/settings.py` 的 `INSTALLED_APPS`：

```python
INSTALLED_APPS = [
    # ...existing apps...
    "apps.notifications",
]
```

- [ ] **步骤 2: 编写 model 测试**

```python
import pytest
from apps.notifications.models import Notification


@pytest.mark.django_db
def test_notification_creation():
    user = ...  # create test user
    notification = Notification.objects.create(
        user=user,
        title="Test",
        body="Test body",
        channel="in_app",
    )
    assert notification.title == "Test"
    assert notification.is_read is False


@pytest.mark.django_db
def test_notification_default_channel():
    user = ...  # create test user
    notification = Notification.objects.create(user=user, title="A", body="B")
    assert notification.channel == "in_app"
```

- [ ] **步骤 3: 运行测试确认失败**

运行: `pytest apps/notifications/tests/test_models.py -v`
预期: FAIL

- [ ] **步骤 4: 实现 Notification model**

```python
from django.db import models
from django.conf import settings


class Notification(models.Model):
    CHANNEL_CHOICES = [
        ("in_app", "In App"),
        ("email", "Email"),
        ("sms", "SMS"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="in_app")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "notifications"
        ordering = ["-created_at"]
```

- [ ] **步骤 5: 生成并运行迁移**

```bash
python manage.py makemigrations notifications
python manage.py migrate
```

- [ ] **步骤 6: 运行测试确认通过**

运行: `pytest apps/notifications/tests/test_models.py -v`
预期: PASS

- [ ] **步骤 7: 提交并推送**

```bash
git add apps/notifications/ config/settings.py
git commit -m "feat: add Notification model (migration phase 1) owner/repository#87"
git push origin migration/notifications-v2
```

---

## 任务 2: 实现新版 Notification view 与 serializer

**状态：** 未开始

**完成标志：** commit 推送到 `migration/notifications-v2` 分支，pytest apps/notifications/tests/test_views.py 通过

**文件：**
- 创建: `apps/notifications/serializers.py`
- 创建: `apps/notifications/views.py`
- 创建: `apps/notifications/tests/test_views.py`
- 创建: `apps/notifications/urls.py`

- [ ] **步骤 1: 编写 view 测试**

```python
import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestNotificationViews:
    def setup_method(self):
        self.client = APIClient()
        self.user = ...  # create test user
        self.client.force_authenticate(user=self.user)

    def test_list_notifications(self):
        response = self.client.get("/api/v2/notifications/")
        assert response.status_code == 200

    def test_mark_as_read(self):
        ...  # create notification for user
        response = self.client.patch("/api/v2/notifications/1/", {"is_read": True})
        assert response.status_code == 200
```

- [ ] **步骤 2: 运行测试确认失败**

运行: `pytest apps/notifications/tests/test_views.py -v`
预期: FAIL

- [ ] **步骤 3: 实现 serializer**

```python
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "body", "channel", "is_read", "created_at"]
        read_only_fields = ["id", "created_at"]
```

- [ ] **步骤 4: 实现 view**

```python
from rest_framework import viewsets, permissions, mixins
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
```

- [ ] **步骤 5: 配置 URL 路由**

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
```

- [ ] **步骤 6: 运行测试确认通过**

运行: `pytest apps/notifications/tests/test_views.py -v`
预期: PASS

- [ ] **步骤 7: 提交并推送**

```bash
git add apps/notifications/serializers.py apps/notifications/views.py apps/notifications/tests/test_views.py apps/notifications/urls.py
git commit -m "feat: add Notification view & serializer (migration phase 2) owner/repository#87"
git push origin migration/notifications-v2
```

---

## 任务 3: 切换 URL 路由指向新版端点

**状态：** 未开始

**完成标志：** commit 推送到 `migration/notifications-v2` 分支，pytest -v 全量通过

**文件：**
- 修改: `config/urls.py`

- [ ] **步骤 1: 在 config/urls.py 中注册新版路由**

修改 `config/urls.py`，在旧版路由旁新增新版路由（暂不删除旧路由，保持兼容）：

```python
urlpatterns = [
    # 旧版（暂时保留）
    path("api/v1/notifications/", include("apps.notifications_legacy.urls")),
    # 新版
    path("api/v2/", include("apps.notifications.urls")),
]
```

- [ ] **步骤 2: 运行全量测试确认无破坏**

运行: `pytest -v`
预期: 全部 PASS

- [ ] **步骤 3: 提交并推送**

```bash
git add config/urls.py
git commit -m "feat: register v2 notification routes (migration phase 3) owner/repository#87"
git push origin migration/notifications-v2
```

---

## 任务 4: 数据迁移脚本

**状态：** 未开始

**完成标志：** commit 推送到 `migration/notifications-v2` 分支，数据迁移前后记录数一致

**文件：**
- 创建: `apps/notifications/migrations/0002_migrate_legacy_data.py`

- [ ] **步骤 1: 编写数据迁移**

```python
from django.db import migrations


def migrate_legacy_notifications(apps, schema_editor):
    LegacyNotification = apps.get_model("notifications_legacy", "LegacyNotification")
    Notification = apps.get_model("notifications", "Notification")
    for legacy in LegacyNotification.objects.all():
        Notification.objects.create(
            user_id=legacy.user_id,
            title=legacy.title,
            body=legacy.body,
            channel="in_app",  # 旧版无 channel 字段，统一映射为 in_app
            is_read=legacy.read,
        )


def reverse_migrate(apps, schema_editor):
    Notification = apps.get_model("notifications", "Notification")
    LegacyNotification = apps.get_model("notifications_legacy", "LegacyNotification")
    for notification in Notification.objects.all():
        LegacyNotification.objects.create(
            user_id=notification.user_id,
            title=notification.title,
            body=notification.body,
            read=notification.is_read,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0001_initial"),
        ("notifications_legacy", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(migrate_legacy_notifications, reverse_migrate),
    ]
```

- [ ] **步骤 2: 运行迁移并验证数据**

```bash
python manage.py migrate
python manage.py shell -c "
from apps.notifications.models import Notification
print(f'New notifications count: {Notification.objects.count()}')
"
```

预期: 输出与旧版数据量一致

- [ ] **步骤 3: 提交并推送**

```bash
git add apps/notifications/migrations/0002_migrate_legacy_data.py
git commit -m "feat: data migration from legacy to new notification (migration phase 4) owner/repository#87"
git push origin migration/notifications-v2
```

---

## 任务 5: 删除旧版代码

**状态：** 未开始

**完成标志：** commit 推送到 `migration/notifications-v2` 分支，pytest -v 全量通过，ruff check + mypy 无报错

**文件：**
- 删除: `apps/notifications_legacy/`（整个目录）
- 修改: `config/settings.py:INSTALLED_APPS`（移除 `notifications_legacy`）
- 修改: `config/urls.py`（移除旧版路由）

- [ ] **步骤 1: 移除旧版 app 注册**

修改 `config/settings.py`，删除 `INSTALLED_APPS` 中的 `"apps.notifications_legacy"`。

- [ ] **步骤 2: 移除旧版 URL 路由**

修改 `config/urls.py`，删除旧版路由行：

```python
urlpatterns = [
    path("api/v2/", include("apps.notifications.urls")),
]
```

- [ ] **步骤 3: 删除旧版 app 目录**

```bash
git rm -r apps/notifications_legacy/
```

- [ ] **步骤 4: 运行全量测试与 lint**

运行: `pytest -v && ruff check apps/notifications/ && mypy apps/notifications/`
预期: 全部 PASS，无报错

- [ ] **步骤 5: 提交并推送**

```bash
git add -A
git commit -m "feat: remove legacy notification module (migration phase 5) owner/repository#87"
git push origin migration/notifications-v2
```

---

## 逐个提交 PR

所有任务完成后，查看 `migration/notifications-v2` 分支的 commit 历史：

```bash
git log main..migration/notifications-v2 --oneline
```

假设输出为：

```
abc1234 feat: add Notification model (migration phase 1) owner/repository#87
def5678 feat: add Notification view & serializer (migration phase 2) owner/repository#87
ghi9012 feat: register v2 notification routes (migration phase 3) owner/repository#87
jkl3456 feat: data migration from legacy to new notification (migration phase 4) owner/repository#87
mno7890 feat: remove legacy notification module (migration phase 5) owner/repository#87
```

逐个 cherry-pick 并提交 PR：

- [ ] **PR 1: model 层**

```bash
git checkout -b migration/notifications-v2-model main
git cherry-pick abc1234
git push origin migration/notifications-v2-model
gh pr create --title "feat: new Notification model" --body "迁移阶段 1/5 — 新增 model 层，关联 owner/repository#87"
```

**完成标志：** PR 合并到 main

- [ ] **PR 2: view 与 serializer 层**

```bash
git checkout -b migration/notifications-v2-view main
git cherry-pick def5678
git push origin migration/notifications-v2-view
gh pr create --title "feat: new Notification view & serializer" --body "迁移阶段 2/5 — view 层实现，关联 owner/repository#87"
```

**完成标志：** PR 合并到 main

- [ ] **PR 3: URL 路由切换**

```bash
git checkout -b migration/notifications-v2-routes main
git cherry-pick ghi9012
git push origin migration/notifications-v2-routes
gh pr create --title "feat: register v2 notification routes" --body "迁移阶段 3/5 — 路由注册，关联 owner/repository#87"
```

**完成标志：** PR 合并到 main

- [ ] **PR 4: 数据迁移**

```bash
git checkout -b migration/notifications-v2-data main
git cherry-pick jkl3456
git push origin migration/notifications-v2-data
gh pr create --title "feat: data migration script" --body "迁移阶段 4/5 — 数据迁移，关联 owner/repository#87"
```

**完成标志：** PR 合并到 main

- [ ] **PR 5: 删除旧版代码**

```bash
git checkout -b migration/notifications-v2-cleanup main
git cherry-pick mno7890
git push origin migration/notifications-v2-cleanup
gh pr create --title "feat: remove legacy notification module" --body "迁移阶段 5/5 — 删除旧版，关联 owner/repository#87"
```

**完成标志：** PR 合并到 main