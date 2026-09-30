"""Regression checks for direct installation and environment rendering."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import build


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for path, data in build.package_files(build.ROOT).items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        for directory in ('environments', 'scripts', '.github'):
            shutil.copytree(build.ROOT / directory, self.root / directory,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for name in ('CONTRIBUTING.md', '.gitignore', 'catalog-info.yaml'):
            shutil.copyfile(build.ROOT / name, self.root / name)

    def test_source_is_installable_without_building(self):
        configs = build.load_environments(self.root)
        version = build.validate_package(build.package_files(self.root), configs['sandbox'], configs['production'])
        self.assertTrue(version)
        self.assertFalse((self.root / 'dist').exists())

    def test_both_releases_are_isolated_and_do_not_modify_source(self):
        before = build.package_files(self.root)
        outputs = build.build_outputs(self.root, 'a' * 40)
        configs = build.load_environments(self.root)
        for environment, files in outputs.items():
            other = 'sandbox' if environment == 'production' else 'production'
            package = {path: files[path] for path in before}
            build.validate_package(package, configs[environment], configs[other])
            self.assertEqual(files[Path('assets/world-id.png')], before[Path('assets/world-id.png')])
            metadata = json.loads(files[Path('release.json')])
            self.assertEqual(metadata['source_commit'], 'a' * 40)
            self.assertEqual(metadata['environment'], environment)
            self.assertEqual(files[Path('.github/workflows/release.yml')],
                             (self.root / '.github/workflows/release.yml').read_bytes())
        self.assertEqual(build.package_files(self.root), before)
        self.assertEqual({path: outputs['sandbox'][path] for path in before}, before)
        production = outputs['production']
        readme = production[Path('README.md')].decode()
        self.assertIn('--ref main', readme)
        self.assertIn('.git#main', readme)
        self.assertIn('world-id@world-id', readme)
        self.assertNotIn('sandbox', readme)
        signin = production[Path('skills/world-id-sign-in/SKILL.md')].decode()
        self.assertIn('auth.worldcoin.dev', signin)
        developer = production[Path('skills/world-id-developer/SKILL.md')].decode()
        self.assertIn('https://auth.worldcoin.dev/portal/clients/{clientId}', developer)
        self.assertIn('codex mcp login world-id ', developer)

    def test_render_matches_longest_value_once(self):
        configs = build.load_environments(self.root)
        render = build.replacements(configs['sandbox'], configs['production'])
        self.assertEqual(render('world-id-sandbox https://sandbox.auth.world.org/mcp sandbox'),
                         'world-id https://auth.worldcoin.dev/mcp production')

    def test_missing_and_mismatched_manifests_fail(self):
        path = self.root / '.claude-plugin/plugin.json'
        manifest = build.read_json(path)
        manifest['version'] = '99.0.0'
        path.write_bytes(build.json_bytes(manifest))
        with self.assertRaisesRegex(ValueError, 'disagree'):
            build.build_outputs(self.root)
        path.unlink()
        with self.assertRaises(FileNotFoundError):
            build.build_outputs(self.root)

    def test_mixed_hosts_and_placeholders_fail(self):
        path = self.root / 'skills/world-id-account/SKILL.md'
        original = path.read_text()
        path.write_text(original + '\nhttps://auth.worldcoin.dev/mcp\n')
        with self.assertRaisesRegex(ValueError, 'other environment'):
            build.build_outputs(self.root)
        path.write_text(original + '\n{{missing}}\n')
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            build.build_outputs(self.root)

    def test_catalog_cannot_point_to_missing_generated_directory(self):
        path = self.root / '.agents/plugins/marketplace.json'
        catalog = build.read_json(path)
        catalog['plugins'][0]['source']['path'] = './plugins/world-id-sandbox'
        path.write_bytes(build.json_bytes(catalog))
        with self.assertRaisesRegex(ValueError, 'root plugin'):
            build.build_outputs(self.root)

    def test_invalid_environment_and_source_commit_fail(self):
        with self.assertRaisesRegex(ValueError, 'full lowercase Git SHA'):
            build.build_outputs(self.root, '--bad-ref')
        path = self.root / 'environments/production.json'
        config = build.read_json(path)
        config['issuer'] = 'http://auth.worldcoin.dev'
        path.write_bytes(build.json_bytes(config))
        with self.assertRaisesRegex(ValueError, 'HTTPS'):
            build.build_outputs(self.root)


if __name__ == '__main__':
    unittest.main()
