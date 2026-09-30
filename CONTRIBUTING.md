# Development and releases

`dev` is the source branch. It contains an installable sandbox plugin at the
repository root: real sandbox URLs, skill instructions, manifests and assets.
Make changes on feature branches and open PRs into `dev`. Do not edit generated
release branches or merge them back into `dev`.

| Branch | Plugin | Updated through |
| --- | --- | --- |
| `dev` | Editable sandbox source | Feature PRs |
| `sandbox` | Released `world-id-sandbox` | Generated release PRs |
| `main` (default) | Released production `world-id` | Generated release PRs |

## Test a feature branch

No Python or build is needed to install a feature branch. Ask your agent to
install this repository from that branch, or run:

```sh
codex plugin marketplace add worldcoin/world-id-agent-plugin --ref feature/my-change
codex plugin add world-id-sandbox@world-id-demo
```

For Claude Code:

```sh
claude plugin marketplace add https://github.com/worldcoin/world-id-agent-plugin.git#feature/my-change
claude plugin install world-id-sandbox@world-id-demo
```

Replace `feature/my-change` with the actual branch. This changes the source of
the sandbox marketplace; check the configured source before testing or updating.
To return to released sandbox, use `sandbox` as the ref. Start a new session after
installation and follow the README's environment-specific authentication steps.
Production has a separate plugin, MCP server and marketplace identity (`world-id`)
so changing the sandbox source does not replace the production connection.

## Change and validate the source

Edit the root plugin files directly. Keep the name, version, description and
author consistent in `plugin.json`, `.codex-plugin/plugin.json`, and
`.claude-plugin/plugin.json`. Bump the version before releasing changed plugin
content. Environment settings live in `environments/`; the source must continue
to use the sandbox values.

CI validates the source, runs regression tests, and renders release previews.
Maintainers can run the same checks locally with Python 3.10 or newer (standard
library only):

```sh
python3 scripts/build.py --validate
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/build.py
```

The builder writes `dist/sandbox/` and `dist/production/`; it never edits the
source plugin. Both outputs are installable repository roots, including hidden
manifests and single-plugin catalogs. Production replaces sandbox names, URLs,
issuer, portal links, notices and installation refs in the plugin and README.
Replacement uses the longest match first and a single pass. Keep environment
references consistent with the configured values rather than inventing aliases.
CI rejects unresolved placeholders, mixed environment hosts, mismatched manifests
and broken catalog paths. Assets and release tooling are copied unchanged.

To inspect a production preview locally, add `./dist/production` as a local
marketplace. Python is only needed by maintainers building previews and by CI;
plugin users never run it. Previews also appear in successful source CI runs as
`release-previews-<commit SHA>` artifacts.

## One-time repository setup

1. Land this layout and both workflows on `main` to bootstrap automation. Before
   the first production release, create `dev` and `sandbox` from that same commit.
   `main` temporarily contains sandbox source until its first release PR merges.
2. Keep `main` as the default branch so the bare repository URL resolves to
   production after that first release. Set feature PRs to target `dev` explicitly.
3. Protect `dev`, `main` and `sandbox` with review and validation requirements.
   Release CI writes only `release/*` branches and opens PRs; it needs no bypass
   permission for the protected branches. Require branches to be up to date before
   merging, and merge matching releases in order.
4. Configure `PLUGIN_RELEASE_TOKEN` as a repository secret: a fine-grained token
   restricted to this repository with **Contents**, **Pull requests**, and
   **Workflows** read/write permissions, owned by an authorized release account.
   Workflows permission is needed because release branches also carry changes to
   `.github/workflows/`. Do not grant bypass access to the protected branches.
   Follow the organization's token approval and rotation policy.
5. Before changing `main` to production, move existing sandbox installations to
   the explicit `sandbox` ref using the README commands. The sandbox marketplace
   keeps its existing `world-id-demo` identity; production uses `world-id`.

The manual release workflow must exist on the default branch. It runs from
`main`, checks out `dev`, and requires an exact commit reachable from `dev`.
See [GitHub's manual workflow documentation](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

## Release

1. Merge and test the source changes on `dev`. Update the version in all three
   manifests, and smoke-test authentication, account status, benefits and app
   registration against sandbox. Check denied and expired authorization paths.
2. In Actions, select **Open release PRs**, keep the workflow ref as `main`, and
   provide the full 40-character `dev` commit SHA. Or run:

   ```sh
   gh workflow run release.yml --ref main -f source_sha=<full-dev-commit-sha>
   ```

3. CI validates and builds both environments from that commit. It pushes
   `release/sandbox/<SHA>` and `release/production/<SHA>` and opens PRs into
   `sandbox` and `main`. Each package records its source in `release.json`.
4. Review the PRs. Merge sandbox first and test its installed package, then
   smoke-test production with designated production test accounts and merge its
   PR. The protected branches only change when their PRs merge.

Release PRs use the release account's token so their normal **Build and validate
plugins** checks run. The built-in `GITHUB_TOKEN` is not used for publishing:
workflow-file updates need additional permission, and its generated PRs have
different workflow-trigger behavior. See [GitHub's token event behavior](https://docs.github.com/en/actions/concepts/security/github_token).

Release runs are serialized. If one PR succeeds and the next operation fails,
the run fails visibly; rerun with the same source SHA. CI reuses an identical
release branch and open PR, skips already released output, and refuses to
force-push a modified release branch. A closed, unmerged PR requires inspection
and reopening before retrying. Package changes without a version change fail.
A candidate older than the already released source also fails. Do not merge an
older outstanding release after a newer one; close superseded release PRs.

For recovery, revert the faulty source change on `dev`, bump the version and
release that new commit. This preserves forward version ordering for installed
clients. Backend deployments remain separate; deploy compatible backend support
before releasing skills that depend on it and keep older clients working.

## Distribution

The bare repository URL selects production on `main`; the sandbox branch URL
selects the sandbox release. An agent can perform the native host installation
from either prompt. The generated catalogs point to the ready-to-install root
plugin, and Git-backed catalogs should track the appropriate release branch.
Users still need to refresh/update their installed plugin through their host.

This repository has no configured external marketplace publishing API or
credentials. Merging a release updates Git distribution and its catalogs; it
does not submit to OpenAI's public directory. Submit the exact reviewed production
package through the directory's publication process. Sandbox is for development
and testing. Add a marketplace-specific publishing integration only when its
actual destination and supported API are configured.
