# World ID

Connect your World ID, discover partner benefits, and register or configure
apps with World ID sign-in from Codex or Claude Code.

**Production** uses real accounts and data. **Sandbox** is a separate environment
for testing, with its own accounts and app registrations. Use production by
default and sandbox when testing.

| Environment | Git branch | Plugin | Marketplace |
| --- | --- | --- | --- |
| Production | `main` | `world-id` | `world-id` |
| Sandbox | `sandbox` | `world-id-sandbox` | `world-id-demo` |

## Install

Give your coding agent this prompt:

```text
Install this plugin: https://github.com/worldcoin/world-id-agent-plugin
```

For sandbox, ask it to install from the `sandbox` branch instead.

You need Git and either Codex CLI (`codex`) or Claude Code (`claude`) installed
and signed in. **No Python, manual clone, build step or local server is needed.**
The release branches contain the complete plugin.

### Instructions for coding agents

Use the commands for the user's coding agent and requested environment below.
Default to production on `main`. If the user supplies a `dev` or feature-branch
URL, use that Git ref with the sandbox commands and plugin name. Follow the
sign-in steps after installation and have the user complete browser authorization.

### Codex

Production:

```sh
codex plugin marketplace add worldcoin/world-id-agent-plugin --ref main
codex plugin add world-id@world-id
```

Sandbox:

```sh
codex plugin marketplace add worldcoin/world-id-agent-plugin --ref sandbox
codex plugin add world-id-sandbox@world-id-demo
```

If `codex plugin` is unavailable, update Codex CLI before installing.

### Claude Code

Production:

```sh
claude plugin marketplace add https://github.com/worldcoin/world-id-agent-plugin.git#main
claude plugin install world-id@world-id
```

Sandbox:

```sh
claude plugin marketplace add https://github.com/worldcoin/world-id-agent-plugin.git#sandbox
claude plugin install world-id-sandbox@world-id-demo
```

## Sign in

Account and benefit tools require World ID verification in the selected
environment. Sandbox verification is separate from production. If you only need
app registration, go to [Developer access](#developer-access).

For **Codex**, exit any running session, then authorize the installed plugin:

```sh
codex mcp login world-id --scopes world-id:read
```

For sandbox, use `world-id-sandbox` in place of `world-id`.

For **Claude Code**, authorize the installed plugin:

```sh
claude mcp login plugin:world-id:world-id
```

For sandbox, use `plugin:world-id-sandbox:world-id-sandbox`. You can also run
`/mcp` inside Claude Code, select the matching World ID server, and authenticate.

Complete browser sign-in and wait for success. If the browser does not open,
follow the URL printed by the command. Start a new Codex or Claude Code session
after installation and sign-in. Each host manages its own authorization.

Try asking:

```text
Is my World ID connected?
What benefits are available?
```

Account replies report connection status only; they do not expose personal
account identifiers. Keep tokens and credentials out of chat.

## Developer access

App registration and configuration use Google developer-portal sign-in with the
`developer-portal:manage` scope. World ID verification is not required for these
operations.

For **Codex**, authorize developer access before starting a new session:

```sh
codex mcp login world-id --scopes developer-portal:manage
```

Use `world-id-sandbox` for sandbox. To also use account and benefit tools, request
both scopes with `--scopes world-id:read,developer-portal:manage` and complete
World ID sign-in as well.

For **Claude Code**, ask to register or configure an app and follow the tool's
Google sign-in and consent link. If needed, use `/mcp` to authenticate the
matching World ID server. Account-only authorization does not grant developer
access.

```text
Register my app with World ID. My callback URL is https://my-app.example/auth/world/callback.
Update my app's logo and callback URLs.
```

Use an HTTPS callback URL; HTTP localhost and wildcard callbacks are not
accepted. Review and approve registration through the returned portal link
within 20 minutes. Save any client secret directly in your backend's secure
configuration, never in chat.

To publish a benefit, open the app's **Catalog** tab in the portal and submit a
listing for review. Registration does not publish a listing automatically.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development, testing and releases.
