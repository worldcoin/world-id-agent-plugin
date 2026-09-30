"""Exercise release publication against a local bare Git remote, never GitHub."""

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import build
import release


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.repo = base / 'source'
        self.repo.mkdir()
        self.remote = base / 'remote.git'
        release.git(base, 'init', '--bare', str(self.remote))
        release.git(self.repo, 'init', '--initial-branch=dev')
        release.git(self.repo, 'config', 'user.name', 'Release Test')
        release.git(self.repo, 'config', 'user.email', 'release-test@example.invalid')
        source = build.build_outputs(build.ROOT)['sandbox']
        for path, data in source.items():
            if path != Path('release.json'):
                target = self.repo / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        (self.repo / 'obsolete.txt').write_text('old package layout')
        release.git(self.repo, 'add', '.')
        release.git(self.repo, 'commit', '-m', 'Sandbox source')
        self.sha = release.git(self.repo, 'rev-parse', 'HEAD')
        release.git(self.repo, 'remote', 'add', 'origin', str(self.remote))
        release.git(self.repo, 'push', 'origin', 'HEAD:dev', 'HEAD:main', 'HEAD:sandbox')
        release.git(self.repo, 'fetch', 'origin')
        self.write_packages()

    def write_packages(self):
        for environment, files in build.build_outputs(self.repo, self.sha).items():
            for path, data in files.items():
                target = self.repo / 'dist' / environment / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)

    def prepare(self, environment='production'):
        return release.prepare_branch(self.repo, self.repo / 'dist' / environment, environment, self.sha)

    def remote_sha(self, branch):
        return release.git(self.repo, 'ls-remote', '--heads', 'origin', f'refs/heads/{branch}').split()[0]

    def merge_release(self, branch, base='main'):
        release.git(self.repo, 'fetch', 'origin', f'refs/heads/{branch}')
        release.git(self.repo, 'push', 'origin', f'FETCH_HEAD:refs/heads/{base}')
        release.git(self.repo, 'fetch', 'origin')

    def test_release_branches_are_complete_and_targets_stay_unchanged(self):
        for environment in ('sandbox', 'production'):
            branch = self.prepare(environment)
            self.assertTrue(branch.startswith(f'release/{environment}/'))
            release.git(self.repo, 'fetch', 'origin', f'refs/heads/{branch}')
            names = release.git(self.repo, 'ls-tree', '-r', '--name-only', 'FETCH_HEAD').splitlines()
            self.assertNotIn('obsolete.txt', names)
            self.assertIn('.codex-plugin/plugin.json', names)
            self.assertIn('.github/workflows/release.yml', names)
            manifest = json.loads(release.git(self.repo, 'show', 'FETCH_HEAD:plugin.json'))
            self.assertEqual(manifest['name'], build.PLUGINS[environment])
        self.assertEqual(self.remote_sha('main'), self.sha)
        self.assertEqual(self.remote_sha('sandbox'), self.sha)
        self.assertEqual(release.git(self.repo, 'status', '--porcelain'), '')

    def test_retry_reuses_branch_and_skips_merged_release(self):
        branch = self.prepare()
        first = self.remote_sha(branch)
        self.assertEqual(self.prepare(), branch)
        self.assertEqual(self.remote_sha(branch), first)
        self.merge_release(branch)
        self.assertIsNone(self.prepare())

    def test_retry_refuses_to_overwrite_modified_release_branch(self):
        branch = self.prepare()
        release.git(self.remote, 'update-ref', f'refs/heads/{branch}', self.sha)
        with self.assertRaisesRegex(ValueError, 'refusing to overwrite'):
            self.prepare()
        self.assertEqual(self.remote_sha(branch), self.sha)

    def test_changed_package_requires_version_bump(self):
        self.merge_release(self.prepare())
        path = self.repo / 'skills/world-id-account/SKILL.md'
        path.write_text(path.read_text() + '\nUpdated account guidance.\n')
        release.git(self.repo, 'add', '.')
        release.git(self.repo, 'commit', '-m', 'Change guidance')
        self.sha = release.git(self.repo, 'rev-parse', 'HEAD')
        self.write_packages()
        with self.assertRaisesRegex(ValueError, 'new version'):
            self.prepare()
        for filename in build.MANIFESTS:
            path = self.repo / filename
            data = build.read_json(path)
            data['version'] = '0.2.0'
            path.write_bytes(build.json_bytes(data))
        release.git(self.repo, 'add', '.')
        release.git(self.repo, 'commit', '-m', 'Bump version')
        self.sha = release.git(self.repo, 'rev-parse', 'HEAD')
        self.write_packages()
        self.assertIsNotNone(self.prepare())

    def test_historical_version_cannot_be_reused_after_another_release(self):
        original_version = build.read_json(self.repo / 'plugin.json')['version']
        targets = (('sandbox', 'sandbox'), ('production', 'main'))
        for environment, base in targets:
            self.merge_release(self.prepare(environment), base)

        # Release A, then B, then attempt A again with different content.
        for version in ('0.2.0', original_version):
            for filename in build.MANIFESTS:
                path = self.repo / filename
                manifest = build.read_json(path)
                manifest['version'] = version
                path.write_bytes(build.json_bytes(manifest))
            skill = self.repo / 'skills/world-id-account/SKILL.md'
            skill.write_text(skill.read_text() + '\nChanged account guidance.\n')
            release.git(self.repo, 'add', '.')
            release.git(self.repo, 'commit', '-m', f'Prepare {version}')
            self.sha = release.git(self.repo, 'rev-parse', 'HEAD')
            self.write_packages()
            for environment, base in targets:
                with self.subTest(environment=environment, version=version):
                    if version == '0.2.0':
                        self.merge_release(self.prepare(environment), base)
                    else:
                        before = self.remote_sha(base)
                        with self.assertRaisesRegex(ValueError, 'previously released'):
                            self.prepare(environment)
                        self.assertEqual(self.remote_sha(base), before)
                        self.assertEqual(release.git(
                            self.repo, 'ls-remote', '--heads', 'origin',
                            f'refs/heads/release/{environment}/{self.sha}'), '')

    def test_partial_pr_failure_is_visible_and_retry_reuses_open_pr(self):
        real_run = release.run
        created = set()
        fail_production = True

        def fake_gh(*args, cwd, check=True):
            if args[0] != 'gh':
                return real_run(*args, cwd=cwd, check=check)
            branch = args[args.index('--head') + 1]
            if args[1:3] == ('pr', 'list'):
                data = [{'url': f'https://example.invalid/{branch}', 'state': 'OPEN'}] if branch in created else []
                return subprocess.CompletedProcess(args, 0, json.dumps(data), '')
            if args[1:3] == ('pr', 'create'):
                if fail_production and '/production/' in branch:
                    raise RuntimeError('simulated GitHub outage')
                created.add(branch)
                return subprocess.CompletedProcess(args, 0, f'https://example.invalid/{branch}', '')
            self.fail(f'Unexpected GitHub command: {args[:3]}')

        with mock.patch.object(release, 'run', side_effect=fake_gh), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'simulated GitHub outage'):
                release.publish(self.repo, self.sha, 'example/plugins')
            self.assertEqual(len(created), 1)
            fail_production = False
            release.publish(self.repo, self.sha, 'example/plugins')
        self.assertEqual(len(created), 2)
        self.assertEqual(self.remote_sha('main'), self.sha)
        self.assertEqual(self.remote_sha('sandbox'), self.sha)

    def test_invalid_source_is_rejected_before_remote_operations(self):
        with mock.patch.object(release, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'full lowercase Git SHA'):
                release.publish(self.repo, '--bad-ref', 'example/plugins')
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
