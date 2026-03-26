---
name: crawl4ai-web-scraping
description: Use Crawl4AI to crawl web pages and save content as Markdown files. Use when the user wants to scrape a URL to Markdown, extract page content to .md, or batch crawl URLs to markdown. Applies to Crawl4AI, crawl4ai, web scraping, or URL to markdown.
---

# Crawl4AI → Markdown

Use **Crawl4AI only** to fetch a page and write its content to a Markdown file. No Playwright, no structured extraction—just URL in, Markdown file out.

## 安装

```bash
pip install -U crawl4ai
```

Python >= 3.10。

## 路径约定

本文中的 `<skill_dir>` 表示“当前 skill 目录”（即本 `SKILL.md` 所在目录）。后续路径均基于该约定展开，例如 `<skill_dir>/scripts/crawl_to_markdown.py`、`<skill_dir>/scripts/requirements.txt`。

## 简化指令：用脚本

优先使用本 skill 下的脚本，一条命令完成「爬取 → 写 Markdown 文件」：

```bash
pip install -r <skill_dir>/scripts/requirements.txt   # 首次需安装依赖
# 单 URL，输出到当前目录（文件名由 URL 生成）
python <skill_dir>/scripts/crawl_to_markdown.py -u "https://example.com"

# 忽略删除线内容（在 HTML 层面丢弃 <s>/<strike>/<del> 再转 Markdown）
python <skill_dir>/scripts/crawl_to_markdown.py -u "https://example.com" --ignore-strikethrough

# 指定输出文件
python <skill_dir>/scripts/crawl_to_markdown.py -u "https://example.com" -o page.md

# 指定输出目录，文件名自动
python <skill_dir>/scripts/crawl_to_markdown.py -u "https://example.com" -d ./output
```

标准配置：非 headless（显示浏览器）+ 持久化 user-data（`~/.crawl4ai_profile`），cookies/session 自动复用。

**需登录页面**：先用浏览器打开目标 URL，通过 `wait_for` 等待当前页面 URL 与目标一致后再提取内容。若被重定向到登录页，用户完成登录后页面跳转，脚本会自动继续并保存正确内容。

Agent 在用户要求「把某网页爬成 Markdown」「把这个链接导出成 md」时，应优先建议或直接使用上述命令；若需改行为再改脚本或看下方代码说明。

## 脚本说明

| 脚本 | 作用 |
|------|------|
| `<skill_dir>/scripts/crawl_to_markdown.py` | 单 URL 爬取，结果写入一个 .md 文件；支持 `-u` URL、`-o` 输出文件、`-d` 输出目录，`--ignore-strikethrough` 在 HTML 层忽略删除线内容；默认非 headless + 持久化 profile；打开后等待页面跳转到目标 URL 再提取，适用于需登录页面 |

依赖：`crawl4ai`。无额外 env 或 API key。

## 代码要点（仅当不用脚本时）

仅使用 Crawl4AI，输出到 Markdown 文件。标准配置：非 headless + 持久化 user-data。

```python
import asyncio
from pathlib import Path
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

USER_DATA_DIR = Path.home() / ".crawl4ai_profile"

async def crawl_to_md(url: str, out_path: str) -> None:
    browser_cfg = BrowserConfig(
        headless=False,
        user_data_dir=str(USER_DATA_DIR),
        use_persistent_context=True,
    )
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url=url, config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS))
        if not result.success:
            raise RuntimeError(result.error_message or "Crawl failed")
        md = result.markdown.raw_markdown or result.markdown
        Path(out_path).write_text(md, encoding="utf-8")

asyncio.run(crawl_to_md("https://example.com", "page.md"))
```

- 只依赖 Crawl4AI，不混用 Playwright。
- 输出内容用 `result.markdown.raw_markdown` 或 `result.markdown`，写入指定 `.md` 路径。
- 默认非 headless + `~/.crawl4ai_profile` 持久化，cookies/session 自动复用。
- 使用 `wait_for` 等待当前 URL 与目标一致后再提取，需登录时用户登录并跳转后自动继续。

## 参考

- [Crawl4AI 文档](https://docs.crawl4ai.com/)
- [Quick Start](https://docs.crawl4ai.com/core/quickstart/)
