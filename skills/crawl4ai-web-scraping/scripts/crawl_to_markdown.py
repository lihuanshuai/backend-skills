#!/usr/bin/env python3
"""
Crawl a single URL with Crawl4AI and save the page content as a Markdown file.
Usage:
  python crawl_to_markdown.py -u "https://example.com"
  python crawl_to_markdown.py -u "https://example.com" -o page.md
  python crawl_to_markdown.py -u "https://example.com" -d ./output
"""
from __future__ import annotations

import argparse
import asyncio
import re
from pathlib import Path

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode


def slug_from_url(url: str) -> str:
    """Generate a safe filename from URL (host + path)."""
    # Remove protocol and trailing slash
    s = re.sub(r"^https?://", "", url).strip("/")
    # Replace invalid path chars
    s = re.sub(r"[^\w\-.]", "_", s)
    return s[:120] or "page"


def get_markdown_text(result) -> str:
    """Get markdown string from CrawlResult (handles both str and MarkdownGenerationResult)."""
    md = result.markdown
    if hasattr(md, "raw_markdown") and md.raw_markdown:
        return md.raw_markdown
    if isinstance(md, str):
        return md
    if hasattr(md, "fit_markdown") and md.fit_markdown:
        return md.fit_markdown
    return ""


async def crawl_to_md(url: str, out_path: Path, ignore_strikethrough: bool = False) -> None:
    config_kwargs: dict = {"cache_mode": CacheMode.BYPASS}
    if ignore_strikethrough:
        # Remove strikethrough content at HTML level by excluding common tags
        config_kwargs["excluded_tags"] = ["s", "strike", "del"]
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(**config_kwargs),
        )
        if not result.success:
            raise RuntimeError(result.error_message or f"Crawl failed (status {getattr(result, 'status_code', '?')})")
        text = get_markdown_text(result)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl URL and save as Markdown file.")
    parser.add_argument("-u", "--url", required=True, help="URL to crawl")
    parser.add_argument("-o", "--output", help="Output .md file path (overrides -d when given)")
    parser.add_argument("-d", "--output-dir", default=".", help="Output directory when -o not set (default: current dir)")
    parser.add_argument(
        "--ignore-strikethrough",
        action="store_true",
        help="Ignore strikethrough content by dropping <s>/<strike>/<del> HTML before markdown conversion",
    )
    args = parser.parse_args()

    if args.output:
        out_path = Path(args.output)
        if out_path.suffix.lower() != ".md":
            out_path = out_path.with_suffix(".md")
    else:
        out_dir = Path(args.output_dir)
        base = slug_from_url(args.url)
        out_path = out_dir / f"{base}.md"

    asyncio.run(crawl_to_md(args.url, out_path, ignore_strikethrough=args.ignore_strikethrough))
    print(out_path.resolve())


if __name__ == "__main__":
    main()
