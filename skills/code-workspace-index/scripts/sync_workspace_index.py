#!/usr/bin/env python3
"""
Build a local workspace index from a VS Code .code-workspace file
and fill project.summary from key files (README, pyproject, app.yaml, etc.).
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

try:
    import tomllib
except ImportError:
    tomllib = None  # type: ignore[assignment]


BADGE_LINE = re.compile(
    r"^\s*(\[!\[|!\[|<img\s|<p\s+align|<h1\s|<a\s+href|https?://.*badge|shields\.|cherry\.|jenkins|codecov|travis|goreportcard)",
    re.I,
)

# README：跳过「开发 / 链接列表」等噪音；优先业务向小节
FICTION_HINTS = (
    "was purchased from",
    "was gifted to harry",
    "eeylops owl",
    "rubeus hagrid",
    "wizarding world",
    "owl emporium",
)
SKIP_H2 = re.compile(
    r"^(开发|Development|测试|Testing|Grafana|前端|dev|CI|Install|安装|CHANGELOG|贡献|Contributing|Build|编译)\s*$",
    re.I,
)
PREFERRED_HEADING = (
    "项目介绍",
    "项目简介",
    "简介",
    "概述",
    "是什么",
    "管理员后台",
    "管理员",
    "docs",
    "文档",
    "功能",
    "服务",
    "目前项目",
    "说明",
    "业务",
)


def strip_jsonc_loose(raw: str) -> str:
    """Remove // line comments (best-effort; avoids full JSONC parser)."""
    out_lines: list[str] = []
    for line in raw.splitlines():
        stripped = line
        if "//" in stripped:
            in_string = False
            escape = False
            for i, ch in enumerate(stripped):
                if escape:
                    escape = False
                    continue
                if ch == "\\" and in_string:
                    escape = True
                    continue
                if ch == '"':
                    in_string = not in_string
                    continue
                if not in_string and ch == "/" and i + 1 < len(stripped) and stripped[i + 1] == "/":
                    stripped = stripped[:i].rstrip()
                    break
        out_lines.append(stripped)
    return "\n".join(out_lines)


def strip_trailing_commas(raw: str) -> str:
    """Remove trailing commas before } or ] (VS Code JSONC often allows them)."""
    prev = None
    while prev != raw:
        prev = raw
        raw = re.sub(r",(\s*[}\]])", r"\1", raw)
    return raw


def load_workspace(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    last_err: json.JSONDecodeError | None = None
    for candidate in (
        text,
        strip_jsonc_loose(text),
        strip_trailing_commas(strip_jsonc_loose(text)),
    ):
        try:
            data = json.loads(candidate)
            break
        except json.JSONDecodeError as e:
            last_err = e
    else:
        raise last_err if last_err else json.JSONDecodeError("parse failed", "", 0)
    if not isinstance(data, dict):
        raise ValueError("workspace root must be a JSON object")
    return data


def git_remotes(project_dir: Path) -> dict[str, str]:
    if not (project_dir / ".git").exists():
        return {}
    try:
        out = subprocess.run(
            ["git", "-C", str(project_dir), "remote", "-v"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}
    if out.returncode != 0 or not out.stdout:
        return {}
    fetch_urls: dict[str, str] = {}
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[1] == "(fetch)":
            name, url = parts[0], parts[2]
            fetch_urls.setdefault(name, url)
    return fetch_urls


def read_tomlish_name(pyproject: Path) -> str | None:
    try:
        text = pyproject.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r'^name\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
    if m:
        return m.group(1)
    return None


def read_package_json_name(pkg: Path) -> tuple[str | None, dict[str, Any]]:
    try:
        data = json.loads(pkg.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, {}
    if not isinstance(data, dict):
        return None, {}
    name = data.get("name")
    return (name if isinstance(name, str) else None), data


def detect_stack(root: Path) -> dict[str, Any]:
    languages: list[str] = []
    frameworks: list[str] = []
    package_name: str | None = None

    if (root / "pyproject.toml").is_file():
        languages.append("python")
        package_name = read_tomlish_name(root / "pyproject.toml")
        try:
            t = (root / "pyproject.toml").read_text(encoding="utf-8").lower()
            if "django" in t:
                frameworks.append("django")
            if "fastapi" in t:
                frameworks.append("fastapi")
            if "flask" in t:
                frameworks.append("flask")
        except OSError:
            pass
    elif (root / "setup.py").is_file() or (root / "setup.cfg").is_file():
        languages.append("python")
    elif list(root.glob("requirements*.txt")):
        languages.append("python")

    if (root / "package.json").is_file():
        if "typescript" not in languages and "javascript" not in languages:
            languages.append("javascript")
        n, pkg = read_package_json_name(root / "package.json")
        package_name = package_name or n
        deps = pkg.get("dependencies") or {}
        dev = pkg.get("devDependencies") or {}
        if isinstance(deps, dict) and isinstance(dev, dict):
            all_dep = {**dev, **deps}
            low = {k.lower(): v for k, v in all_dep.items()}
            if "react" in low:
                frameworks.append("react")
            if "next" in low:
                frameworks.append("next")
            if "vue" in low:
                frameworks.append("vue")
            if "@angular/core" in low:
                frameworks.append("angular")

    if (root / "go.mod").is_file():
        languages.append("go")
    if (root / "Cargo.toml").is_file():
        languages.append("rust")
    if (root / "Gemfile").is_file():
        languages.append("ruby")
    if (root / "pom.xml").is_file() or (root / "build.gradle").is_file() or (root / "build.gradle.kts").is_file():
        languages.append("java")

    if not languages:
        languages.append("unknown")

    seen: set[str] = set()
    languages = [x for x in languages if not (x in seen or seen.add(x))]
    return {
        "languages": languages,
        "frameworks": sorted(set(frameworks)),
        "package_name": package_name,
    }


def rel_to_base(base: Path, target: Path) -> str:
    try:
        return str(target.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(target.resolve())


def clip(text: str, n: int = 300) -> str:
    text = " ".join(text.split())
    if len(text) <= n:
        return text
    return text[: n - 1] + "…"


def from_pyproject(root: Path) -> str | None:
    if tomllib is None:
        return None
    p = root / "pyproject.toml"
    if not p.is_file():
        return None
    try:
        data = tomllib.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    proj = data.get("project")
    if isinstance(proj, dict):
        d = proj.get("description")
        if isinstance(d, str) and d.strip():
            return clip(d, 320)
    poetry = data.get("tool", {}).get("poetry")
    if isinstance(poetry, dict):
        d = poetry.get("description")
        if isinstance(d, str) and d.strip():
            return clip(d, 320)
    return None


def from_package_json(root: Path) -> str | None:
    p = root / "package.json"
    if not p.is_file():
        return None
    try:
        j = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    d = j.get("description")
    if isinstance(d, str) and d.strip():
        return clip(d, 320)
    return None


def normalize_readme_raw(raw: str) -> str:
    """Strip common HTML in README so # / ## 解析可用。"""
    if not re.search(r"(?i)<\s*h[12]\b|<\s*p\b", raw):
        return raw
    t = raw
    t = re.sub(
        r"(?is)<\s*h1[^>]*>(.*?)</\s*h1\s*>",
        lambda m: "# " + re.sub(r"<[^>]+>", " ", m.group(1)).strip() + "\n",
        t,
        count=1,
    )
    t = re.sub(
        r"(?is)<\s*h2[^>]*>(.*?)</\s*h2\s*>",
        lambda m: "## " + re.sub(r"<[^>]+>", " ", m.group(1)).strip() + "\n",
        t,
    )
    t = re.sub(r"(?i)<\s*br\s*/?>\s*", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(t)


def clean_body_text(s: str) -> str:
    s = re.sub(r"```[\s\S]*?```", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"`+", "", s)
    return " ".join(s.split()).strip()


def is_links_only_body(body: str) -> bool:
    lines = [ln.strip() for ln in body.splitlines() if ln.strip() and not ln.strip().startswith("```")]
    if not lines:
        return True
    url_lines = sum(1 for ln in lines if re.search(r"https?://", ln))
    return url_lines >= max(1, len(lines) - 1)


def is_dev_noise_body(body: str) -> bool:
    b = clean_body_text(body).lower()
    if not b:
        return True
    if "pre-commit" in b and ("pip install" in b or "推荐使用" in body or "安装方法" in body):
        return True
    if b.startswith("pip install") or "pre-commit install" in b:
        return True
    return False


def is_fiction_noise(body: str) -> bool:
    b = clean_body_text(body).lower()
    return any(h in b for h in FICTION_HINTS)


def preamble_substance(preamble: str) -> str:
    lines: list[str] = []
    for line in preamble.splitlines():
        ls = line.strip()
        if not ls or BADGE_LINE.search(ls) or ls.startswith("[!["):
            continue
        lines.append(ls)
    return "\n".join(lines)


def parse_h1_preamble_h2(text: str) -> tuple[str, str, list[tuple[str, str]]]:
    lines = text.splitlines()
    title = ""
    preamble: list[str] = []
    h2_list: list[tuple[str, list[str]]] = []
    state = "find_h1"
    cur_h2: str | None = None
    cur_body: list[str] = []
    for line in lines:
        if state == "find_h1":
            m = re.match(r"^#\s+(.+)$", line)
            if m:
                title = m.group(1).strip()
                state = "preamble"
            continue
        if state == "preamble":
            m2 = re.match(r"^##\s+(.+)$", line)
            if m2:
                cur_h2 = m2.group(1).strip()
                cur_body = []
                state = "in_h2"
            elif line.strip():
                preamble.append(line)
            continue
        if state == "in_h2":
            m2 = re.match(r"^##\s+(.+)$", line)
            if m2:
                if cur_h2 is not None:
                    h2_list.append((cur_h2, "\n".join(cur_body)))
                cur_h2 = m2.group(1).strip()
                cur_body = []
            else:
                cur_body.append(line)
    if state == "in_h2" and cur_h2 is not None:
        h2_list.append((cur_h2, "\n".join(cur_body)))
    return title, "\n".join(preamble).strip(), h2_list


def heading_priority(h: str) -> tuple[int, int]:
    hlow = h.lower()
    for i, pref in enumerate(PREFERRED_HEADING):
        if pref.lower() in hlow:
            return (0, i)
    return (1, 0)


def pick_readme_summary(raw_text: str) -> str | None:
    text = normalize_readme_raw(raw_text)
    for kw in ("项目介绍", "项目简介", "简介", "Introduction", "概述", "关于本项目", "About"):
        pat = re.compile(
            rf"(?m)^#{{1,3}}\s*{re.escape(kw)}[^\n]*\n+([\s\S]+?)(?=^#{{1,3}}\s|\Z)",
        )
        m = pat.search(text)
        if m:
            chunk = m.group(1)
            body = clean_body_text(chunk)
            if len(body) > 12 and not is_dev_noise_body(chunk) and not is_fiction_noise(chunk):
                return clip(body, 300)

    title, preamble, h2s = parse_h1_preamble_h2(text)
    order = sorted(range(len(h2s)), key=lambda i: (heading_priority(h2s[i][0]), i))
    for idx in order:
        h, body = h2s[idx]
        if SKIP_H2.match(h.strip()):
            continue
        if re.match(r"(?i)^links?$", h.strip()) and is_links_only_body(body):
            continue
        if is_dev_noise_body(body) or is_fiction_noise(body):
            continue
        cleaned = clean_body_text(body)
        if len(cleaned) < 12:
            continue
        return clip(cleaned, 300)

    pre_raw = preamble_substance(preamble)
    pre = clean_body_text(pre_raw)
    if len(pre) > 15 and not is_fiction_noise(pre_raw) and not is_dev_noise_body(pre_raw):
        if re.search(r"[\u4e00-\u9fff]", pre) or len(pre) > 55:
            return clip(pre, 300)

    if title and len(title.strip()) >= 2:
        t = clean_body_text(title)
        if t:
            return clip(t, 160)

    return None


def from_readme_md(root: Path) -> str | None:
    for name in ("README.md", "readme.md"):
        p = root / name
        if not p.is_file():
            continue
        raw = p.read_text(encoding="utf-8", errors="ignore")
        got = pick_readme_summary(raw)
        if got:
            return got
        nonempty = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        if len(nonempty) == 1 and nonempty[0].startswith("#"):
            title = re.sub(r"^#+\s*", "", nonempty[0]).strip()
            if title:
                return clip(f"仓库 README 仅有标题「{title}」；请结合目录内文件理解用途。", 280)
    return None


def from_readme_rst(root: Path) -> str | None:
    p = root / "README.rst"
    if not p.is_file():
        return None
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    buf: list[str] = []
    for line in lines:
        ls = line.strip()
        if not ls or ls.startswith(".. ") or ls.startswith("==="):
            if buf:
                break
            continue
        buf.append(ls)
        if len(" ".join(buf)) > 200:
            break
    raw = " ".join(buf)
    if len(raw.strip()) > 15:
        return clip(raw, 300)
    return None


def from_skill_md(root: Path) -> str | None:
    p = root / "SKILL.md"
    if not p.is_file():
        return None
    text = p.read_text(encoding="utf-8", errors="ignore")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = parts[1]
    m = re.search(r"(?m)^description:\s*(.+)$", fm)
    if not m:
        return None
    desc = m.group(1).strip()
    if (desc.startswith('"') and desc.endswith('"')) or (desc.startswith("'") and desc.endswith("'")):
        desc = desc[1:-1]
    if len(desc) > 8:
        return clip(desc, 320)
    return None


def from_docs_index(root: Path) -> str | None:
    for cand in (root / "docs" / "index.md", root / "docs" / "README.md"):
        if not cand.is_file():
            continue
        t = cand.read_text(encoding="utf-8", errors="ignore")
        t = re.sub(r"^#+\s+[^\n]+\n", "", t, count=1)
        t = re.sub(r"```[\s\S]*?```", " ", t)
        t = " ".join(t.split())
        if len(t) > 20:
            return clip(t, 300)
    return None


def from_app_yaml(root: Path) -> str | None:
    p = root / "app.yaml"
    if not p.is_file():
        return None
    text = p.read_text(encoding="utf-8", errors="ignore")
    app_m = re.search(r"(?m)^application:\s*(\S+)", text)
    if not app_m:
        return None
    app = app_m.group(1).strip()
    rt_m = re.search(r"(?m)^runtime:\s*(\S+)", text)
    runtime = rt_m.group(1).strip() if rt_m else ""
    rv_m = re.search(r"(?m)^runtime_version:\s*[\"']?([^\"'\n]+)[\"']?", text)
    ver = rv_m.group(1).strip() if rv_m else ""
    bits = [f"DAE 应用「{app}」"]
    if runtime:
        bits.append(runtime)
    if ver:
        bits.append(ver)
    bits.append("；职责与路由见 app.yaml。")
    return clip("".join(bits), 300)


def summarize_root(root: Path) -> str:
    if not root.exists():
        return (
            "路径当前不可访问（未检出或本机无此目录）；请在检出后重新运行本脚本或手写简介。"
            "若 workspace 另有同名可访问目录，以可访问路径为准。"
        )
    if not root.is_dir():
        return "路径非目录，简介待确认。"
    for fn in (
        from_pyproject,
        from_package_json,
        from_readme_md,
        from_readme_rst,
        from_docs_index,
        from_skill_md,
        from_app_yaml,
    ):
        s = fn(root)
        if s:
            return s
    return (
        f"工作区子目录「{root.name}」，未见 README/pyproject/package.json/SKILL.md 等可抽取说明，"
        "请打开仓库确认职责。"
    )


def fill_summaries(index: dict[str, Any]) -> int:
    """Mutate index['projects'][*]['project']['summary']. Returns count of empty summaries."""
    for proj in index["projects"]:
        proj["project"]["summary"] = summarize_root(Path(proj["path_resolved"]))
    return sum(1 for p in index["projects"] if not str(p["project"].get("summary", "")).strip())


def write_index(index: dict[str, Any], out_path: Path, as_yaml: bool) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if as_yaml:
        if yaml is None:
            print("error: PyYAML is required for yaml output. pip install -r scripts/requirements.txt", flush=True)
            sys.exit(1)
        out_path.write_text(
            yaml.dump(index, allow_unicode=True, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
    else:
        out_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync workspace index from .code-workspace and fill project summaries.",
    )
    parser.add_argument(
        "workspace",
        type=Path,
        help="Path to the .code-workspace file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output index file (default under skill_dir: workspace-index.local.yaml or .json)",
    )
    parser.add_argument(
        "--format",
        choices=("yaml", "json"),
        default="yaml",
        help="Output format when extension is ambiguous (default yaml)",
    )
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent

    workspace_file = args.workspace.expanduser().resolve()
    if not workspace_file.is_file():
        print(f"error: workspace file not found: {workspace_file}", flush=True)
        return 2

    if args.output is None:
        if args.format == "json":
            out_path = skill_dir / "workspace-index.local.json"
        else:
            out_path = skill_dir / "workspace-index.local.yaml"
    else:
        out_path = args.output.expanduser().resolve()

    data = load_workspace(workspace_file)
    folders = data.get("folders") or []
    if not isinstance(folders, list):
        print("error: 'folders' must be a list", flush=True)
        return 2

    base_dir = workspace_file.parent
    projects: list[dict[str, Any]] = []

    for item in folders:
        if not isinstance(item, dict):
            continue
        raw_path = item.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            continue
        folder_name = item.get("name")
        folder_name = folder_name if isinstance(folder_name, str) else None

        path_obj = Path(raw_path)
        if path_obj.is_absolute():
            resolved = path_obj.resolve()
        else:
            resolved = (base_dir / raw_path).resolve()

        rel = rel_to_base(base_dir, resolved)
        display_name = folder_name or resolved.name

        remotes = git_remotes(resolved)
        stack = detect_stack(resolved)

        remote_roles = ""
        if "upstream" in remotes and "origin" in remotes:
            remote_roles = "存在 upstream 与 origin：通常 upstream 为上游只读参考，origin 为个人 fork 或主推送远程。"
        elif "origin" in remotes:
            remote_roles = "仅有 origin：一般为默认远程。"

        projects.append(
            {
                "name": display_name,
                "path_relative": rel,
                "path_resolved": str(resolved),
                "git": {
                    "is_repo": bool(remotes),
                    "remotes": remotes,
                    "remote_notes": remote_roles,
                },
                "project": {
                    "languages": stack["languages"],
                    "frameworks": stack["frameworks"],
                    "package_name": stack["package_name"],
                    "summary": "",
                },
            }
        )

    index: dict[str, Any] = {
        "meta": {
            "synced_at": datetime.now(timezone.utc).isoformat(),
            "workspace_file": str(workspace_file),
            "workspace_base": str(base_dir.resolve()),
            "folder_count": len(projects),
        },
        "agent_hints": {
            "matching": "本脚本按 README/pyproject/app.yaml/SKILL 等启发式填充 project.summary；不准处由 Agent 读 path_resolved 后改索引。关键词匹配可结合 summary、name、languages、frameworks、path_relative。跨仓改动优先列出同 workspace 内相关语言/框架项目。",
            "git": "若 remotes 同时含 upstream 与 origin，PR 目标多为 upstream；本地推送多为 origin。",
            "summary_quality": "每条 projects[].project.summary 建议为非空；若启发式仍空或不准，Agent 须补全或润色后再作语义检索。",
        },
        "projects": projects,
    }

    empty = fill_summaries(index)

    suf = out_path.suffix.lower()
    if suf in (".yaml", ".yml"):
        as_yaml = True
    elif suf == ".json":
        as_yaml = False
    else:
        as_yaml = args.format == "yaml"
    write_index(index, out_path, as_yaml)

    print(f"wrote {out_path} projects={len(projects)} empty_summary={empty}", flush=True)
    return 0 if empty == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
