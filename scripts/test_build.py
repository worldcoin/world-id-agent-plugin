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
            self.assertEqual(files[Path('README.md')], before[Path('README.md')])
            metadata = json.loads(files[Path('release.json')])
            self.assertEqual(metadata['source_commit'], 'a' * 40)
            self.assertEqual(metadata['environment'], environment)
            catalog = json.loads(files[Path('.agents/plugins/marketplace.json')])
            self.assertEqual(catalog['plugins'][0]['policy']['authentication'], 'ON_USE')
            self.assertEqual(files[Path('.github/workflows/release.yml')],
                             (self.root / '.github/workflows/release.yml').read_bytes())
        self.assertEqual(build.package_files(self.root), before)
        self.assertEqual({path: outputs['sandbox'][path] for path in before}, before)
        production = outputs['production']
        readme = production[Path('README.md')].decode()
        self.assertIn('--ref main', readme)
        self.assertIn('.git#main', readme)
        self.assertIn('world-id@world-id', readme)
        self.assertIn('--ref sandbox', readme)
        self.assertIn('.git#sandbox', readme)
        self.assertIn('world-id-sandbox@world-id-demo', readme)
        signin = production[Path('skills/world-id-sign-in/SKILL.md')].decode()
        self.assertIn('auth.world.org', signin)
        developer = production[Path('plugins/world-id-developer/skills/world-id-developer/SKILL.md')].decode()
        self.assertIn('https://auth.world.org/portal/clients/{clientId}', developer)
        self.assertIn('codex mcp login world-id-developer ', developer)

    def test_user_and_developer_plugins_are_separate_in_both_releases(self):
        outputs = build.build_outputs(self.root)
        for environment, user_name, developer_name, issuer in (
            ('production', 'world-id', 'world-id-developer', 'https://auth.world.org'),
            ('sandbox', 'world-id-sandbox', 'world-id-developer-sandbox', 'https://sandbox.auth.world.org'),
        ):
            with self.subTest(environment=environment):
                files = outputs[environment]
                catalog = json.loads(files[Path('.agents/plugins/marketplace.json')])
                self.assertEqual([(entry['name'], entry['source']['path']) for entry in catalog['plugins']],
                                 [(user_name, './'), (developer_name, './plugins/world-id-developer')])
                self.assertEqual(json.loads(files[Path('.mcp.json')])['mcpServers'],
                                 {user_name: {'type': 'http', 'url': issuer + '/mcp'}})
                self.assertEqual(json.loads(files[Path('plugins/world-id-developer/.mcp.json')])['mcpServers'],
                                 {developer_name: {'type': 'http', 'url': issuer + '/mcp/developer'}})
                self.assertEqual(sorted(str(path) for path in files if path.name == 'SKILL.md'), [
                    'plugins/world-id-developer/skills/world-id-developer/SKILL.md',
                    'skills/world-id-account/SKILL.md', 'skills/world-id-benefits/SKILL.md',
                    'skills/world-id-sign-in/SKILL.md',
                ])

    def test_cross_audience_mcp_connection_is_rejected(self):
        path = self.root / 'plugins/world-id-developer/.mcp.json'
        connection = build.read_json(path)
        connection['mcpServers']['world-id-developer-sandbox']['url'] = 'https://sandbox.auth.world.org/mcp'
        path.write_bytes(build.json_bytes(connection))
        with self.assertRaisesRegex(ValueError, 'unexpected MCP connection'):
            build.build_outputs(self.root)

    def test_render_matches_longest_value_once(self):
        configs = build.load_environments(self.root)
        render = build.replacements(configs['sandbox'], configs['production'])
        self.assertEqual(render('world-id-sandbox https://sandbox.auth.world.org/mcp sandbox'),
                         'world-id https://auth.world.org/mcp production')

    def test_release_version_updates_all_manifests_without_changing_source(self):
        before = build.package_files(self.root)
        for version in ('0.2.0', '0.2.0-sandbox.1+build.123'):
            with self.subTest(version=version):
                outputs = build.build_outputs(self.root, 'a' * 40, version)
                for files in outputs.values():
                    for filename in build.ALL_MANIFESTS:
                        self.assertEqual(json.loads(files[Path(filename)])['version'], version)
                    metadata = json.loads(files[Path('release.json')])
                    self.assertEqual(metadata['version'], version)
                    self.assertEqual(metadata['source_commit'], 'a' * 40)
                self.assertEqual(build.package_files(self.root), before)

    def test_invalid_release_versions_fail(self):
        for version in ('', 'latest', 'v0.2.0', '01.2.0', '0.2.0-01', '0.2.0+bad..build',
                        '0.2.0\n', '0.2.0/other'):
            with self.subTest(version=version):
                with self.assertRaisesRegex(ValueError, 'semantic version'):
                    build.build_outputs(self.root, 'a' * 40, version)

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
        path.write_text(original + '\nhttps://auth.world.org/mcp\n')
        with self.assertRaisesRegex(ValueError, 'other environment'):
            build.build_outputs(self.root)
        path.write_text(original + '\n{{missing}}\n')
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            build.build_outputs(self.root)

    def test_cross_environment_hosts_fail_in_both_packages(self):
        configs = build.load_environments(self.root)
        outputs = build.build_outputs(self.root)
        path = Path('skills/world-id-account/SKILL.md')
        for environment, files in outputs.items():
            other = 'sandbox' if environment == 'production' else 'production'
            for reference in (configs[other]['mcp_url'], configs[other]['issuer'].removeprefix('https://')):
                with self.subTest(environment=environment, reference=reference):
                    mixed = {key: files[key] for key in build.package_files(self.root)}
                    mixed[path] += ('\n' + reference + '\n').encode()
                    with self.assertRaisesRegex(ValueError, 'other environment'):
                        build.validate_package(mixed, configs[environment], configs[other])

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
        config['issuer'] = 'http://auth.world.org'
        path.write_bytes(build.json_bytes(config))
        with self.assertRaisesRegex(ValueError, 'HTTPS'):
            build.build_outputs(self.root)


if __name__ == '__main__':
    unittest.main()
