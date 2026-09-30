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

    def write_packages(self, version=None):
        for environment, files in build.build_outputs(self.repo, self.sha, version).items():
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

    def advance_target(self, base):
        release.git(self.repo, 'checkout', '--detach', f'origin/{base}')
        (self.repo / 'target-only.txt').write_text('Added after the release PR opened')
        release.git(self.repo, 'add', 'target-only.txt')
        release.git(self.repo, 'commit', '-m', 'Advance release target')
        release.git(self.repo, 'push', 'origin', f'HEAD:refs/heads/{base}')
        release.git(self.repo, 'fetch', 'origin')
        release.git(self.repo, 'checkout', 'dev')

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

    def test_same_source_can_have_distinct_release_versions(self):
        before = build.package_files(self.repo)
        branches = {}
        for version in ('0.2.0', '0.3.0+build.lock'):
            self.write_packages(version)
            for environment, base in (('sandbox', 'sandbox'), ('production', 'main')):
                branch = self.prepare(environment)
                self.assertEqual(branch, f'release/{environment}/{version}-{self.sha}')
                branches[branch] = self.remote_sha(branch)
                self.assertEqual(self.prepare(environment), branch)
                self.merge_release(branch, base)
                self.assertIsNone(self.prepare(environment))
        self.assertEqual(len(branches), 4)
        for branch, commit in branches.items():
            self.assertEqual(self.remote_sha(branch), commit)
        self.assertEqual(build.package_files(self.repo), before)

    def test_retry_recreates_matching_release_on_current_target(self):
        for environment, base in (('sandbox', 'sandbox'), ('production', 'main')):
            with self.subTest(environment=environment):
                branch = self.prepare(environment)
                first = self.remote_sha(branch)
                expected_tree = release.git(self.repo, 'rev-parse', f'{first}^{{tree}}')
                self.advance_target(base)
                target = self.remote_sha(base)

                self.assertEqual(self.prepare(environment), branch)
                updated = self.remote_sha(branch)
                self.assertNotEqual(updated, first)
                self.assertEqual(release.git(self.repo, 'rev-parse', f'{updated}^'), target)
                self.assertEqual(release.git(self.repo, 'rev-parse', f'{updated}^{{tree}}'), expected_tree)
                self.assertEqual(self.remote_sha(base), target)
                self.assertEqual(self.prepare(environment), branch)
                self.assertEqual(self.remote_sha(branch), updated)

                self.merge_release(branch, base)
                names = release.git(self.repo, 'ls-tree', '-r', '--name-only', f'origin/{base}').splitlines()
                self.assertNotIn('target-only.txt', names)
                self.assertIsNone(self.prepare(environment))

    def test_retry_preserves_concurrent_release_branch_update(self):
        branch = self.prepare()
        first = self.remote_sha(branch)
        self.advance_target('main')
        target = self.remote_sha('main')
        concurrent = release.git(self.repo, 'commit-tree', f'{first}^{{tree}}', '-p', first,
                                 '-m', 'Concurrent release branch update')
        release.git(self.repo, 'push', 'origin', f'{concurrent}:refs/heads/concurrent-update')
        real_run = release.run

        def update_before_push(*args, cwd, check=True):
            if args[:2] == ('git', 'push'):
                real_run('git', 'update-ref', f'refs/heads/{branch}', concurrent, cwd=self.remote)
            return real_run(*args, cwd=cwd, check=check)

        with mock.patch.object(release, 'run', side_effect=update_before_push):
            with self.assertRaisesRegex(RuntimeError, 'git push failed'):
                self.prepare()
        self.assertEqual(self.remote_sha(branch), concurrent)
        self.assertEqual(self.remote_sha('main'), target)

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
        self.write_packages('0.2.0')
        self.assertIsNotNone(self.prepare())

    def test_historical_version_cannot_be_reused_after_another_release(self):
        original_version = build.read_json(self.repo / 'plugin.json')['version']
        targets = (('sandbox', 'sandbox'), ('production', 'main'))
        for environment, base in targets:
            self.merge_release(self.prepare(environment), base)

        # Release A, then B, then attempt A again with different content.
        for version in ('0.2.0', original_version):
            skill = self.repo / 'skills/world-id-account/SKILL.md'
            skill.write_text(skill.read_text() + '\nChanged account guidance.\n')
            release.git(self.repo, 'add', '.')
            release.git(self.repo, 'commit', '-m', f'Prepare {version}')
            self.sha = release.git(self.repo, 'rev-parse', 'HEAD')
            self.write_packages(version)
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
                            f'refs/heads/release/{environment}/{version}-{self.sha}'), '')

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
