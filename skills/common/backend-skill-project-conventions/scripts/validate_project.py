#!/usr/bin/env python3
"""Validate deterministic backend-skills project conventions."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Sequence, Set, Tuple


SKILL_PATH_RE = re.compile(r"skills/(?:common|python)/([a-z0-9-]+)/")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESOURCE_RE = re.compile(
    r"<skill_dir>/((?:agents|references|scripts)/[A-Za-z0-9_.\-/]+)"
)
FORBIDDEN_PATHS = (
    "/Users/",
    "~/.cursor/",
    "~/.claude/",
    "~/.codex/",
    "$HOME/",
    ".agents/skills/",
)


class ValidationResult(NamedTuple):
    status: str
    skills: int
    errors: List[str]


def _frontmatter(text: str) -> Tuple[List[str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], text
    try:
        end = lines.index("---", 1)
    except ValueError:
        return [], text
    return lines[1:end], "\n".join(lines[end + 1 :])


def _scalar(frontmatter: Sequence[str], key: str) -> str:
    prefix = key + ":"
    for line in frontmatter:
        if line.startswith(prefix):
            return line[len(prefix) :].strip().strip("'\"")
    return ""


def _dependencies(frontmatter: Sequence[str]) -> Set[str]:
    dependencies = set()
    in_dependencies = False
    for line in frontmatter:
        if re.match(r"^  (?:depends_on|used_by):\s*$", line):
            in_dependencies = True
            continue
        if in_dependencies and line.startswith("    - "):
            dependencies.add(line[6:].strip().strip("'\""))
            continue
        if in_dependencies and line.strip() and not line.startswith("    "):
            in_dependencies = False
    return dependencies


def _readme_skills(readme: str) -> Set[str]:
    return set(SKILL_PATH_RE.findall(readme))


def _validate_skill(
    repo_dir: Path,
    skill_file: Path,
    known_skills: Set[str],
    errors: List[str],
) -> None:
    text = skill_file.read_text(encoding="utf-8")
    frontmatter, body = _frontmatter(text)
    relative = str(skill_file.relative_to(repo_dir))
    expected_name = skill_file.parent.name

    if not frontmatter:
        errors.append("{}: missing or unclosed YAML frontmatter".format(relative))
        return

    name = _scalar(frontmatter, "name")
    description = _scalar(frontmatter, "description")
    if name != expected_name:
        errors.append(
            "{}: name {!r} does not match directory {!r}".format(
                relative, name, expected_name
            )
        )
    if not SKILL_NAME_RE.match(expected_name):
        errors.append("{}: directory name must be kebab-case".format(relative))
    if not description:
        errors.append("{}: description is required".format(relative))
    elif ":" in description:
        errors.append("{}: description must not contain a colon".format(relative))

    missing_dependencies = _dependencies(frontmatter) - known_skills
    for dependency in sorted(missing_dependencies):
        errors.append(
            "{}: dependency {!r} is not listed in README".format(
                relative, dependency
            )
        )

    if "<skill_dir>/" in body and "`<skill_dir>`" not in body:
        errors.append("{}: <skill_dir> is used without a declaration".format(relative))

    for forbidden in FORBIDDEN_PATHS:
        if forbidden in body:
            errors.append(
                "{}: contains non-portable path {!r}".format(relative, forbidden)
            )

    for resource in RESOURCE_RE.findall(body):
        resource_path = skill_file.parent / resource.rstrip(".,)")
        if not resource_path.exists():
            errors.append(
                "{}: referenced resource does not exist: {}".format(
                    relative, resource
                )
            )


def validate(repo_dir: Path) -> ValidationResult:
    errors = []  # type: List[str]
    readme_path = repo_dir / "README.md"
    skills_dir = repo_dir / "skills"
    if not readme_path.is_file():
        errors.append("README.md is missing")
    if not skills_dir.is_dir():
        errors.append("skills directory is missing")
    if errors:
        return ValidationResult(status="error", skills=0, errors=errors)

    skill_dirs = sorted(
        path
        for category in ("common", "python")
        for path in (skills_dir / category).glob("*")
        if path.is_dir()
    )
    skill_files = []
    locations = {}  # type: Dict[str, List[str]]
    for skill_dir in skill_dirs:
        relative_dir = str(skill_dir.relative_to(repo_dir))
        locations.setdefault(skill_dir.name, []).append(relative_dir)
        skill_file = skill_dir / "SKILL.md"
        if skill_file.is_file():
            skill_files.append(skill_file)
        else:
            errors.append("{}: SKILL.md is missing".format(relative_dir))

    discovered = {path.name for path in skill_dirs}
    listed = _readme_skills(readme_path.read_text(encoding="utf-8"))

    for name, paths in sorted(locations.items()):
        if len(paths) > 1:
            errors.append(
                "skill {!r} exists in multiple categories: {}".format(
                    name, ", ".join(paths)
                )
            )
    for name in sorted(discovered - listed):
        errors.append("skill {!r} is missing from README".format(name))
    for name in sorted(listed - discovered):
        errors.append("README lists missing skill {!r}".format(name))
    for skill_file in skill_files:
        _validate_skill(repo_dir, skill_file, listed, errors)

    return ValidationResult(
        status="error" if errors else "ok",
        skills=len(skill_dirs),
        errors=errors,
    )


def main(argv: Sequence[str]) -> int:
    if len(argv) > 2:
        sys.stderr.write("usage: validate_project.py [repo_dir]\n")
        return 2
    repo_dir = Path(argv[1] if len(argv) == 2 else ".").resolve()
    result = validate(repo_dir)
    payload = {
        "status": result.status,
        "skills": result.skills,
        "errors": result.errors,
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if result.status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
