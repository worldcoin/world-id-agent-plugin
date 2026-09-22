# World ID

Connect your World ID, check your account, and discover partner benefits from an
AI agent. Choose **sandbox** for the hackathon or **staging** for staging tests.

| Environment | Plugin | MCP endpoint |
| --- | --- | --- |
| Sandbox (hackathon) | `world-id-sandbox` | `https://sandbox.auth.world.org/mcp` |
| Staging | `world-id` | `https://auth.worldcoin.dev/mcp` |

Enable only one World ID environment plugin at a time. The existing `world-id`
plugin remains staging so current installations keep their environment.
Each environment requires its own sign-in and has its own app registrations
and benefit catalog. A partner must also be configured for the chosen environment.

## Install the plugin

Run these commands from this repository's root after cloning it.

### Codex

Add this checkout as a marketplace, then install **one** plugin:

```sh
codex plugin marketplace add .
codex plugin add world-id-sandbox@world-id-demo
codex
```

For staging, use `world-id@world-id-demo` instead. Complete authentication when
prompted. Use `/mcp` to inspect the connection and the host's authentication
controls if sign-in is required. Start a new session after installing or updating.

To switch from staging to sandbox, remove `world-id@world-id-demo` with
`codex plugin remove`, then install `world-id-sandbox@world-id-demo` and start a
new session. Reverse the names to switch back. Also disable any manually added
World ID MCP connection to the other environment; removing a plugin does not
remove separately configured servers.

### Claude Code

Load the selected plugin for this session:

```sh
claude --plugin-dir ./plugins/world-id-sandbox
```

For staging, use `./plugins/world-id`. Run `/mcp` inside Claude Code and
authenticate the selected World ID server. To switch environments, exit and
start Claude Code with the other directory. Disable any previously installed
World ID plugin or manually added server for the other environment first.

## MCP-only setup

For just the server tools, without the plugin's skills, use the commands below
instead of installing the plugin. Do not configure both routes for the same
environment.

Codex:

```sh
codex mcp add world-id-sandbox --url https://sandbox.auth.world.org/mcp
codex mcp login world-id-sandbox --scopes mcp:read
codex
```

Claude Code:

```sh
claude mcp add --transport http world-id-sandbox https://sandbox.auth.world.org/mcp
claude
```

In Claude Code, run `/mcp` to authenticate. For staging, replace the server name
with `world-id-staging` and the URL with `https://auth.worldcoin.dev/mcp`.
Remove or disable the previous environment's connection before switching.

## Try it

> Connect my World ID.
>
> What benefits are available?
>
> Help me use one of those benefits.

Account checks and benefit discovery require World ID sign-in and OAuth consent
for `mcp:read`. Public integration guides do not require sign-in.
Benefit listings describe offers, not confirmed eligibility or redemption.
Partner services require their own authorization.

## Development

The staging package in `plugins/world-id/` is the shared source. After editing it,
regenerate the self-contained sandbox package and commit both:

```sh
python3 scripts/sync-sandbox-plugin.py
python3 scripts/sync-sandbox-plugin.py --check
```

The generated sandbox package changes only the plugin/server identity,
environment labels, and hostname. Edit shared skills and assets in the staging
source, not the generated copy. No local server or build step is required to
install either committed package.

Each package includes portable `plugin.json` and `mcp.json` files, Codex's
`.codex-plugin/plugin.json` and `.mcp.json`, and Claude Code's
`.claude-plugin/plugin.json`. Both MCP files within a package point to the same
environment. `.agents/plugins/marketplace.json` lists both Codex plugins.

See the [Codex MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
and [Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference)
for host setup details.
