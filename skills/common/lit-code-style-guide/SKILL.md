---
name: lit-code-style-guide
description: Lit 前端代码风格与无构建发布规范，适用于用 Lit 重构页面、设计后端模板入口、管理本地 import map、维护 browser ESM 与 CSS vendor 文件、避免前端路由和构建流程的场景。
---

# Lit 代码风格规范

跨仓库通用基线；若项目已有更严格的前端规范或设计系统，以项目本地规范优先。

## 路径约定

`<skill_dir>` 表示本 skill 目录（本 `SKILL.md` 所在目录）。下文路径均相对该目录。

## 何时使用

- 用户要求用 Lit 重构或新增前端页面
- 用户强调不能引入构建流程，静态资源要随后端发布
- 需要以后端模板作为页面入口，而不是由前端解析路由
- 需要用本地 import map 管理 browser ESM 依赖
- 需要整理 Lit 组件拆分、vendor 更新、pre-commit 忽略和验证方式

## 快速原则

- **无构建优先**：不要新增 `package.json`、`node_modules`、Vite、Rollup、Webpack 等发布前构建流程。
- **后端模板定页面**：每个后端 route 使用明确模板，模板直接渲染当前页面 custom element。
- **按页面加载模块**：不要用全局入口预加载全部 app；模板只加载当前页面需要的 app module。
- **本地 import map**：业务代码使用 bare import，import map 指向随应用发布的本地静态 vendor 文件。
- **组件分层**：页面 app、可复用 component、无 UI lib 分开，不把所有组件写在一个文件里。
- **Lit 正常绑定**：优先使用 `html``...`` ` 和 `css``...`` `；属性、布尔值和事件使用 Lit 绑定语法。
- **原样管理 vendor**：第三方 `.mjs`、`.min.css` 尽量原样下载和校验，不让格式化 hook 隐式修改。
- **真实页面验证**：不要只看 200 或源码，要用浏览器确认真实数据、模块加载、CSS 加载和 Lit marker。

## 细则参考

主文档只保留决策入口。需要落地代码、README 或 review 时，读取：

| 主题 | 文件 |
| --- | --- |
| 无构建 Lit 页面架构、import map、vendor、pre-commit、验证清单 | `<skill_dir>/references/no-build-lit-frontend.md` |

## 执行流程

1. 先确认发布约束：是否允许构建流程、是否必须随后端模板和静态资源发布。
2. 梳理后端 route 与页面模板，一页一个 app module，不把 route 传给前端再解析。
3. 设计 JS 分层：`apps/` 承载页面，`components/` 承载复用 UI，`lib/` 承载通用逻辑。
4. 用本地 import map 管理 ESM 依赖；CSS vendor 也纳入同一套更新工具。
5. 配置 vendor 文件的格式化忽略，避免 hook 改坏第三方 minified 文件。
6. 用静态检查、Bruno 或 HTTP 用例、浏览器真实渲染共同验证。

## 注意事项

- 如果现有项目已经有成熟前端构建链路，本技能只作为「无构建约束」场景参考，不强行替换。
- 如果浏览器 DOM 中出现 `.value="lit$..."`、`@click="lit$..."` 或 `?checked="lit$..."`，优先排查 Lit bundle 与加载方式，而不是改回手写 DOM。
- 若修改技能规则或示例，应同步更新 `<skill_dir>/references/no-build-lit-frontend.md`，避免入口和细则不一致。
