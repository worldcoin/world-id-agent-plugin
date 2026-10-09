# Contributing

| Branch | Purpose |
| --- | --- |
| `dev` | Editable sandbox plugin |
| `sandbox` | Released sandbox plugin |
| `main` (default) | Released production plugin |

## Development

Create feature branches from `dev` and open PRs into `dev`. Edit the root user
plugin and `plugins/world-id-developer/` using the sandbox values in `environments/`.
Keep their skills and MCP connections separate. CI generates the release branches.

Keep the name, version, description and author consistent across `plugin.json`,
`.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` within each plugin.
Both plugins use the same release version. You do not need to
bump versions on `dev`; CI sets the release version in the generated packages.

## Testing

Ask Codex or Claude Code to install the repository from your feature branch.
No build is needed. Start a new session and follow the [README](README.md) for
sign-in. Specify branch `sandbox` to return to the released plugin.

CI runs validation and tests. Optional local checks require Python 3.10 or newer:

```sh
python3 scripts/build.py --validate
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/build.py
```

The build writes installable previews to `dist/sandbox/` and `dist/production/`.
Each environment's marketplace lists both plugins.
Add `--version 0.2.0` to preview a specific release version.

## Release

1. Merge and test the plugin changes on `dev`.
2. In GitHub Actions, run **Open release PRs** from `main` and enter a new
   version, such as `0.2.0`. Leave `source_sha` blank to use the latest `dev` commit.
3. CI records the selected SHA in the run summary and tests that source.
   `scripts/build.py` generates both environments with the requested version;
   `scripts/release.py` opens PRs into `sandbox` and `main`.
4. Review, merge and test sandbox first. Test the production preview with
   production test accounts, then merge its PR.

CI does not merge PRs or push directly to protected branches. Merge releases in
order and close superseded PRs.

CI opens release PRs as the `world-id-plugin-releases` GitHub App, so the person
running the workflow can review them. It uses repository variable
`PLUGIN_RELEASE_APP_CLIENT_ID` and secret `PLUGIN_RELEASE_APP_PRIVATE_KEY` to
create a temporary installation token.

New releases must have higher [SemVer precedence](https://semver.org/#spec-item-11)
than the current release on each target. Changing only `+build` metadata does
not count as a version increase. Previously released versions cannot be reused.
To retry a release, enter the same version and the full SHA from its run summary in
`source_sha`. Leaving it blank selects `dev` again, which may have advanced.
Unchanged branches and open PRs are reused.
Inspect and reopen closed release PRs before retrying. To undo a release, revert
on `dev` and publish a new version.

## User installation

After the first production release, developers can ask Codex:

```text
Install this plugin: https://github.com/worldcoin/world-id-agent-plugin
```

`main` contains the complete production plugin. Users need no Python, manual
clone or build step. Specify branch `sandbox` for the sandbox plugin.

Public-directory publication and backend deployment are separate from this
Git release process.
