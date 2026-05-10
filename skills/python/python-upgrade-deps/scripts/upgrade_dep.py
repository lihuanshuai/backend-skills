#!/usr/bin/env python3
"""
Upgrade a Python dependency in pip-req.txt, requirements.txt, or pyproject.toml.
Usage: python upgrade_dep.py <project_dir> <package_name> [target_version]
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path


VERSION_SPECIFIERS = ["===", "!=", ">=", "<=", "==", "~=", ">", "<"]


def fetch_latest_version(package_name: str) -> str:
    """Fetch latest version from PyPI. Uses base package name (no extras)."""
    base_name = package_name.split("[")[0].strip()
    url = f"https://pypi.org/pypi/{base_name}/json"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return data["info"]["version"]
    except Exception as e:
        raise SystemExit(f"Failed to fetch version from PyPI: {e}") from e


def normalize_package_name(name: str) -> str:
    """Extract base package name for comparison (lowercase, no extras)."""
    return name.split("[")[0].strip().lower()


def parse_req_line(line: str) -> tuple[str | None, str]:
    """
    Parse a requirements line. Returns (package_base_name, package_part) if it's a
    package line with version specifier, else (None, "").
    package_part is the package name with extras, e.g. "ArticleCommonLib" or "pkg[extra]".
    """
    line_stripped = line.strip()
    if not line_stripped or line_stripped.startswith("#") or line_stripped.startswith("-"):
        return (None, "")

    # Split off inline comment
    main_part = line_stripped
    if " #" in line_stripped:
        idx = line_stripped.index(" #")
        main_part = line_stripped[:idx].strip()
    if " ;" in main_part:
        idx = main_part.index(" ;")
        main_part = main_part[:idx].strip()

    # Find version specifier (prefer longer matches first)
    specifier = None
    spec_pos = -1
    for spec in VERSION_SPECIFIERS:
        pos = main_part.find(spec)
        if pos >= 0 and (spec_pos < 0 or pos < spec_pos):
            spec_pos = pos
            specifier = spec

    if specifier is None or spec_pos < 0:
        return (None, "")

    package_part = main_part[:spec_pos].strip()
    pkg_base = normalize_package_name(package_part)
    return (pkg_base, package_part)


def upgrade_req_line(line: str, package_name: str, new_version: str, spec: str = "~=") -> str:
    """Upgrade a single requirements line if it matches package_name."""
    pkg_base, package_part = parse_req_line(line)
    if pkg_base is None or pkg_base != normalize_package_name(package_name):
        return line

    # Preserve leading whitespace and trailing comment
    leading = line[: len(line) - len(line.lstrip())]
    rest = ""
    if " #" in line:
        idx = line.index(" #")
        rest = line[idx:]
        if not rest.endswith("\n"):
            rest += "\n"
    else:
        rest = "\n"

    new_line = f"{leading}{package_part}{spec}{new_version}{rest}"
    if not new_line.endswith("\n"):
        new_line += "\n"
    return new_line


def upgrade_req_file(path: Path, package_name: str, new_version: str, spec: str = "~=") -> bool:
    """Upgrade package in a requirements-style file. Returns True if changed."""
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    new_lines = []
    changed = False
    for line in lines:
        new_line = upgrade_req_line(line, package_name, new_version, spec)
        if new_line != line:
            changed = True
        new_lines.append(new_line)

    if changed:
        path.write_text("".join(new_lines), encoding="utf-8")
    return changed


def upgrade_pyproject(path: Path, package_name: str, new_version: str, spec: str = "~=") -> bool:
    """Upgrade package in pyproject.toml dependencies. Returns True if changed."""
    content = path.read_text(encoding="utf-8")
    pkg_lower = normalize_package_name(package_name)
    spec_pattern = "|".join(re.escape(s) for s in VERSION_SPECIFIERS)

    # Match: "package~=1.2.3" - full quoted dependency string
    pattern = re.compile(
        r'"([^"]*?)(' + spec_pattern + r')([\d.]+[^"]*)"',
        re.IGNORECASE,
    )

    def repl(m: re.Match) -> str:
        pkg_part = m.group(1)
        if normalize_package_name(pkg_part) != pkg_lower:
            return m.group(0)
        return f'"{pkg_part}{spec}{new_version}"'

    new_content = pattern.sub(repl, content)
    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
        return True
    return False


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python upgrade_dep.py <project_dir> <package_name> [target_version]")
        sys.exit(1)

    proj_dir = Path(sys.argv[1]).resolve()
    package_name = sys.argv[2]
    target_version = sys.argv[3] if len(sys.argv) > 3 else None

    if not proj_dir.is_dir():
        print(f"Not a directory: {proj_dir}", file=sys.stderr)
        sys.exit(1)

    if target_version is None:
        target_version = fetch_latest_version(package_name)
        print(f"Latest version from PyPI: {target_version}")

    updated = []
    for name in ("pip-req.txt", "requirements.txt"):
        p = proj_dir / name
        if p.exists() and upgrade_req_file(p, package_name, target_version):
            updated.append(name)

    pyproject = proj_dir / "pyproject.toml"
    if pyproject.exists() and upgrade_pyproject(pyproject, package_name, target_version):
        updated.append("pyproject.toml")

    if updated:
        print(f"Updated {', '.join(updated)}: {package_name} -> {target_version}")
    else:
        print(f"Package {package_name} not found or no changes needed", file=sys.stderr)
        sys.exit(1)
