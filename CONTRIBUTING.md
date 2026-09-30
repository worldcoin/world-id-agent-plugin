# Contributing

| Branch | Purpose |
| --- | --- |
| `dev` | Editable sandbox plugin |
| `sandbox` | Released sandbox plugin |
| `main` (default) | Released production plugin |

## Development

Create feature branches from `dev` and open PRs into `dev`. Edit the root plugin
using the sandbox values in `environments/`. CI generates the release branches.

Keep the name, version, description and author consistent across `plugin.json`,
`.codex-plugin/plugin.json` and `.claude-plugin/plugin.json`. Changed plugin
content needs a new version. Do not reuse a previously released version.

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

## Release

1. Merge and test changes on `dev`.
2. In GitHub Actions, run **Open release PRs** from `main` with the full
   40-character `dev` commit SHA.
3. CI tests the source. `scripts/build.py` generates both environments;
   `scripts/release.py` opens PRs into `sandbox` and `main`.
4. Review, merge and test sandbox first. Test the production preview with
   production test accounts, then merge its PR.

CI does not merge PRs or push directly to protected branches. Merge releases in
order and close superseded PRs.

Retry failed runs with the same SHA; unchanged branches and open PRs are reused.
Inspect and reopen closed release PRs before retrying. To undo a release, revert
on `dev` and publish a new version.

## One-time setup

1. Merge this layout and its workflows into `main`. Create `dev` and `sandbox`
   from that commit. Keep `main` as default; it becomes production after the
   first production release PR merges.
2. Protect all three branches with required reviews and validation. Require
   release PRs to be up to date before merging.
3. Set repository secret `PLUGIN_RELEASE_TOKEN` to a fine-grained token limited
   to this repository, with **Contents**, **Pull requests** and **Workflows**
   read/write permissions. No branch-protection bypass is needed.
4. Move existing sandbox installs to branch `sandbox` before releasing production.
   Sandbox keeps marketplace name `world-id-demo`; production uses `world-id`.

## User installation

After the first production release, developers can ask Codex:

```text
Install this plugin: https://github.com/worldcoin/world-id-agent-plugin
```

`main` contains the complete production plugin. Users need no Python, manual
clone or build step. Specify branch `sandbox` for the sandbox plugin.

Public-directory publication and backend deployment are separate from this
Git release process.
