# 无构建 Lit 前端规范

## 发布模型

- 以后端模板作为页面入口，静态资源随后端应用发布。
- 不依赖单独前端发布系统，也不要求发布前运行 bundler。
- API 优先使用同域固定路径，例如 `/api/...`，让 pre、stage、prod 随后端环境自然切换。
- 不在模板里注入 `window.APP_ROUTE`、`window.API_BASE` 等全局变量让前端再解析路由。

## 后端模板与路由

- 每个后端 route 对应一个明确模板，例如列表页、详情页、编辑页分别使用不同模板。
- 模板直接输出当前页面 custom element，例如：

```html
<yaml-config-detail-app config-id="{{ config_id }}"></yaml-config-detail-app>
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

推荐结构：

```text
static/<app>/
├── apps/
│   ├── list-app.js
│   ├── detail-app.js
│   └── meta-app.js
├── components/
│   ├── page-element.js
│   └── value-editor.js
├── lib/
│   ├── api.js
│   └── yaml.js
└── vendor/
    ├── lit.bundle.mjs
    └── js-yaml.bundle.mjs
```

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
      .value=${this.yamlText}
      @input=${(event) => {
        this.yamlText = event.currentTarget.value;
      }}
    ></textarea>
  `,
  root,
);
```

规则：

- 文本和结构使用 `html``...`` `，样式进入组件时可用 `css``...`` `。
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
import * as yaml from "js-yaml";
```

- 后端模板中的本地 import map 将 bare import 映射到本地静态 vendor 文件。
- 不要在业务代码里直接写 `../vendor/lit.bundle.mjs`，避免 vendor 路径散落到各模块。
- import map 指向本地文件，不依赖 CDN runtime。

## Vendor 更新工具

无构建项目仍应有 vendor 更新入口，例如 Makefile：

```makefile
STATIC_DIR := static/app
VENDOR_DIR := $(STATIC_DIR)/vendor

LIT_VERSION := 3.3.1
BOOTSTRAP_VERSION := 5.2.3

LIT_URL := https://esm.sh/lit@$(LIT_VERSION)/es2022/lit.bundle.mjs
BOOTSTRAP_URL := https://cdn.jsdelivr.net/npm/bootstrap@$(BOOTSTRAP_VERSION)/dist/css/bootstrap.min.css

CURL := curl -fsSL --retry 3 --retry-delay 1 --connect-timeout 10 --max-time 120

.PHONY: vendor-update vendor-check

vendor-update:
	@mkdir -p "$(VENDOR_DIR)"
	$(CURL) "$(LIT_URL)" -o "$(VENDOR_DIR)/lit.bundle.mjs"
	$(CURL) "$(BOOTSTRAP_URL)" -o "$(STATIC_DIR)/bootstrap.min.css"

vendor-check:
	@tmp=$$(mktemp -d); \
	trap 'rm -rf "$$tmp"' EXIT; \
	$(CURL) "$(LIT_URL)" -o "$$tmp/lit.bundle.mjs"; \
	$(CURL) "$(BOOTSTRAP_URL)" -o "$$tmp/bootstrap.min.css"; \
	cmp -s "$$tmp/lit.bundle.mjs" "$(VENDOR_DIR)/lit.bundle.mjs"; \
	cmp -s "$$tmp/bootstrap.min.css" "$(STATIC_DIR)/bootstrap.min.css"
```

原则：

- 工具只下载和校验静态文件，不安装 npm 依赖，不生成 `node_modules`，不 bundle。
- CSS vendor 也纳入同一套工具，例如 `bootstrap.min.css`。
- 版本集中在 Makefile 或等价 manifest 中。
- 第三方 minified 文件尽量原样管理；不要为了通过格式化 hook 做隐式 patch。

## Pre-commit 与 vendor

第三方 `.mjs`、`.min.css` 可能包含合法尾随空白或没有 EOF newline，应避免格式化 hook 改动原始内容。

推荐忽略：

```yaml
- id: end-of-file-fixer
  exclude: \.(mjs|min\.css)$
- id: trailing-whitespace
  exclude: \.(mjs|min\.css)$
```

`git diff --check` 验证时也应排除原始 vendor：

```bash
git diff --check -- . ':!*.mjs' ':!*.min.css'
```

## 验证清单

本地静态检查：

```bash
find static -name '*.js' -o -name '*.mjs' | sort | xargs -n 1 node --check
git diff --check -- . ':!*.mjs' ':!*.min.css'
```

后端模板或 HTTP 用例应覆盖：

- 页面包含对应 custom element。
- 页面不再注入旧 route/API 全局变量。
- 页面不加载旧全局入口 `main.js`。
- 页面只加载当前 route 对应 app module。
- 静态 app module 能直接返回 200。

浏览器真实验证应覆盖：

- 页面展示真实数据，而不是空壳。
- 当前页面只存在对应 `script[type="module"][src]`。
- CSS 在 `document.styleSheets` 中实际加载。
- Lit marker 数量为 0，例如检查 `.value`、`@click`、`?checked` 等残留属性。
- 表单控件有真实值，结构化输入数量符合预期。

示例浏览器检查片段：

```js
Array.from(document.querySelectorAll('script[type="module"][src]')).map((script) =>
  script.getAttribute('src')
);

document.querySelectorAll('[\\.value], [\\@input], [\\@click], [\\?checked], [\\?disabled]').length;
```

## Review 常见问题

- 中转入口文件只做全量 import：删除中转入口，改成模板按页面加载。
- vendor 更新脚本自己 patch 第三方文件：优先移除 patch，改为 pre-commit 忽略原始 vendor。
- 只忽略某个具体 minified 文件：改成忽略所有 `.min.css`。
- 页面 200 但没有真实数据：补浏览器检查真实 DOM、表单值和 API 返回。
- 前端解析后端 route：改成后端模板选择页面 app，前端只做当前页面逻辑。
