#!/usr/bin/env python3
"""
Bump Python package version in setup.py, setup.cfg, or pyproject.toml.
Usage: python bump_version.py <project_dir> [patch|minor|major]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse x.y.z into (x, y, z). Handles x.y as x.y.0."""
    parts = version_str.strip().split(".")
    x = int(parts[0]) if len(parts) > 0 else 0
    y = int(parts[1]) if len(parts) > 1 else 0
    z = int(parts[2]) if len(parts) > 2 else 0
    return (x, y, z)


def bump_version(version_str: str, bump_type: str) -> str:
    """Bump version string. bump_type: patch, minor, major."""
    x, y, z = parse_version(version_str)
    if bump_type == "patch":
        z += 1
    elif bump_type == "minor":
        y += 1
        z = 0
    elif bump_type == "major":
        x += 1
        y = 0
        z = 0
    else:
        raise ValueError(f"Unknown bump_type: {bump_type}")
    return f"{x}.{y}.{z}"


# Regex for version in different configs
PYPROJECT_PATTERN = re.compile(
    r'^(\s*version\s*=\s*["\'])(\d+(?:\.\d+)*)(["\'])\s*$', re.MULTILINE
)
SETUP_CFG_PATTERN = re.compile(
    r'^(\s*version\s*=\s*)(\d+(?:\.\d+)*)\s*$', re.MULTILINE
)
SETUP_PY_VERSION_ASSIGN = re.compile(
    r"^(\s*version\s*=\s*)([\"'])(\d+(?:\.\d+)*)([\"'])\s*$", re.MULTILINE
)
SETUP_PY_SETUP_KW = re.compile(
    r"(\bversion\s*=\s*)([\"'])(\d+(?:\.\d+)*)([\"'])\s*"
)


def bump_pyproject(content: str, new_version: str) -> str:
    def repl(m):
        return f"{m.group(1)}{new_version}{m.group(3)}"

    return PYPROJECT_PATTERN.sub(repl, content)


def bump_setup_cfg(content: str, new_version: str) -> str:
    def repl(m):
        return f"{m.group(1)}{new_version}"

    return SETUP_CFG_PATTERN.sub(repl, content)


def bump_setup_py(content: str, new_version: str) -> str:
    # First handle version = 'x.y.z' assignment
    content = SETUP_PY_VERSION_ASSIGN.sub(
        lambda m: f"{m.group(1)}{m.group(2)}{new_version}{m.group(4)}",
        content,
    )
    # Then handle setup(..., version='x.y.z', ...)
    content = SETUP_PY_SETUP_KW.sub(
        lambda m: f"{m.group(1)}{m.group(2)}{new_version}{m.group(4)}",
        content,
    )
    return content


def detect_and_bump(proj_dir: Path, bump_type: str) -> bool:
    """Detect config file, bump version, write back. Returns True if updated."""
    pyproject = proj_dir / "pyproject.toml"
    setup_cfg = proj_dir / "setup.cfg"
    setup_py = proj_dir / "setup.py"

    # Try each file in priority order; only use if it contains a valid version
    candidates: list[tuple[Path, str, callable]] = []

    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        if "[project]" in content and PYPROJECT_PATTERN.search(content):
            candidates.append((pyproject, content, bump_pyproject))

    if setup_cfg.exists():
        content = setup_cfg.read_text(encoding="utf-8")
        if "[metadata]" in content and SETUP_CFG_PATTERN.search(content):
            candidates.append((setup_cfg, content, bump_setup_cfg))

    if setup_py.exists():
        content = setup_py.read_text(encoding="utf-8")
        if SETUP_PY_VERSION_ASSIGN.search(content) or SETUP_PY_SETUP_KW.search(content):
            candidates.append((setup_py, content, bump_setup_py))

    if not candidates:
        print("No setup.py, setup.cfg, or pyproject.toml with version found", file=sys.stderr)
        return False

    target_file, content, bump_fn = candidates[0]

    # Extract current version
    if target_file == pyproject:
        m = PYPROJECT_PATTERN.search(content)
        old_ver = m.group(2) if m else None
    elif target_file == setup_cfg:
        m = SETUP_CFG_PATTERN.search(content)
        old_ver = m.group(2) if m else None
    else:
        m = SETUP_PY_VERSION_ASSIGN.search(content) or SETUP_PY_SETUP_KW.search(content)
        old_ver = m.group(3) if m else None

    if not old_ver:
        print(f"Could not find version in {target_file}", file=sys.stderr)
        return False

    new_version = bump_version(old_ver, bump_type)
    new_content = bump_fn(content, new_version)

    if new_content == content:
        print("No change (version pattern not matched)", file=sys.stderr)
        return False

    target_file.write_text(new_content, encoding="utf-8")
    print(f"Updated {target_file.name}: {old_ver} -> {new_version}")
    return True


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python bump_version.py <project_dir> [patch|minor|major]")
        sys.exit(1)

    proj_dir = Path(sys.argv[1]).resolve()
    bump_type = sys.argv[2] if len(sys.argv) > 2 else "patch"

    if not proj_dir.is_dir():
        print(f"Not a directory: {proj_dir}", file=sys.stderr)
        sys.exit(1)

    if bump_type not in ("patch", "minor", "major"):
        print("bump_type must be patch, minor, or major", file=sys.stderr)
        sys.exit(1)

    ok = detect_and_bump(proj_dir, bump_type)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
