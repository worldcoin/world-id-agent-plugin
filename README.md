# World ID (Sandbox)

Connect your sandbox World ID, discover partner benefits, or register and
configure your app's World ID sign-in from Codex or Claude Code. This hackathon
plugin uses only
[`https://sandbox.auth.world.org/mcp`](https://sandbox.auth.world.org/mcp),
not staging or production.

## Getting started

You need Git and either Codex CLI (`codex`) or Claude Code (`claude`) installed
and signed in. **No manual clone, build, Python, or local server is required.**

For account and benefit tools, have the sandbox World ID app ready and complete
its test proof-of-human flow. A staging or production verification is not a
substitute for sandbox setup. For app registration, install the same plugin
below, then follow [Developer setup](#developer-setup); only Google portal
sign-in is required.

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

Installing the plugin does not sign you in. After installing, authorize World
ID with `claude mcp login` using the steps below.

### 2. Authorize World ID and launch your agent

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

Run this in your terminal before starting Claude Code. If Claude Code is already
running, exit it first:

```sh
claude mcp login plugin:world-id-sandbox:world-id-sandbox
```

This is the Claude Code equivalent of `codex mcp login`. The server name carries
a `plugin:world-id-sandbox:` prefix because the plugin supplies it; run
`claude mcp list` to see the exact name. Complete browser sign-in using your
sandbox app and wait for the command to report success. If asked how to connect,
choose **Connect World ID**. On an SSH or headless machine, add `--no-browser` to
print the authorization URL and paste the redirect URL back when prompted.
Claude Code has no `--scopes` option; this sign-in grants `world-id:read`, and
developer access is authorized separately (see
[Developer setup](#developer-setup)). Then start Claude Code:

```sh
claude
```

Alternatively, start `claude` first, enter `/mcp`, select the sandbox World ID
server, and choose **Authenticate**. Either path stores the OAuth credentials and
uses them for MCP requests; never paste tokens into chat. `codex mcp login` does
not authenticate Claude Code.

`/mcp` and `claude mcp list` report the server as **Connected** even before you
sign in, because the server accepts anonymous connections and only requires
World ID for protected tools. To confirm you are signed in, ask
`Is my sandbox World ID connected?` in a session. If tools fail with
"Sign in with World ID and allow access to continue", exit Claude Code and run
`claude mcp login plugin:world-id-sandbox:world-id-sandbox` again.

### 3. Try it

Send these prompts one at a time:

```text
Is my sandbox World ID connected?
What benefits are available?
Help me use the maitre benefit, if available.
```

## Developer setup

The bundled `world-id-developer` skill registers sandbox OIDC clients and updates
their callback URLs, name, and logo through MCP tools. Developer access uses
Google portal sign-in and the `developer-portal:manage` scope, separately from
the `world-id:read` scope used by account and benefit tools.

### Codex

Before starting Codex, authorize developer access in your terminal:

```sh
codex mcp login world-id-sandbox --scopes developer-portal:manage
```

Complete Google sign-in and portal consent, wait for the command to succeed,
then start a new Codex session. If you also want account and benefit tools,
request both scopes with `--scopes world-id:read,developer-portal:manage`;
that also requires sandbox World ID sign-in.

### Claude Code

Ask to register or configure your app. Follow the portal tool's authorization
challenge for `developer-portal:manage` and complete Google sign-in and consent.
If authentication is needed, use `/mcp` to select and authenticate the sandbox
World ID server, or exit Claude Code and run
`claude mcp login plugin:world-id-sandbox:world-id-sandbox`. World ID-only
authorization does not grant developer access.

### Register or configure an app

```text
Register my sandbox app with World ID. My callback URL is https://my-app.example/auth/world/callback.
Update my sandbox app's logo and callback URLs.
```

Use your actual HTTPS callback URL; sandbox does not accept HTTP localhost
callbacks. The agent gathers the remaining details and prepares registration.
Open its returned portal link to review and approve the request within 20
minutes. Save any generated client secret directly in your backend's secure
configuration; never paste it into chat. The agent checks completion and returns
your client ID and public configuration.

Registration does not publish a benefit listing. For that, open the app's
**Catalog** tab in the portal, save a listing, and submit it for review as the
app owner. An authorized reviewer outside the app's team must approve it before
it is published. Catalog submission is not currently exposed through MCP.
