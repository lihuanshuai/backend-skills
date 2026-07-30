# 无构建 Lit 页面架构

## 发布模型

- 以后端模板作为页面入口，静态资源随后端应用发布。
- 不依赖单独前端发布系统，也不要求发布前运行 bundler。
- API 优先使用同域固定路径，例如 `/api/...`，让 pre、stage、prod 随后端环境自然切换。
- 不在模板里注入 `window.APP_ROUTE`、`window.API_BASE` 等全局变量让前端再解析路由。

## 后端模板与路由

- 每个后端 route 对应一个明确模板，例如列表页、详情页、编辑页分别使用不同模板。
- 模板直接输出当前页面 custom element，例如：

```html
<record-detail-app record-id="{{ record_id }}"></record-detail-app>
```

- 页面参数通过 HTML attribute 传给 custom element，组件内部读取 attribute。
- 公共模板只放 CSS、import map、公共结构和脚本 block：

```html
<script type="importmap">
  {
    "imports": {
      "lit": "{{ url_for('static', filename='app/vendor/lit.bundle.mjs') }}"
    }
  }
</script>
{% block scripts %}{% endblock %}
```

- 页面模板只加载当前 app module：

```html
{% block scripts %}
  <script type="module" src="{{ url_for('static', filename='app/apps/detail-app.js') }}"></script>
{% endblock %}
```

## JS 目录分层

- `apps/`：页面级 custom element，负责页面数据加载、状态和布局。
- `components/`：可复用 UI 或行为，不直接绑定某一个后端 route。
- `lib/`：无 UI 的通用逻辑，例如 API client、格式化、解析。
- `vendor/`：第三方 browser ESM 文件，随静态资源发布。
- 如果 `main.js` 只是 import 一个聚合文件，而聚合文件又全量 import 所有 app，优先删掉，改为模板按需加载 app module。

## Lit 写法

优先使用 Lit 模板保持可读性：

```js
litRender(
  html`
    <textarea
      class="form-control"
      .value=${this.formValue}
      @input=${(event) => {
        this.formValue = event.currentTarget.value;
      }}
    ></textarea>
  `,
  root,
);
```

规则：

- 文本和结构使用 `` html`...` ``，组件样式可用 `` css`...` ``。
- 表单值用属性绑定：`.value=${value}`。
- 布尔值用布尔绑定：`?checked=${checked}`、`?disabled=${disabled}`。
- 事件用事件绑定：`@input=${handler}`、`@click=${handler}`。
- 不要为了规避动态绑定问题改用字符串拼接或 `innerHTML` 绑定动态数据。
- 如果项目要复用 Bootstrap 或全局 CSS，可使用 light DOM 组件：

```js
import { LitElement } from "lit";

export class LightElement extends LitElement {
  createRenderRoot() {
    return this;
  }
}
```

## Import map

- 业务代码使用 bare import：

```js
import { html, render as litRender } from "lit";
```

- 后端模板中的本地 import map 将 bare import 映射到本地静态 vendor 文件。
- 不要在业务代码里直接写 `../vendor/lit.bundle.mjs`，避免 vendor 路径散落到各模块。
- import map 指向本地文件，不依赖 CDN runtime。
