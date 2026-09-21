# World ID

A ChatGPT and Codex plugin that connects to the hosted World ID MCP server at
[auth.worldcoin.dev/mcp](https://auth.worldcoin.dev/mcp).

The plugin uses `get_benefits` to list approved, published apps that offer
World ID benefits. The tool returns each app's name, description, and URL.
It requires World ID sign-in and OAuth consent for the `mcp:read` scope.

Install the plugin from `plugins/world-id-benefits/`. Complete sign-in when
the host asks, then ask:

> Show me the benefits I can access with World ID.

The package has portable `plugin.json` and `mcp.json` files. The hidden
`.codex-plugin/plugin.json` and `.mcp.json` files support Codex hosts that use
that layout. Both MCP files use the same hosted endpoint.

This project contains the plugin package and its local marketplace entry.
It does not need a local server, Node.js dependencies, or deployment.

| Path | Purpose |
| --- | --- |
| `plugins/world-id-benefits/` | Plugin manifests, MCP configuration, and logo |
| `plugins/world-id-benefits/skills/` | World ID sign-in and benefit instructions |
| `.agents/plugins/marketplace.json` | Local marketplace entry |
