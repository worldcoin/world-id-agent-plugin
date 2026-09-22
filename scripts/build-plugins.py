#!/usr/bin/env python3
"""Package both World ID environments with the shared skills and assets."""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check dist without writing files")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    output = root / "dist"
    marketplace = Path(".agents/plugins/marketplace.json")
    files = {marketplace: (root / marketplace).read_bytes()}
    for name in ("world-id", "world-id-sandbox"):
        destination = Path("plugins") / name
        for source, prefix in (
            (root / "plugins" / name, destination),
            (root / "skills", destination / "skills"),
            (root / "assets", destination / "assets"),
        ):
            if not source.is_dir():
                parser.error(f"Missing source directory: {source}")
            for path in sorted(source.rglob("*")):
                if path.is_symlink():
                    parser.error(f"Package sources must be regular files: {path}")
                if path.is_file():
                    relative = prefix / path.relative_to(source)
                    if relative in files:
                        parser.error(f"Duplicate package path: {relative}")
                    files[relative] = path.read_bytes()

    extra = sorted(
        path.relative_to(output)
        for path in output.rglob("*")
        if path.is_file() and path.relative_to(output) not in files
    )
    if extra:
        parser.error(
            "Unexpected dist files; review and remove obsolete build output: "
            + ", ".join(map(str, extra))
        )

    stale = []
    for relative, content in files.items():
        destination = output / relative
        if destination.is_file() and destination.read_bytes() == content:
            continue
        stale.append(str(relative))
        if not args.check:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)

    if args.check and stale:
        print("Build output is out of date: " + ", ".join(stale), file=sys.stderr)
        print("Run python3 scripts/build-plugins.py", file=sys.stderr)
        return 1
    print("Build output is up to date." if args.check else "Built both plugins in dist/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
