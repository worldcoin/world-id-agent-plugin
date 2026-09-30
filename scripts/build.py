#!/usr/bin/env python3
"""Validate the installable sandbox source and render release branch contents."""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PLUGINS = {"sandbox": "world-id-sandbox", "production": "world-id"}
MANIFESTS = ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json")
PACKAGE_FILES = (*MANIFESTS, "mcp.json", ".mcp.json", "README.md",
                 ".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json")
VERSION_PATTERN = (r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
                   r"(?:-(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
                   r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*)?"
                   r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def load_environments(root):
    configs = {}
    fields = {"name", "environment", "display_name", "mcp_url", "issuer", "portal_url",
              "notice", "branch", "catalog_name", "catalog_display_name"}
    for environment, name in PLUGINS.items():
        path = root / "environments" / f"{environment}.json"
        config = read_json(path)
        if not isinstance(config, dict) or set(config) != fields:
            raise ValueError(f"{path}: expected exactly {sorted(fields)}")
        if any(not isinstance(value, str) or not value for value in config.values()):
            raise ValueError(f"{path}: all values must be nonempty strings")
        branch = "main" if environment == "production" else "sandbox"
        if (config["name"], config["environment"], config["branch"]) != (name, environment, branch):
            raise ValueError(f"{path}: unexpected plugin identity or release branch")
        for key in ("mcp_url", "issuer", "portal_url"):
            url = urlsplit(config[key])
            if (url.scheme != "https" or not url.hostname or url.username is not None
                    or url.password is not None or url.query or url.fragment):
                raise ValueError(f"{path}: {key} must be HTTPS without credentials, query or fragment")
        if (config["mcp_url"] != config["issuer"] + "/mcp"
                or config["portal_url"] != config["issuer"] + "/portal"):
            raise ValueError(f"{path}: MCP and portal URLs must use the configured issuer")
        configs[environment] = config
    for key in ("issuer", "catalog_name"):
        if configs["sandbox"][key] == configs["production"][key]:
            raise ValueError(f"Environments must have distinct {key} values")
    return configs


def package_files(root):
    paths = [Path(path) for path in PACKAGE_FILES]
    for directory in ("skills", "assets"):
        if not (root / directory).is_dir():
            raise ValueError(f"Missing plugin directory: {directory}")
        paths.extend(path.relative_to(root) for path in sorted((root / directory).rglob("*"))
                     if path.is_file())
    for path in paths:
        if (root / path).is_symlink():
            raise ValueError(f"Plugin files must not be symlinks: {path}")
    return {path: (root / path).read_bytes() for path in paths}


def validate_package(files, config, other):
    manifests = [json.loads(files[Path(path)]) for path in MANIFESTS]
    identity = {key: manifests[0][key] for key in ("name", "version", "description", "author")}
    if identity["name"] != config["name"] or not isinstance(identity["version"], str):
        raise ValueError("Plugin identity does not match its environment")
    if not re.fullmatch(VERSION_PATTERN, identity["version"]):
        raise ValueError("Plugin version must be a semantic version")
    for manifest in manifests:
        if any(manifest[key] != value for key, value in identity.items()):
            raise ValueError("Plugin manifests disagree on identity or version")
    codex = manifests[1]
    if codex["skills"] != "./skills/" or codex["mcpServers"] != "./.mcp.json":
        raise ValueError("Codex manifest must reference the root skills and MCP configuration")
    for key in ("composerIcon", "logo"):
        if Path(codex["interface"][key]) not in files:
            raise ValueError(f"Codex {key} references a missing asset")
    for filename, transport in (("mcp.json", "streamable-http"), (".mcp.json", "http")):
        expected = {config["name"]: {"type": transport, "url": config["mcp_url"]}}
        if json.loads(files[Path(filename)])["mcpServers"] != expected:
            raise ValueError(f"{filename}: unexpected MCP connection")
    for filename in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
        catalog = json.loads(files[Path(filename)])
        entries = catalog["plugins"]
        expected_source = {"source": "local", "path": "./"} if filename.startswith(".agents") else "./"
        if (catalog["name"] != config["catalog_name"] or len(entries) != 1
                or entries[0]["name"] != config["name"] or entries[0]["source"] != expected_source):
            raise ValueError(f"{filename}: catalog must expose this environment's root plugin")
    if not any(path.name == "SKILL.md" for path in files):
        raise ValueError("Plugin contains no skills")
    wrong_host = urlsplit(other["issuer"]).netloc.encode()
    # The production host can be a suffix of the sandbox host.
    wrong_host_pattern = re.compile(rb"(?<![\w.-])" + re.escape(wrong_host), re.IGNORECASE)
    for path, data in files.items():
        if path.suffix in (".json", ".md"):
            if b"{{" in data or b"}}" in data:
                raise ValueError(f"{path}: unresolved template marker")
            if wrong_host_pattern.search(data):
                raise ValueError(f"{path}: references the other environment's host")
    return identity["version"]


def replacements(source, target):
    # Match once, longest first: replacing 'sandbox' first would corrupt URLs and names.
    values = {source[key]: target[key] for key in source if key != "branch"}
    values["Sandbox"] = "Production"
    values[urlsplit(source["issuer"]).netloc] = urlsplit(target["issuer"]).netloc
    values.update({f"--ref {source['branch']}": f"--ref {target['branch']}",
                   f".git#{source['branch']}": f".git#{target['branch']}",
                   f"/tree/{source['branch']}": f"/tree/{target['branch']}"})
    pattern = re.compile("|".join(re.escape(key) for key in sorted(values, key=len, reverse=True)))
    return lambda text: pattern.sub(lambda match: values[match[0]], text)


def build_outputs(root, source_sha=None, release_version=None):
    configs = load_environments(root)
    source_files = package_files(root)
    validate_package(source_files, configs["sandbox"], configs["production"])
    if source_sha is not None and not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        raise ValueError("Source commit must be a full lowercase Git SHA")
    # Keep release automation on main so workflow_dispatch remains available there.
    support = [Path("CONTRIBUTING.md"), Path("catalog-info.yaml"), Path(".gitignore")]
    for directory in ("scripts", "environments", ".github"):
        support.extend(path.relative_to(root) for path in sorted((root / directory).rglob("*"))
                       if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc")
    outputs = {}
    for environment, config in configs.items():
        files = dict(source_files)
        if environment == "production":
            render = replacements(configs["sandbox"], config)
            # The README documents both installations and is shared unchanged.
            files = {path: render(data.decode()).encode()
                     if path != Path("README.md") and path.suffix in (".md", ".json") else data
                     for path, data in files.items()}
        other = configs["production" if environment == "sandbox" else "sandbox"]
        if release_version is not None:
            for filename in MANIFESTS:
                path = Path(filename)
                manifest = json.loads(files[path])
                manifest["version"] = release_version
                files[path] = json_bytes(manifest)
        version = validate_package(files, config, other)
        files.update({path: (root / path).read_bytes() for path in support})
        files[Path("release.json")] = json_bytes({
            "environment": environment, "version": version, "source_commit": source_sha,
        })
        outputs[environment] = files
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="Validate this checkout without writing files")
    parser.add_argument("--source-sha", help="Record the source commit in release packages")
    parser.add_argument("--version", help="Set the release version in generated packages only")
    args = parser.parse_args()
    if args.validate and args.version is not None:
        parser.error("--version cannot be used with --validate")
    try:
        if args.validate:
            configs = load_environments(ROOT)
            name = read_json(ROOT / "plugin.json")["name"]
            environment = next(env for env, plugin in PLUGINS.items() if name == plugin)
            other = "sandbox" if environment == "production" else "production"
            validate_package(package_files(ROOT), configs[environment], configs[other])
            print(f"Validated {environment} plugin.")
        else:
            outputs = build_outputs(ROOT, args.source_sha, args.version)
            for environment, files in outputs.items():
                destination = ROOT / "dist" / environment
                if destination.is_symlink():
                    raise ValueError(f"Refusing to replace symlink: {destination}")
                if destination.exists():
                    shutil.rmtree(destination)
                for path, data in files.items():
                    target = destination / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
            print("Built dist/production and dist/sandbox from the sandbox source.")
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as error:
        print(f"Plugin validation/build failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
