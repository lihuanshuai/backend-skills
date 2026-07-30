---
name: lit-code-style-guide
description: 设计、实现或审查随后端发布的无构建 Lit 页面，覆盖后端模板入口、页面级模块、本地 import map、vendor 管理和浏览器验证。适用于明确不引入前端构建链路的 Lit 场景。
---

# 无构建 Lit 前端

约定 `<skill_dir>` 为当前技能目录，`<repo_dir>` 为目标项目根目录。项目本地规范和设计系统优先。

## 场景路由

- 设计或实现后端 route、模板、custom element、模块分层和 import map 时，读取 `<skill_dir>/references/no-build-lit-frontend.md`。
- 新增或更新 browser ESM、CSS vendor、下载脚本或格式化忽略时，读取 `<skill_dir>/references/vendor-management.md`。
- 验证、排障或 review 页面时，读取 `<skill_dir>/references/verification-and-review.md`。
- 端到端新增或重构同时涉及以上场景时才读取全部 reference；局部任务只读取对应文件。

## 执行

1. 读取 `<repo_dir>` 的 route、模板、静态目录、现有 JS/CSS、依赖入口和验证配置，确认它确实采用或要求无构建发布。
2. 按场景 reference 修改最小必要范围；沿用现有模板继承、URL 生成、目录命名、认证和 API 约定，不发明平行入口。
3. 静态检查变更模块，再验证后端 route、静态资源和真实浏览器渲染；自动修复或 vendor 更新后审查 diff 并复跑同一范围。
4. 汇报实际验证的 route、资源、浏览器行为及未覆盖项；局部静态检查或 HTTP 200 不得表述为页面可用。

## 门禁

- 不给已有成熟构建链路的项目强行改成无构建架构；也不为无构建项目新增 `package.json`、`node_modules` 或 bundler 发布步骤。
- 后端 route 决定模板和页面 app；不得把 route/API base 注入全局变量后交给前端重新路由，也不得用全局入口预加载全部页面。
- 业务模块使用 bare import，本地 import map 指向随应用发布的 vendor；不得依赖 CDN runtime 或在各模块散落 vendor 相对路径。
- 动态值使用 Lit 属性、布尔值和事件绑定；不得用字符串拼接或 `innerHTML` 规避绑定问题。
- 第三方 vendor 原样下载并校验，不得为格式化工具隐式 patch；版本或内容变化必须可审查。
- 浏览器中出现 `.value="lit$..."`、`@click="lit$..."`、`?checked="lit$..."` 等 marker 时，先排查 bundle、import map 和加载方式，不回退为手写 DOM。
