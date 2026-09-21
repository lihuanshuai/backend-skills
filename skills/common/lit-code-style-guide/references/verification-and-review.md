# Lit 页面验证与 Review

## 按变更选择验证

执行仓库必跑项，并按以下范围选择检查；不为局部改动重复整套验证。

- 自有 JS / MJS 变化：运行项目适用的 lint、format 或语法检查；原始 vendor 按项目排除规则处理。
- route、模板或页面参数变化：运行相关后端模板或 HTTP 用例，检查模板选择、参数转义与资源入口；涉及页面输出时在真实浏览器验证受影响页面。
- 组件或交互变化：在真实浏览器验证受影响组件的数据、控件状态和关键交互。
- 样式变化：在真实浏览器确认目标样式加载及受影响页面的显示效果，不重复无关的路由或交互检查。
- import map、vendor 或共享加载顺序变化：检查模块和资源加载，并在真实浏览器重新验证所有受影响页面，不能只验证共享模板中的一个 route。
- 仅文档变化：核对说明与实际入口、命令的一致性，无需仅为文字修改启动页面。

以下清单按变更选择相关项；HTTP 200 或源码断言不能代替页面渲染验证。验证后有新改动时重跑受影响检查，否则仅在失败或未解决风险需要时追加验证。

后端/HTTP 检查项：

- 页面包含目标 custom element，且参数值正确转义。
- 页面不注入已废弃的 route/API 全局变量，不加载旧全局入口。
- 页面只加载当前 route 对应的 app module，模块和 CSS URL 可访问。

浏览器检查项：

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
