#!/usr/bin/env python3
"""Build the self-contained sandbox package from the staging package."""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without writing files")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    source = root / "plugins/world-id"
    target = root / "plugins/world-id-sandbox"
    files = [
        Path(name) for name in (
            "plugin.json", "mcp.json", ".mcp.json",
            ".codex-plugin/plugin.json", ".claude-plugin/plugin.json",
        )
    ]
    for directory in ("skills", "assets"):
        files.extend(
            path.relative_to(source)
            for path in (source / directory).rglob("*") if path.is_file()
        )

    extra = sorted(
        path.relative_to(target)
        for path in target.rglob("*")
        if path.is_file() and path.relative_to(target) not in files
    )
    if extra:
        parser.error(
            "Unexpected sandbox files; review and remove obsolete generated files: "
            + ", ".join(map(str, extra))
        )

    stale = []
    for relative in sorted(files):
        content = (source / relative).read_bytes()
        if relative.suffix in (".json", ".md"):
            content = (
                content.decode("utf-8")
                .replace('"world-id"', '"world-id-sandbox"')
                .replace("World ID (Staging)", "World ID (Sandbox)")
                .replace("auth.worldcoin.dev", "sandbox.auth.world.org")
                .encode("utf-8")
            )
        destination = target / relative
        if destination.exists() and destination.read_bytes() == content:
            continue
        stale.append(str(relative))
        if not args.check:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)

    if args.check and stale:
        print("Sandbox package is out of date: " + ", ".join(stale), file=sys.stderr)
        print("Run python3 scripts/sync-sandbox-plugin.py", file=sys.stderr)
        return 1
    print("Sandbox package is up to date." if args.check else "Sandbox package synchronized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
