# Lit 页面验证与 Review

## 验证顺序

1. 对变更的自有 `.js` / `.mjs` 运行项目既有 lint、format 和语法检查；原始 vendor 按项目排除规则处理。
2. 运行后端模板或 HTTP 用例，确认 route 返回正确模板，custom element、模块 URL 和静态资源可访问。
3. 在匹配目标环境的真实浏览器打开页面，检查数据、模块、样式和交互；HTTP 200 或源码断言不能代替渲染验证。
4. 修改 import map、vendor 或加载顺序后重新验证所有受影响页面，而非只验证共享模板中的一个 route。

后端/HTTP 检查至少覆盖：

- 页面包含目标 custom element，且参数值正确转义。
- 页面不注入已废弃的 route/API 全局变量，不加载旧全局入口。
- 页面只加载当前 route 对应的 app module，模块和 CSS URL 可访问。

浏览器检查至少覆盖：

- 页面展示真实数据，表单控件具有预期值，关键交互能改变可观察状态。
- `script[type="module"][src]` 只有当前页面所需入口，网络面板无模块、import map 或 CSS 加载错误。
- 目标 CSS 出现在 `document.styleSheets`，不能只依据 `<link>` 元素存在。
- Lit marker 数量为 0；若不为 0，先检查 bundle 格式、Lit 实例、import map 和脚本加载方式。

```js
Array.from(document.querySelectorAll('script[type="module"][src]')).map((script) =>
  script.getAttribute('src')
);

document.querySelectorAll(
  '[\\.value], [\\@input], [\\@click], [\\?checked], [\\?disabled]',
).length;
```

## Review 重点

- 前端根据注入的 route 再选页面：改由后端 route 选择模板和 app。
- `main.js` 或聚合模块无条件 import 全部页面：改为模板按页面加载。
- 动态值使用字符串、`innerHTML` 或错误 attribute 绑定：改为 Lit 对应绑定，并检查数据转义。
- vendor 更新脚本 patch 第三方文件：保留原始文件，用窄范围 hook 排除解决格式化冲突。
- 只证明页面或资源返回 200：补真实数据、样式加载、marker 和关键交互验证。
