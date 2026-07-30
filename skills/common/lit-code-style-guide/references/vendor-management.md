# Lit Vendor 管理

## 更新契约

- 用 Makefile 或等价脚本集中声明版本、下载 URL、目标路径和超时；版本值是项目选择，不照抄示例快照。
- 同一入口覆盖 browser ESM 与 CSS vendor，只下载和校验静态文件，不安装 npm 依赖、不生成 `node_modules`、不 bundle。
- 下载到临时目录并与 tracked 文件比较；更新命令再写入目标路径，避免校验动作修改工作区。
- 保留上游文件原始内容，不为 lint、EOF newline 或尾随空白做隐式 patch；版本和文件内容变化必须同时出现在可审查 diff 中。
- 项目已有 checksum、lock manifest 或内部镜像时沿用，不另建平行真源。网络受阻时报告环境问题，不手工伪造 vendor 内容。

参考结构：

```makefile
STATIC_DIR := static/app
VENDOR_DIR := $(STATIC_DIR)/vendor
LIT_VERSION := <project-version>
LIT_URL := https://esm.sh/lit@$(LIT_VERSION)/es2022/lit.bundle.mjs
CURL := curl -fsSL --retry 3 --connect-timeout 10 --max-time 120

.PHONY: vendor-update vendor-check

vendor-update:
	@mkdir -p "$(VENDOR_DIR)"
	$(CURL) "$(LIT_URL)" -o "$(VENDOR_DIR)/lit.bundle.mjs"

vendor-check:
	@tmp=$$(mktemp -d); \
	trap 'rm -rf "$$tmp"' EXIT; \
	$(CURL) "$(LIT_URL)" -o "$$tmp/lit.bundle.mjs"; \
	cmp -s "$$tmp/lit.bundle.mjs" "$(VENDOR_DIR)/lit.bundle.mjs"
```

## 格式化边界

第三方 `.mjs`、`.min.css` 可能合法地缺少 EOF newline 或包含尾随空白。只对确认属于原始 vendor 的路径设置项目现有 hook 的排除规则，例如：

```yaml
- id: end-of-file-fixer
  exclude: \.(mjs|min\.css)$
- id: trailing-whitespace
  exclude: \.(mjs|min\.css)$
```

排除原始 vendor 后仍检查其余 diff：

```bash
git diff --check -- . ':!*.mjs' ':!*.min.css'
```

不得用宽泛 exclude 掩盖业务 JS/CSS 问题；如果 `.mjs` 同时包含自有代码，应按目录区分，而不是按扩展名全部排除。
