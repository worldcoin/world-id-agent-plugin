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
`.codex-plugin/plugin.json` and `.claude-plugin/plugin.json`. You do not need to
bump versions on `dev`; CI sets the release version in the generated packages.

## Testing

Ask Codex or Claude Code to install the repository from your feature branch.
No build is needed. Start a new session and follow the [README](README.md) for
sign-in. Specify branch `sandbox` to return to the released plugin.

### Iterate before merge

For a feature branch, install directly from its Git ref:

```sh
codex plugin marketplace add worldcoin/world-id-agent-plugin --ref codex/verification-first-onboarding
codex plugin add world-id-sandbox@world-id-demo
```

After pushing changes to that branch, refresh the marketplace and reinstall:

```sh
codex plugin marketplace upgrade world-id-demo
codex plugin add world-id-sandbox@world-id-demo
```

Start a fresh chat to load the updated skills and MCP configuration. Invoke
`$world-id-setup` explicitly when testing alongside the production plugin, and
specify sandbox. An existing production connection is not sandbox verification.
The sandbox
marketplace follows the feature branch until you explicitly return it to `sandbox`:

```sh
codex plugin marketplace add worldcoin/world-id-agent-plugin --ref sandbox
codex plugin add world-id-sandbox@world-id-demo
```

For local iteration before pushing, add this checkout's absolute path as the
marketplace source instead. Install through the desktop plugin directory and
start a fresh chat. Local and branch marketplaces use the sandbox plugin identity;
keep only the intended test source selected to avoid testing a stale package.

Each feature-branch PR gets a CI artifact named `release-previews-<commit>` with
both `sandbox/` and `production/` packages, including hidden manifest files.
The production preview uses real accounts and data; generating it does not deploy
or publish anything. Download the desired package and install it from a local
marketplace to test the exact PR commit before merge.

Test setup in a fresh chat and when installing during an existing chat. Cover an
already verified user, successful verification, declined authorization, stale
credentials, browsing without sign-in, and an empty or unavailable benefits
catalog. Verify that partner consent starts only after selecting a partner and
that sign-in alone is never reported as a successful claim.

Plugin branches version skills and MCP configuration; they do not deploy the
remote backend. A hub integration additionally needs an accessible test backend
with the advertised tools and OAuth callbacks. Validate that endpoint separately
before switching a preview package to it. The setup skill uses the public
`start_world_id_setup` welcome and protected `complete_world_id_setup` confirmation
when the test backend advertises them. Without those tools, it uses a text
welcome and the existing account/catalog tools. Installing a newer skill alone
does not add the connection prompt or change the host's authentication callback.

For a backend-team test deployment, request a public HTTPS MCP URL with working
OAuth discovery and callbacks, and confirm the deployed backend commit. Use the
test environment's identity flow and catalog; sandbox identities do not authorize
production benefits. Check that `tools/list` advertises `start_world_id_setup`
with a UI resource and `complete_world_id_setup` with OAuth and no UI resource.
The public welcome must work without sign-in; completion must require a valid
`world-id:read` token.

Add the endpoint as a custom MCP in ChatGPT developer mode and create a private
test plugin. Refresh the connection after backend updates and test in a fresh
conversation with only the intended test plugin selected. A separate deployment
URL must also be set in both MCP configuration files of the local preview package;
keep the released plugin pointed at its normal endpoint.

Test the whole conversation: get started, choose Connect World ID, complete the
host's sign-in, return to the chat, and confirm that verification and real catalog
suggestions appear in the conversation. No second setup card or typed `done`
should be needed in a host that resumes automatically. Repeat with declined
sign-in and with Explore benefits first. Record whether the host supports
`ui/message`, resumes after OAuth, and owns any reconnect banner or callback page.
Catalog approval and merging are not prerequisites for this private test.

CI runs validation and tests. Optional local checks require Python 3.10 or newer:

```sh
python3 scripts/build.py --validate
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/build.py
```

The build writes installable previews to `dist/sandbox/` and `dist/production/`.
Add `--version 0.2.0` to preview a specific release version.

## Release

1. Merge and test changes on `dev`.
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
