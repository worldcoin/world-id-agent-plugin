# World ID (Sandbox)

Connect your sandbox World ID, check your account, and discover partner benefits
from Codex or Claude Code. This hackathon plugin uses only
[`https://sandbox.auth.world.org/mcp`](https://sandbox.auth.world.org/mcp),
not staging or production.

## Getting started

You need Git and either Codex CLI (`codex`) or Claude Code (`claude`) installed
and signed in. **No manual clone, build, Python, or local server is required.**

If you previously installed the staging `world-id` plugin, remove or disable it
first. Also disable any separately configured staging World ID MCP server.
The new `world-id-sandbox` identity does not switch existing installations to
sandbox automatically.

### 1. Install in your agent (choose one)

#### Codex

Run in your terminal:

```sh
codex plugin marketplace add worldcoin/world-id-agent-plugin
codex plugin add world-id-sandbox@world-id-demo
codex
```

If `codex plugin` is unrecognized, update your Codex CLI before continuing.

#### Claude Code

Run in your terminal:

```sh
claude plugin marketplace add worldcoin/world-id-agent-plugin
claude plugin install world-id-sandbox@world-id-demo
claude
```

**Testing before this change is merged?** Replace the first command for your
agent with the corresponding branch-specific command below, then run the install
and launch commands above:

```sh
# Codex
codex plugin marketplace add worldcoin/world-id-agent-plugin --ref codex/world-id-sandbox-hackathon

# Claude Code
claude plugin marketplace add worldcoin/world-id-agent-plugin@codex/world-id-sandbox-hackathon
```

### 2. Connect your sandbox World ID

Inside your agent, enter `/mcp` and check that the sandbox World ID connection
is listed. Complete World ID sign-in and OAuth consent when prompted. In Claude
Code, select the server in `/mcp` to authenticate. If Codex reports authentication
is required without opening a prompt, check its available connection controls;
repeated tool calls do not guarantee that a sign-in window will open.

Use the sandbox World app and complete its test proof-of-human flow. A staging
or production verification is not a substitute for sandbox setup.

### 3. Try it

Send these prompts one at a time:

```text
Connect my sandbox World ID.
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
codex
```

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
