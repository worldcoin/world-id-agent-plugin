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

After installing the plugin, sign in to World ID using the steps below.

### 2. Authorize World ID and launch your agent

Already connected before the scope migration? Existing connections were revoked.
Repeat the authorization steps below to reconnect with `world-id:read`.

#### Codex

Run this in your terminal before starting Codex. If Codex is already running,
exit it first:

```sh
codex mcp login world-id-sandbox --scopes world-id:read
```

Complete browser sign-in using your sandbox app and wait for the command to
report success. If the browser does not open, open the URL printed by the command.
Then start Codex:

```sh
codex
```

This authorizes World ID access separately from signing into Codex itself.
Codex saves the OAuth credentials and uses them for MCP requests; never paste
tokens into chat. You normally only repeat MCP login if authorization expires,
is revoked, or Codex asks you to reconnect.

#### Claude Code

Launch Claude Code:

```sh
claude
```

Enter `/mcp`, select the sandbox World ID server, and authenticate. If asked how
to connect, choose **Connect World ID**. Complete World ID sign-in and consent
before continuing. `codex mcp login` does not authenticate Claude Code.

### 3. Try it

Send these prompts one at a time:

```text
Is my sandbox World ID connected?
What benefits are available?
Help me use the maitre benefit, if available.
```
