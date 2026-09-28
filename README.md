# World ID plugins

Connect your World ID, discover partner benefits, or register and configure
an app's World ID sign-in from Codex or Claude Code.

| Plugin | Environment | MCP endpoint |
| --- | --- | --- |
| `world-id` | Production | `https://auth.worldcoin.dev/mcp` |
| `world-id-sandbox` | Sandbox | `https://sandbox.auth.world.org/mcp` |

Both packages are generated from shared sources. Each has its own MCP connection
and authorization. Choose the environment you intend to use; test accounts and
app registrations belong to that environment. When testing, enable only the
intended plugin to avoid ambiguous skill selection.

## Getting started

You need Git and either Codex CLI (`codex`) or Claude Code (`claude`) installed
and signed in. **No manual clone, build, Python, or local server is required.**

For account and benefit tools, complete the World ID verification flow in your
chosen environment. Sandbox requires its own test proof-of-human setup. For app
registration, install the same plugin below, then follow
[Developer setup](#developer-setup); only Google portal sign-in is required.

### 1. Install the plugin (choose your agent)

The commands below install production. For sandbox, replace `world-id` with
`world-id-sandbox` in install and login commands, including both occurrences in
Claude Code's `plugin:world-id:world-id` server name. The marketplace name remains
`world-id-demo` for compatibility with existing installations.

#### Codex

Run in your terminal:

```sh
codex plugin marketplace add worldcoin/world-id-agent-plugin
codex plugin add world-id@world-id-demo
```

If `codex plugin` is unrecognized, update your Codex CLI before continuing.

#### Claude Code

Run in your terminal:

```sh
claude plugin marketplace add worldcoin/world-id-agent-plugin
claude plugin install world-id@world-id-demo
```

After installing the plugin, sign in to World ID using the steps below.

### 2. Authorize World ID and launch your agent

#### Codex

Run this in your terminal before starting Codex. If Codex is already running,
exit it first:

```sh
codex mcp login world-id --scopes world-id:read
```

Complete browser sign-in using the app for your chosen environment and wait for
the command to report success. If the browser does not open, open the URL printed
by the command. Then start Codex:

```sh
codex
```

This authorizes World ID access separately from signing into Codex itself.
Codex saves the OAuth credentials and uses them for MCP requests; never paste
tokens into chat. You normally only repeat MCP login if authorization expires,
is revoked, or Codex asks you to reconnect.

#### Claude Code

Run this in your terminal before starting Claude Code:

```sh
claude mcp login plugin:world-id:world-id
```

Complete World ID sign-in in the browser. If asked how to connect, choose
**Connect World ID**. Then start Claude Code:

```sh
claude
```

You can also sign in from inside Claude Code: enter `/mcp`, select your chosen
World ID server, and authenticate. `codex mcp login` does not authenticate
Claude Code.

### 3. Try it

Send these prompts one at a time:

```text
Is my World ID connected?
What benefits are available?
Help me use the maitre benefit, if available.
```

## Developer setup

The bundled `world-id-developer` skill registers OIDC clients and updates
their callback URLs, name, and logo through MCP tools. Developer access uses
Google portal sign-in and the `developer-portal:manage` scope, separately from
the `world-id:read` scope used by account and benefit tools.

### Codex

Before starting Codex, authorize developer access in your terminal:

```sh
codex mcp login world-id --scopes developer-portal:manage
```

Complete Google sign-in and portal consent, wait for the command to succeed,
then start a new Codex session. If you also want account and benefit tools,
request both scopes with `--scopes world-id:read,developer-portal:manage`;
that also requires World ID sign-in in the chosen environment.

### Claude Code

Ask to register or configure your app. Follow the portal tool's authorization
challenge for `developer-portal:manage` and complete Google sign-in and consent.
If authentication is needed, use `/mcp` to select and authenticate your chosen
World ID server. World ID-only authorization does not grant developer access.

### Register or configure an app

```text
Register my app with World ID. My callback URL is https://my-app.example/auth/world/callback.
Update my app's logo and callback URLs.
```

Use your actual HTTPS callback URL; these environments do not accept HTTP
localhost callbacks. The agent gathers the remaining details and prepares registration.
Open its returned portal link to review and approve the request within 20
minutes. Save any generated client secret directly in your backend's secure
configuration; never paste it into chat. The agent checks completion and returns
your client ID and public configuration.

Registration does not publish a benefit listing. For that, open the app's
**Catalog** tab in the portal, save a listing, and submit it for review as the
app owner. An authorized reviewer outside the app's team must approve it before
it is published. Catalog submission is not currently exposed through MCP.

## Development

Development happens in this public repository on short-lived feature branches.
Edit the sources, regenerate both packages, and commit the sources and outputs
in the same pull request. Python 3.10 or newer is needed only by maintainers;
plugin users do not need Python or a build step. No Python dependencies are
required.

```text
src/plugin.json           Shared metadata and release version
src/marketplace.json      Shared marketplace identity
src/skills/               Shared skills with {{variable}} substitutions
src/assets/               Shared assets
environments/             Explicit sandbox and production configuration
scripts/build.py          Deterministic package generator
plugins/world-id/         Generated production package
plugins/world-id-sandbox/ Generated sandbox package
```

Do not edit files under `plugins/` or the two marketplace catalogs directly.
The build owns those outputs and removes obsolete files inside the two generated
plugin directories. It does not contact a backend or publish anything.

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m unittest discover -s scripts -p 'test_*.py'
```

`--check` writes nothing and fails if an output is missing, modified, or stale.
CI runs this check and the regression tests on pull requests and pushes to main.
The build fails on missing template values, invalid environment configuration,
or identical sandbox and production endpoint settings. Both hosts' manifests
get their version from `src/plugin.json`; update it when distributing changed
plugin content.

### Share a test build

Push the branch with its generated packages committed. Colleagues can select
that Git ref when adding the marketplace:

```sh
codex plugin marketplace add worldcoin/world-id-agent-plugin --ref feature/my-change
codex plugin add world-id-sandbox@world-id-demo
```

Substitute the actual branch or a release tag for `feature/my-change`. This
selects a revision of the existing marketplace; it does not create a second
marketplace identity. Verify the selected source with
`codex plugin marketplace list`, refresh/reinstall after changes, and start a
new session to test the installed copy. Follow the sandbox authentication
instructions above. Test behavior in both Codex and Claude Code before release.

### Prepare a production release

1. Test the candidate against sandbox, including authorization failures and
   denied or expired registration approval.
2. Set the release version in `src/plugin.json`, regenerate, and run the checks.
3. Smoke-test the generated `world-id` package with designated production test
   accounts. Package validation does not verify backend availability or OAuth.
4. Merge the reviewed changes and tag the tested commit. For stable Git-based
   distribution, consumers can select that release tag with `--ref`.

A Git push does not submit a plugin to OpenAI's public directory. Directory
publication and remote MCP backend deployments are separate release steps.
Deploy compatible backend support before releasing skills that depend on it;
keep older installed plugins working. Retain previous release tags for recovery.
