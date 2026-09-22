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

## Getting started

You need Git, Python 3, and either the Codex CLI (`codex`) or Claude Code
(`claude`) installed and signed in. The examples below use **sandbox** for the
hackathon; staging alternatives are shown alongside them.

### 1. Download and build the plugins

In your terminal:

```sh
git clone https://github.com/worldcoin/world-id-agent-plugin.git
cd world-id-agent-plugin
```

If testing [PR #4](https://github.com/worldcoin/world-id-agent-plugin/pull/4)
before it is merged, select its branch before building:

```sh
git switch codex/world-id-sandbox-selection
```

Build the packages (Python standard library only; no dependencies to install):

```sh
python3 scripts/build-plugins.py
```

The current installation requires this clone-and-build step. Install from
`dist/`, not directly from the source folders or a Git marketplace URL.
Keep this terminal in the repository root for the commands below.

### 2. Set up your agent (choose one)

#### Codex

Add the built marketplace, install sandbox, and start a new session:

```sh
codex plugin marketplace add ./dist
codex plugin add world-id-sandbox@world-id-demo
codex
```

For **staging**, replace `world-id-sandbox@world-id-demo` with
`world-id@world-id-demo` in the install command. Install only one variant.
If `codex plugin` is unrecognized, update your Codex CLI before continuing.

#### Claude Code

Start a session with the sandbox plugin:

```sh
claude --plugin-dir ./dist/plugins/world-id-sandbox
```

For **staging**, replace `./dist/plugins/world-id-sandbox` with
`./dist/plugins/world-id`. This loads the plugin for this session; use the same
`--plugin-dir` option each time you launch Claude Code.

### 3. Connect your World ID and try it

Inside your agent, enter `/mcp` and check that the selected World ID connection
is listed. Complete World ID sign-in and consent when prompted. In Claude Code,
select the server in `/mcp` to authenticate. If Codex reports authentication is
required without opening a prompt, check its available connection controls;
retrying a benefit tool does not guarantee that a login window will open.

Then send these prompts, one at a time:

```text
Connect my World ID.
What benefits are available?
Help me use one of those benefits.
```

You should be able to check your linked account and discover benefits in the
selected environment. An empty catalog can mean no partner offers are published
there yet. Partner services may require their own sign-in; discovering a benefit
does not mean it has been claimed.

Account checks and benefit discovery require World ID sign-in and OAuth consent
for `mcp:read`. Public integration guides do not require sign-in.
Benefit listings describe offers, not confirmed eligibility or redemption.

## Switching environments

Enable only one World ID environment, including any manually added MCP servers.
Removing a plugin does not remove separately configured servers.

In Codex, exit the session and switch from staging to sandbox with:

```sh
codex plugin remove world-id@world-id-demo
codex plugin add world-id-sandbox@world-id-demo
codex
```

Reverse the names to switch back. In Claude Code, exit and relaunch with the other
`--plugin-dir` path. Disable any previously installed World ID plugin or manually
added server for the other environment first. Authenticate the new environment
as needed.

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

## Development

Edit skills in `skills/` and the logo in `assets/`. The two directories under
`plugins/` contain only environment-specific manifests and MCP configuration.
Both variants use exactly the same skills; the endpoint is set in each variant's
MCP configuration.

After editing, rebuild and check the packages:

```sh
python3 scripts/build-plugins.py
python3 scripts/build-plugins.py --check
```

`dist/` is generated and ignored by Git. Distribute the built marketplace or
plugin directories, including the bundled skills and assets. No local server is
required. Rebuild before reinstalling an updated plugin and start a new session.

Each package includes portable `plugin.json` and `mcp.json` files, Codex's
`.codex-plugin/plugin.json` and `.mcp.json`, and Claude Code's
`.claude-plugin/plugin.json`. Both MCP files within a package point to the same
environment. The build copies `.agents/plugins/marketplace.json` into `dist/`
to list both Codex plugins.

See the [Codex plugin documentation](https://developers.openai.com/plugins/build/plugins),
[Codex MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli),
and [Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference)
for host setup details.
