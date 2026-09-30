#!/usr/bin/env python3
"""Open release PRs from validated packages; never push to main or sandbox."""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import build


def run(*args, cwd, check=True):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=120)
    if check and result.returncode:
        raise RuntimeError(f"{args[0]} {args[1]} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result


def git(repo, *args):
    return run("git", *args, cwd=repo).stdout.strip()


def prepare_branch(repo, package, environment, source_sha):
    base = "main" if environment == "production" else "sandbox"
    branch = f"release/{environment}/{source_sha}"
    config = build.load_environments(repo)
    files = build.package_files(package)
    version = build.validate_package(files, config[environment], config[
        "sandbox" if environment == "production" else "production"])
    metadata = build.read_json(package / "release.json")
    if metadata != {"environment": environment, "version": version, "source_commit": source_sha}:
        raise ValueError(f"{environment}: release metadata does not match the requested source")
    with tempfile.TemporaryDirectory(prefix="world-id-release-") as temp:
        worktree = Path(temp) / "checkout"
        git(repo, "worktree", "add", "--detach", str(worktree), f"origin/{base}")
        try:
            previous_release = worktree / "release.json"
            if previous_release.exists():
                previous = build.read_json(previous_release)
                ancestor = run("git", "merge-base", "--is-ancestor", previous["source_commit"],
                               source_sha, cwd=repo, check=False)
                if ancestor.returncode != 0:
                    raise ValueError(f"{base}: candidate must descend from the released source commit")
                if previous["version"] == version and build.package_files(worktree) != files:
                    raise ValueError(f"{base}: changed plugin content requires a new version")
                if previous["version"] != version:
                    if git(repo, "rev-parse", "--is-shallow-repository") == "true":
                        raise ValueError(f"{base}: full Git history is required to check released versions")
                    # Follow the target branch's releases, excluding unmerged source/PR history.
                    revisions = git(repo, "log", "--first-parent", "--format=%H",
                                    f"origin/{base}", "--", "release.json").splitlines()
                    for revision in revisions:
                        past = json.loads(git(repo, "show", f"{revision}:release.json"))
                        if past["version"] == version:
                            raise ValueError(f"{base}: version {version} was previously released; choose a new version")
            git(worktree, "rm", "-r", "--ignore-unmatch", "--", ".")
            shutil.copytree(package, worktree, dirs_exist_ok=True)
            git(worktree, "add", "--all")
            tree = git(worktree, "write-tree")
            if tree == git(worktree, "rev-parse", "HEAD^{tree}"):
                return None
            existing = git(repo, "ls-remote", "--heads", "origin", f"refs/heads/{branch}")
            expected_head = ""
            if existing:
                git(repo, "fetch", "origin", f"refs/heads/{branch}")
                expected_head = git(repo, "rev-parse", "FETCH_HEAD")
                if git(repo, "rev-parse", f"{expected_head}^{{tree}}") != tree:
                    raise ValueError(f"{branch}: existing release branch differs; refusing to overwrite it")
                ancestor = run("git", "merge-base", "--is-ancestor", "HEAD", expected_head,
                               cwd=worktree, check=False)
                if ancestor.returncode == 0:
                    return branch
                if ancestor.returncode != 1:
                    raise RuntimeError(f"{branch}: ancestry check failed: {ancestor.stderr.strip()}")
            # Recreate the full snapshot on the current target, including new deletions.
            git(worktree, "-c", "user.name=github-actions[bot]", "-c",
                "user.email=41898282+github-actions[bot]@users.noreply.github.com",
                "commit", "-m", f"Release {environment} {version} from {source_sha}")
            git(worktree, "push", "origin", f"--force-with-lease=refs/heads/{branch}:{expected_head}",
                f"HEAD:refs/heads/{branch}")
        finally:
            git(repo, "worktree", "remove", "--force", str(worktree))
    return branch


def publish(repo, source_sha, repository):
    if not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        raise ValueError("Source commit must be a full lowercase Git SHA")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Repository must be owner/name")
    # Fetch every target before writing anything; missing bootstrap branches fail here.
    git(repo, "fetch", "origin", "dev:refs/remotes/origin/dev",
        "main:refs/remotes/origin/main", "sandbox:refs/remotes/origin/sandbox")
    git(repo, "merge-base", "--is-ancestor", source_sha, "origin/dev")
    for environment in ("sandbox", "production"):
        package = repo / "dist" / environment
        branch = prepare_branch(repo, package, environment, source_sha)
        if branch is None:
            print(f"{environment}: already released", flush=True)
            continue
        base = "main" if environment == "production" else "sandbox"
        existing = json.loads(run("gh", "pr", "list", "--repo", repository, "--head", branch,
                                  "--base", base, "--state", "all", "--json", "url,state",
                                  cwd=repo).stdout)
        if existing:
            if existing[0]["state"] != "OPEN":
                raise ValueError(f"Release PR is {existing[0]['state']}: {existing[0]['url']}; inspect before retrying")
            print(existing[0]["url"], flush=True)
        else:
            metadata = build.read_json(package / "release.json")
            body = (
                f"Publish the {environment} plugin from dev commit `{source_sha}`.\n\n"
                "This branch contains the ready-to-install plugin at the repository root. "
                "CI validated both environments and ran the source regression tests before opening this PR.\n\n"
                "Review the environment URLs and version, then merge using the normal protected-branch rules. "
                "Install and smoke-test sandbox before merging the matching production PR. "
                "Public-directory submission is a separate step.\n"
            )
            with tempfile.TemporaryDirectory(prefix="world-id-pr-") as temp:
                body_path = Path(temp) / "body.md"
                body_path.write_text(body)
                result = run("gh", "pr", "create", "--repo", repository, "--base", base,
                             "--head", branch, "--title", f"Release {environment} {metadata['version']}",
                             "--body-file", str(body_path), cwd=repo)
                print(result.stdout.strip(), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()
    try:
        publish(build.ROOT, args.source_sha, args.repository)
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"Release PR creation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
