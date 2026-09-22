# World ID (Sandbox)

Connect your sandbox World ID, check your account, and discover partner benefits
from Codex or Claude Code. This hackathon plugin uses only
[`https://sandbox.auth.world.org/mcp`](https://sandbox.auth.world.org/mcp),
not staging or production.

## Getting started

You need Git and either Codex CLI (`codex`) or Claude Code (`claude`) installed
and signed in. **No manual clone, build, Python, or local server is required.**

Have the sandbox World ID app ready and complete its test proof-of-human flow.
A staging or production verification is not a substitute for sandbox setup.

If you previously installed the staging `world-id` plugin, remove or disable it
first. Also disable any separately configured staging World ID MCP server.
The new `world-id-sandbox` identity does not switch existing installations to
sandbox automatically.

### 1. Install the plugin (choose your agent)

#### Codex

Run in your terminal:

```sh
codex plugin marketplace add worldcoin/world-id-agent-plugin
codex plugin add world-id-sandbox@world-id-demo
```

If `codex plugin` is unrecognized, update your Codex CLI before continuing.

#### Claude Code

Run in your terminal:

```sh
claude plugin marketplace add worldcoin/world-id-agent-plugin
claude plugin install world-id-sandbox@world-id-demo
```

Installing the plugin configures its MCP server and skills. It does **not** sign
you into World ID. You do not need to run `codex mcp add` or `claude mcp add`
as well.

### 2. Authorize World ID and launch your agent

#### Codex

**Complete MCP login in your terminal before starting the Codex session.**
If Codex is already running, exit it first, then run:

```sh
codex mcp login world-id-sandbox --scopes mcp:read
```

Complete World ID sign-in and approve access in the browser using your sandbox
app. If the browser does not open, open the URL printed by the command. Keep the
command running until it reports:

```text
Successfully logged in to MCP server 'world-id-sandbox'.
```

Only after login succeeds, launch Codex:

```sh
codex
```

This authorizes World ID access separately from signing into Codex itself.
Codex saves the OAuth credentials and uses them for MCP requests; never paste
tokens into chat. You normally only repeat MCP login if authorization expires,
is revoked, or Codex asks you to reconnect. See the
[Codex MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

Why this order? In our Codex CLI 0.155.1 tests, a session that connected
anonymously did not pick up credentials saved by a later login command. Logging
in before launching avoids that stale connection. If you already completed login
from inside a running session, exit and relaunch Codex before checking again.

#### Claude Code

Launch Claude Code:

```sh
claude
```

Enter `/mcp`, select the sandbox World ID server, and authenticate. Complete
World ID sign-in and consent before continuing. `codex mcp login` does not
authenticate Claude Code.

### 3. Try it

Send these prompts one at a time:

```text
Is my sandbox World ID connected?
What benefits are available?
Help me use the maitre benefit, if available.
```

Account checks and benefit discovery require World ID sign-in and OAuth consent
for `mcp:read`. Public integration guides do not require sign-in. An empty catalog
can mean no offers are published in sandbox yet; partners such as Maître must
also be configured for sandbox. Partner services require their own authorization.
A benefit listing does not confirm eligibility or successful redemption.

## MCP-only setup (without skills)

Use this **instead of** the plugin if you only want the server tools. Do not add
the same connection twice.

Codex:

```sh
codex mcp add world-id-sandbox --url https://sandbox.auth.world.org/mcp
codex mcp login world-id-sandbox --scopes mcp:read
```

Wait for browser sign-in to complete and the login command to report success,
then launch `codex`.

Claude Code:

```sh
claude mcp add --transport http world-id-sandbox https://sandbox.auth.world.org/mcp
claude
```

In Claude Code, run `/mcp` to authenticate.

## Development

The self-contained package is in `plugins/world-id-sandbox/`. Edit its skills,
manifests, and assets directly; there is no build or generated copy to maintain.
Both MCP configuration files must point to the sandbox endpoint.

- `.agents/plugins/marketplace.json`: Codex marketplace.
- `.claude-plugin/marketplace.json`: Claude Code marketplace.
- `plugins/world-id-sandbox/.codex-plugin/plugin.json`: Codex manifest.
- `plugins/world-id-sandbox/.claude-plugin/plugin.json`: Claude Code manifest.
- `plugins/world-id-sandbox/plugin.json` and `mcp.json`: portable manifests.

See the [Codex plugin documentation](https://developers.openai.com/plugins/build/plugins)
and [Claude Code marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces)
for installation details.
