import json
import subprocess
import sys
from typing import Dict, List, Optional, Set, Tuple


def _run_git(args: List[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=check,
    )


def _git_stdout(args: List[str]) -> str:
    cp = _run_git(args, check=True)
    return (cp.stdout or "").strip()


def _parse_commit_tree_lines(text: str) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            continue
        commit_hash, tree_hash = parts
        if len(commit_hash) == 40 and len(tree_hash) == 40:
            pairs.append((commit_hash, tree_hash))
    return pairs


def _build_remote_tree_set(merge_base: str, remote_ref: str) -> Set[str]:
    # 仅统计分叉点之后远端新增的提交，避免把共享历史误判为 squash 对齐结果。
    output = _git_stdout(["rev-list", "--format=%H %T", f"{merge_base}..{remote_ref}"])
    return {tree for _, tree in _parse_commit_tree_lines(output)}


def _find_local_tree_match(merge_base: str, remote_trees: Set[str]) -> Optional[str]:
    # 按 first-parent 从 HEAD 向后找“最近的可匹配树”，
    # 这样当当前分支在 squash 前提交后又有新提交时，会优先定位到那个“已被上游吸收”的最近点。
    output = _git_stdout(["rev-list", "--first-parent", "--format=%H %T", "HEAD", f"^{merge_base}"])
    for commit_hash, tree_hash in _parse_commit_tree_lines(output):
        if tree_hash in remote_trees:
            return commit_hash
    return None


def choose_rebase_base(remote: str, default_branch: str) -> Dict[str, str]:
    remote_ref = f"{remote}/{default_branch}"
    _run_git(["fetch", remote, default_branch], check=True)

    merge_base = _git_stdout(["merge-base", "HEAD", remote_ref])
    remote_trees = _build_remote_tree_set(merge_base, remote_ref)
    matched_local_commit = _find_local_tree_match(merge_base, remote_trees)

    if matched_local_commit:
        return {
            "base_commit": matched_local_commit,
            "strategy": "tree_match",
            "merge_base": merge_base,
            "remote_ref": remote_ref,
        }

    return {
        "base_commit": merge_base,
        "strategy": "merge_base_fallback",
        "merge_base": merge_base,
        "remote_ref": remote_ref,
    }


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        sys.stderr.write("usage: select_rebase_base.py <remote> <default_branch>\n")
        return 2

    remote, default_branch = argv[1], argv[2]
    try:
        result = choose_rebase_base(remote, default_branch)
    except subprocess.CalledProcessError as exc:
        err = (exc.stderr or "").strip()
        sys.stderr.write(f"[select_rebase_base] git command failed: {' '.join(exc.cmd)}\n")
        if err:
            sys.stderr.write(f"{err}\n")
        return 1

    sys.stdout.write(json.dumps(result, ensure_ascii=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
