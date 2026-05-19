import argparse
import json
import os
import subprocess
import sys
from typing import Dict, List, Sequence, Tuple

from select_rebase_base import choose_rebase_base


class StepError(RuntimeError):
    def __init__(self, message: str, returncode: int = 1) -> None:
        super().__init__(message)
        self.returncode = returncode


class RebaseConflictError(StepError):
    def __init__(self, conflicted_files: Sequence[str], returncode: int) -> None:
        super().__init__(
            "git rebase failed; resolve conflicts manually and run git rebase --continue",
            returncode,
        )
        self.conflicted_files = list(conflicted_files)


def _run_git(args: Sequence[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=check,
    )


def _git_stdout(args: Sequence[str]) -> str:
    cp = _run_git(args, check=True)
    return (cp.stdout or "").strip()


def _print_step(name: str, **payload: object) -> None:
    data = {"step": name, **payload}
    sys.stdout.write(json.dumps(data, ensure_ascii=True, sort_keys=True))
    sys.stdout.write("\n")
    sys.stdout.flush()


def _repo_root() -> str:
    return _git_stdout(["rev-parse", "--show-toplevel"])


def _current_head() -> str:
    return _git_stdout(["rev-parse", "HEAD"])


def _has_staged_changes() -> bool:
    cp = _run_git(["diff", "--cached", "--quiet"], check=False)
    if cp.returncode == 0:
        return False
    if cp.returncode == 1:
        return True
    raise subprocess.CalledProcessError(cp.returncode, cp.args, cp.stdout, cp.stderr)


def _staged_files() -> List[str]:
    output = _git_stdout(["diff", "--cached", "--name-only", "--diff-filter=ACMR"])
    return [line for line in output.splitlines() if line]


def _untracked_files() -> List[str]:
    output = _git_stdout(["ls-files", "--others", "--exclude-standard"])
    return [line for line in output.splitlines() if line]


def _pre_commit_config_exists(repo_root: str) -> bool:
    return os.path.exists(os.path.join(repo_root, ".pre-commit-config.yaml"))


def _run_pre_commit_on_staged(files: Sequence[str]) -> None:
    if not files:
        return
    cp = subprocess.run(
        ["pre-commit", "run", "--files", *files],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if cp.stdout:
        sys.stdout.write(cp.stdout)
    if cp.stderr:
        sys.stderr.write(cp.stderr)
    if cp.returncode != 0:
        raise StepError("pre-commit failed; fix issues and rerun", cp.returncode)


def _commit(message: str) -> str:
    cp = _run_git(["commit", "-m", message], check=False)
    if cp.stdout:
        sys.stdout.write(cp.stdout)
    if cp.stderr:
        sys.stderr.write(cp.stderr)
    if cp.returncode != 0:
        raise StepError("git commit failed", cp.returncode)
    return _current_head()


def _rebase_onto(rebase_info: Dict[str, str]) -> Tuple[bool, str]:
    before = _current_head()
    cp = _run_git(
        [
            "rebase",
            "--autostash",
            "--onto",
            rebase_info["remote_ref"],
            rebase_info["base_commit"],
        ],
        check=False,
    )
    if cp.stdout:
        sys.stdout.write(cp.stdout)
    if cp.stderr:
        sys.stderr.write(cp.stderr)
    if cp.returncode != 0:
        conflicted = _git_stdout(["diff", "--name-only", "--diff-filter=U"])
        conflicted_files = [line for line in conflicted.splitlines() if line]
        raise RebaseConflictError(conflicted_files, cp.returncode)
    after = _current_head()
    return before != after, after


def _has_upstream(branch: str) -> bool:
    cp = _run_git(["rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"], check=False)
    return cp.returncode == 0


def _push(origin_remote: str, current_branch: str, force_with_lease: bool) -> None:
    args = ["push", origin_remote, current_branch]
    if force_with_lease:
        args.append("--force-with-lease")
    elif not _has_upstream(current_branch):
        args.insert(1, "--set-upstream")
    cp = _run_git(args, check=False)
    if cp.stdout:
        sys.stdout.write(cp.stdout)
    if cp.stderr:
        sys.stderr.write(cp.stderr)
    if cp.returncode != 0:
        raise StepError("git push failed", cp.returncode)


def run(args: argparse.Namespace) -> int:
    repo_root = _repo_root()
    untracked = _untracked_files()
    if untracked:
        _print_step("untracked_ignored", files=untracked)

    _run_git(["add", "--update"], check=True)
    if not _has_staged_changes():
        _print_step("skip", reason="no staged changes; skipped commit/push")
        return 0

    staged = _staged_files()
    _print_step("staged", files=staged)

    if _pre_commit_config_exists(repo_root) and not args.skip_pre_commit:
        _print_step("pre_commit", mode="staged_files")
        _run_pre_commit_on_staged(staged)
        _run_git(["add", "--update"], check=True)
        if not _has_staged_changes():
            _print_step("skip", reason="no staged changes after pre-commit; skipped commit/push")
            return 0

    committed_head = _commit(args.message)
    _print_step("commit", head=committed_head)

    rebase_info = choose_rebase_base(args.upstream_remote, args.default_branch)
    _print_step("rebase_base", **rebase_info)
    rebased, head_after_rebase = _rebase_onto(rebase_info)
    _print_step("rebase", changed=rebased, head=head_after_rebase)

    if not args.no_push:
        _push(args.origin_remote, args.current_branch, force_with_lease=rebased)
        _print_step("push", branch=args.current_branch, force_with_lease=rebased, remote=args.origin_remote)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Commit staged tracked changes, rebase with squash-aware base selection, and push."
    )
    parser.add_argument("upstream_remote")
    parser.add_argument("origin_remote")
    parser.add_argument("default_branch")
    parser.add_argument("current_branch")
    parser.add_argument("--message", required=True, help="commit message generated by the agent")
    parser.add_argument(
        "--skip-pre-commit",
        action="store_true",
        help="skip explicit pre-commit run and rely on the commit hook",
    )
    parser.add_argument("--no-push", action="store_true", help="commit and rebase but skip push")
    return parser


def main(argv: Sequence[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv[1:])
    try:
        return run(args)
    except subprocess.CalledProcessError as exc:
        err = (exc.stderr or "").strip()
        sys.stderr.write(f"[commit_rebase_push] git command failed: {' '.join(exc.cmd)}\n")
        if err:
            sys.stderr.write(f"{err}\n")
        return exc.returncode or 1
    except RebaseConflictError as exc:
        _print_step("rebase_conflict", conflicted_files=exc.conflicted_files)
        sys.stderr.write(f"[commit_rebase_push] {exc}\n")
        return exc.returncode
    except StepError as exc:
        sys.stderr.write(f"[commit_rebase_push] {exc}\n")
        return exc.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
