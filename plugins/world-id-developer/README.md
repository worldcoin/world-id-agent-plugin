# World ID Developer

Read integration guides and register or configure apps with World ID. This plugin
connects to `https://sandbox.auth.world.org/mcp/developer` and uses sandbox data.
Portal tools require Google sign-in with `developer-portal:manage`. Reading guides
requires no sign-in. World ID verification is not required for developer access.

Install `world-id-developer-sandbox` from the `world-id-demo` marketplace. See the
[installation guide](https://github.com/worldcoin/world-id-agent-plugin#developer-plugin)
for Codex and Claude Code commands.

Approve registration and credential requests through the returned portal link.
Save secrets directly in backend configuration and keep them out of chat.

The separate World ID plugin provides account, benefit, and Orb tools. Install
both plugins if you need both kinds of access; their authorizations are separate.
