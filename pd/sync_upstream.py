"""Prepare an upstream merge for verification; this script never pushes or releases."""

import argparse
import json
import os
from pathlib import Path
import subprocess

from apply_branding import apply


UPSTREAM = "https://github.com/ChrisTitusTech/winutil"


def git(root, *arguments, check=True):
    return subprocess.run(["git", *arguments], cwd=root, check=check, capture_output=True, text=True)


def record_upstream(root, ref):
    """Store deterministic provenance and an unmodified copy of the upstream README."""
    commit = git(root, "rev-parse", "--verify", f"{ref}^{{commit}}").stdout.strip()
    commit_date = git(root, "show", "-s", "--format=%cI", commit).stdout.strip()
    readme = subprocess.run(["git", "show", f"{commit}:README.md"], cwd=root,
                            check=True, capture_output=True).stdout
    provenance = {"repository": UPSTREAM, "branch": "main", "commit": commit, "commit_date": commit_date}
    path = Path(root) / "pd/upstream.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8", newline="\n")
    archive = Path(root) / "docs/upstream/README.md"
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_bytes(readme)


def prepare(root, ref="upstream/main"):
    """Merge into a clean checkout, leaving the candidate uncommitted for testing."""
    root = Path(root)
    if git(root, "status", "--porcelain").stdout.strip():
        raise RuntimeError("Upstream sync needs a clean checkout. Commit or stash your work first.")
    commit = git(root, "rev-parse", "--verify", f"{ref}^{{commit}}").stdout.strip()
    has_updates = git(root, "merge-base", "--is-ancestor", commit, "HEAD", check=False)
    if has_updates.returncode not in (0, 1):
        raise RuntimeError(has_updates.stderr)
    try:
        if has_updates.returncode == 1:
            merged = git(root, "merge", "--no-ff", "--no-commit", commit, check=False)
            if merged.returncode:
                conflicts = git(root, "diff", "--name-only", "--diff-filter=U").stdout.splitlines()
                source_conflicts = [name for name in conflicts if name != "README.md"]
                if source_conflicts or not conflicts:
                    details = ", ".join(source_conflicts) or merged.stderr or merged.stdout
                    raise RuntimeError(f"Upstream merge needs manual resolution: {details}")
                # README is generated from the fork-owned template. Never resolve source conflicts this way.
                git(root, "checkout", "--ours", "--", "README.md")
                git(root, "add", "--", "README.md")
        apply(root)
        record_upstream(root, commit)
    except Exception:
        if git(root, "rev-parse", "--verify", "MERGE_HEAD", check=False).returncode == 0:
            git(root, "merge", "--abort")
        raise
    return bool(git(root, "status", "--porcelain").stdout.strip())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="upstream/main", help="A fetched upstream ref; no network fetch is performed here")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    changed = prepare(root, args.ref)
    result = f"changed={str(changed).lower()}\n"
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(result)
    print(result, end="")
