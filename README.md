# World ID

A plugin for AI agents that connects to the hosted World ID MCP server at
[auth.worldcoin.dev/mcp](https://auth.worldcoin.dev/mcp).

Connect your World ID, check your account with `get_world_id_account`, discover
published offers with `get_benefits`, and access World ID integration guidance.
Account checks and benefit discovery require World ID sign-in and OAuth consent
for the `mcp:read` scope. Public integration guides do not require sign-in.

Install the plugin from `plugins/world-id/`. Complete sign-in when
the host asks, then ask:

> Connect my World ID.
>
> What can I do with World ID?
>
> What benefits are available?

Benefit listings describe offers, not confirmed eligibility or redemption.
Partner services require their own authorization.

The package has portable `plugin.json` and `mcp.json` files. The hidden
`.codex-plugin/plugin.json` and `.mcp.json` files support Codex hosts that use
that layout. Both MCP files use the same hosted endpoint.

This project contains the plugin package and its local marketplace entry.
It does not need a local server, Node.js dependencies, or deployment.

| Path | Purpose |
| --- | --- |
| `plugins/world-id/` | Plugin manifests, MCP configuration, and logo |
| `plugins/world-id/skills/` | World ID sign-in and benefit instructions |
| `.agents/plugins/marketplace.json` | Local marketplace entry |
