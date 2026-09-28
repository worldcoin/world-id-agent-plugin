"""Regression checks for package isolation and generated output maintenance."""

import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit

import build


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(build.ROOT / "src", self.root / "src")
        shutil.copytree(build.ROOT / "environments", self.root / "environments")

    def test_packages_are_isolated_and_manifests_agree(self):
        outputs = build.build_outputs(self.root)
        for environment, name in build.PLUGINS.items():
            base = Path("plugins") / name
            config = build.read_json(self.root / "environments" / f"{environment}.json")
            manifests = [json.loads(outputs[base / path]) for path in
                         ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json")]
            self.assertEqual({m["name"] for m in manifests}, {name})
            self.assertEqual(len({m["version"] for m in manifests}), 1)
            for filename in ("mcp.json", ".mcp.json"):
                servers = json.loads(outputs[base / filename])["mcpServers"]
                self.assertEqual(set(servers), {name})
                self.assertEqual(servers[name]["url"], config["mcp_url"])
            other = "production" if environment == "sandbox" else "sandbox"
            other_config = build.read_json(self.root / "environments" / f"{other}.json")
            wrong_host = urlsplit(other_config["issuer"]).netloc
            for path, content in outputs.items():
                if base in path.parents and path.suffix in (".json", ".md"):
                    self.assertNotIn(wrong_host.encode(), content, str(path))
                    self.assertNotIn(b"{{", content, str(path))
            self.assertIn(base / "skills/world-id-sign-in/SKILL.md", outputs)

    def test_check_detects_edits_and_stale_files_without_writing(self):
        outputs = build.build_outputs(self.root)
        build.sync_outputs(self.root, outputs)
        self.assertTrue(build.sync_outputs(self.root, outputs, check=True))
        edited = self.root / "plugins/world-id/plugin.json"
        edited.write_text("manual edit")
        stale = self.root / "plugins/world-id/skills/removed.md"
        stale.write_text("old skill")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertFalse(build.sync_outputs(self.root, outputs, check=True))
        self.assertEqual(edited.read_text(), "manual edit")
        self.assertTrue(stale.exists())
        build.sync_outputs(self.root, outputs)
        self.assertFalse(stale.exists())
        self.assertTrue(build.sync_outputs(self.root, outputs, check=True))

    def test_missing_template_value_fails_before_output_is_written(self):
        (self.root / "src/skills/world-id-account/SKILL.md").write_text("{{missing}}")
        with self.assertRaisesRegex(ValueError, "missing"):
            build.build_outputs(self.root)
        self.assertFalse((self.root / "plugins").exists())

    def test_shared_endpoint_is_rejected(self):
        path = self.root / "environments/production.json"
        config = build.read_json(path)
        config["mcp_url"] = "https://sandbox.auth.world.org/mcp"
        path.write_bytes(build.json_bytes(config))
        with self.assertRaisesRegex(ValueError, "distinct mcp_url"):
            build.build_outputs(self.root)


if __name__ == "__main__":
    unittest.main()
