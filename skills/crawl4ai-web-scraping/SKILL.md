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

## 简化指令：用脚本

优先使用本 skill 下的脚本，一条命令完成「爬取 → 写 Markdown 文件」。在 skill 根目录（`crawl4ai-web-scraping/`）下执行：

```bash
pip install -r scripts/requirements.txt   # 首次需安装依赖
# 单 URL，输出到当前目录（文件名由 URL 生成）
python scripts/crawl_to_markdown.py -u "https://example.com"

# 忽略删除线内容（在 HTML 层面丢弃 <s>/<strike>/<del> 再转 Markdown）
python scripts/crawl_to_markdown.py -u "https://example.com" --ignore-strikethrough

# 指定输出文件
python scripts/crawl_to_markdown.py -u "https://example.com" -o page.md

# 指定输出目录，文件名自动
python scripts/crawl_to_markdown.py -u "https://example.com" -d ./output
```

Agent 在用户要求「把某网页爬成 Markdown」「把这个链接导出成 md」时，应优先建议或直接使用上述命令；若需改行为再改脚本或看下方代码说明。

## 脚本说明

| 脚本 | 作用 |
|------|------|
| `scripts/crawl_to_markdown.py` | 单 URL 爬取，结果写入一个 .md 文件；支持 `-u` URL、`-o` 输出文件、`-d` 输出目录，`--ignore-strikethrough` 在 HTML 层忽略删除线内容 |

依赖：`crawl4ai`。无额外 env 或 API key。

## 代码要点（仅当不用脚本时）

仅使用 Crawl4AI，输出到 Markdown 文件：

```python
import asyncio
from pathlib import Path
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def crawl_to_md(url: str, out_path: str) -> None:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS))
        if not result.success:
            raise RuntimeError(result.error_message or "Crawl failed")
        md = result.markdown.raw_markdown or result.markdown
        Path(out_path).write_text(md, encoding="utf-8")

# 使用
asyncio.run(crawl_to_md("https://example.com", "page.md"))
```

- 只依赖 Crawl4AI，不混用 Playwright。
- 输出内容用 `result.markdown.raw_markdown` 或 `result.markdown`，写入指定 `.md` 路径。

## 参考

- [Crawl4AI 文档](https://docs.crawl4ai.com/)
- [Quick Start](https://docs.crawl4ai.com/core/quickstart/)
