#!/usr/bin/env python3
"""Generate the installable plugins and catalogs using only the standard library."""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PLUGINS = {"sandbox": "world-id-sandbox", "production": "world-id"}
TOKEN = re.compile(r"\{\{([a-z_]+)\}\}")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def render(text, config):
    def substitute(match):
        key = match[1]
        if key not in config or not isinstance(config[key], str):
            raise ValueError(f"Missing string template value: {key}")
        return config[key]

    result = TOKEN.sub(substitute, text)
    if "{{" in result or "}}" in result:
        raise ValueError("Unresolved template marker")
    return result


def render_json(value, config):
    if isinstance(value, str):
        return render(value, config)
    if isinstance(value, list):
        return [render_json(item, config) for item in value]
    if isinstance(value, dict):
        return {key: render_json(item, config) for key, item in value.items()}
    return value


def load_environment(root, environment, name):
    path = root / "environments" / f"{environment}.json"
    config = read_json(path)
    fields = {
        "name", "environment", "display_name", "qualifier", "mcp_url",
        "issuer", "portal_url", "notice",
    }
    if not isinstance(config, dict) or set(config) != fields:
        raise ValueError(f"{path}: expected exactly {sorted(fields)}")
    if config["name"] != name or config["environment"] != environment:
        raise ValueError(f"{path}: plugin name or environment does not match")
    for key in fields:
        if not isinstance(config[key], str) or (key != "qualifier" and not config[key]):
            raise ValueError(f"{path}: {key} must be a string")
    for key in ("mcp_url", "issuer", "portal_url"):
        url = urlsplit(config[key])
        if (url.scheme != "https" or not url.hostname or url.username is not None
                or url.password is not None or url.query or url.fragment):
            raise ValueError(f"{path}: {key} must be an HTTPS URL without credentials, query or fragment")
    config["auth_host"] = urlsplit(config["issuer"]).netloc
    return config


def build_outputs(root):
    outputs = {}
    catalog = read_json(root / "src/marketplace.json")
    codex_entries, claude_entries = [], []
    configs = [load_environment(root, env, name) for env, name in PLUGINS.items()]
    for key in ("mcp_url", "issuer", "portal_url"):
        if configs[0][key] == configs[1][key]:
            raise ValueError(f"Sandbox and production must have distinct {key} values")
    for config in configs:
        name = config["name"]
        destination = Path("plugins") / name
        manifest = render_json(read_json(root / "src/plugin.json"), config)
        identity = {key: manifest[key] for key in ("name", "version", "description", "author")}
        outputs[destination / ".codex-plugin/plugin.json"] = json_bytes(manifest)
        outputs[destination / ".claude-plugin/plugin.json"] = json_bytes(identity)
        outputs[destination / "plugin.json"] = json_bytes({
            "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            **identity,
        })
        for filename, transport in (("mcp.json", "streamable-http"), (".mcp.json", "http")):
            mcp = {"mcpServers": {name: {"type": transport, "url": config["mcp_url"]}}}
            if filename == "mcp.json":
                mcp = {"$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", **mcp}
            outputs[destination / filename] = json_bytes(mcp)
        for path in sorted((root / "src/skills").rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(root / "src")
            outputs[destination / relative] = render(path.read_text(encoding="utf-8"), config).encode()
        for path in sorted((root / "src/assets").rglob("*")):
            if path.is_file():
                outputs[destination / path.relative_to(root / "src")] = path.read_bytes()
        codex_entries.append({
            "name": name,
            "source": {"source": "local", "path": f"./plugins/{name}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        })
        claude_entries.append({
            "name": name, "source": f"./plugins/{name}", "description": identity["description"],
        })
    outputs[Path(".agents/plugins/marketplace.json")] = json_bytes({
        "name": catalog["name"], "interface": {"displayName": catalog["display_name"]},
        "plugins": codex_entries,
    })
    outputs[Path(".claude-plugin/marketplace.json")] = json_bytes({
        "name": catalog["name"], "owner": {"name": catalog["owner"]},
        "metadata": {"description": "World ID plugins for production and sandbox."},
        "plugins": claude_entries,
    })
    return outputs


def sync_outputs(root, outputs, check=False):
    existing = {
        path.relative_to(root)
        for name in PLUGINS.values()
        for path in (root / "plugins" / name).rglob("*") if path.is_file()
    }
    stale = existing - outputs.keys()
    changed = [path for path, data in outputs.items()
               if not (root / path).is_file() or (root / path).read_bytes() != data]
    if check:
        for path in sorted(stale | set(changed)):
            print(f"Generated output differs: {path}", file=sys.stderr)
        return not (stale or changed)
    for path in changed:
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(outputs[path])
    for path in stale:
        (root / path).unlink()
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if committed outputs differ; write nothing")
    args = parser.parse_args()
    try:
        outputs = build_outputs(ROOT)
        if not sync_outputs(ROOT, outputs, check=args.check):
            return 1
    except (OSError, ValueError, KeyError) as error:
        print(f"Plugin build failed: {error}", file=sys.stderr)
        return 1
    print("Generated plugins are current." if args.check else "Built sandbox and production plugins.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
